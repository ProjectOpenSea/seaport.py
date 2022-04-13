from collections import namedtuple
from functools import reduce
from itertools import chain
from secrets import token_hex

from brownie import ZERO_ADDRESS, Contract
from jsonschema import ValidationError
from consideration.constants import (
    ONE_HUNDRED_PERCENT_BP,
    ItemType,
    OrderType,
    ProxyStrategy,
)
from typing import Optional, Sequence, TypedDict, cast, Union
from consideration.types import (
    BalancesAndApprovals,
    BasicErc1155Item,
    BasicErc721Item,
    ConsiderationItem,
    CreateInputItem,
    CurrencyItem,
    Erc1155Item,
    Erc1155ItemWithCriteria,
    Erc721Item,
    Erc721ItemWithCriteria,
    Fee,
    InputCriteria,
    InsufficientApprovals,
    Item,
    OfferItem,
    Order,
    OrderParameters,
)
from web3.constants import ADDRESS_ZERO

from consideration.utils.balance_and_approval_check import (
    validate_offer_balances_and_approvals,
)
from consideration.utils.item import (
    TimeBasedItemParams,
    get_maximum_size_for_order,
    is_currency_item,
)


def get_order_type_from_options(
    allow_partial_fills: bool, restricted_by_zone: bool, use_proxy: bool
):
    if allow_partial_fills:
        if restricted_by_zone:
            return (
                OrderType.FULL_RESTRICTED_VIA_PROXY
                if use_proxy
                else OrderType.FULL_RESTRICTED
            )
        else:
            return OrderType.FULL_OPEN_VIA_PROXY if use_proxy else OrderType.FULL_OPEN
    else:
        if restricted_by_zone:
            return (
                OrderType.PARTIAL_RESTRICTED_VIA_PROXY
                if use_proxy
                else OrderType.PARTIAL_RESTRICTED
            )
        else:
            return (
                OrderType.PARTIAL_OPEN_VIA_PROXY
                if use_proxy
                else OrderType.PARTIAL_OPEN
            )


def multiply_basis_points(amount: int, basis_points: int) -> int:
    return amount * basis_points // ONE_HUNDRED_PERCENT_BP


def fee_to_consideration_item(
    fee: Fee, token: str, base_amount: int, base_end_amount: int
) -> ConsiderationItem:
    return ConsiderationItem(
        itemType=ItemType.NATIVE if token == ZERO_ADDRESS else ItemType.ERC20,
        token=token,
        identifierOrCriteria=0,
        startAmount=multiply_basis_points(base_amount, fee["basis_points"]),
        endAmount=multiply_basis_points(base_end_amount, fee["basis_points"]),
        recipient=fee["recipient"],
    )


def deduct_fees(items: Sequence[Item], fees: list[Fee] = []):
    total_basis_points = 0

    for fee in fees:
        total_basis_points += fee["basis_points"]

    return list(
        map(
            lambda item: item.copy(
                update={
                    "startAmount": item.startAmount
                    - multiply_basis_points(item.startAmount, total_basis_points)
                    if is_currency_item(item.itemType)
                    else item.startAmount,
                    "endAmount": item.endAmount
                    - multiply_basis_points(item.endAmount, total_basis_points)
                    if is_currency_item(item.itemType)
                    else item.endAmount,
                }
            ),
            items,
        )
    )


def map_input_item_to_offer_item(item: CreateInputItem) -> OfferItem:
    # Item is an NFT
    if "item_type" in item:
        # Convert this into a criteria based item
        if "identifiers" in item:
            item = cast(Union[Erc721ItemWithCriteria, Erc1155ItemWithCriteria], item)
            return OfferItem(
                itemType=ItemType.ERC721_WITH_CRITERIA
                if item["item_type"] == ItemType.ERC721
                else ItemType.ERC1155_WITH_CRITERIA,
                token=item["token"],
                identifierOrCriteria=0,
                startAmount=item.get("amount", 1),
                endAmount=item.get("endAmount", item.get("amount", 1)),
            )

        if "amount" in item or "end_amount" in item:
            item = cast(Union[BasicErc721Item, BasicErc1155Item], item)
            return OfferItem(
                itemType=item["item_type"],
                token=item["token"],
                identifierOrCriteria=item["identifier"],
                startAmount=item.get("amount", 1),
                endAmount=item.get("endAmount", item.get("amount", 1)),
            )

        return OfferItem(
            itemType=item["item_type"],
            token=item["token"],
            identifierOrCriteria=item["identifier"],
            startAmount=1,
            endAmount=1,
        )

    # Item is a currency
    item = cast(CurrencyItem, item)

    return OfferItem(
        itemType=ItemType.ERC20
        if "token" in item and item["token"] != ADDRESS_ZERO
        else ItemType.NATIVE,
        token=item["token"] or ADDRESS_ZERO,
        identifierOrCriteria=0,
        startAmount=item["amount"],
        endAmount=item.get("end_amount", item["amount"]),
    )


def are_all_currencies_same(
    offer: list[OfferItem], consideration: list[ConsiderationItem]
):
    all_items = list(chain(offer, consideration))
    currencies = list(filter(lambda item: is_currency_item(item.itemType), all_items))

    return all(
        map(
            lambda item: item.itemType == currencies[0].itemType
            and item.token == currencies[0].token,
            currencies,
        ),
    )


def validate_order_parameters(
    *,
    order_parameters: OrderParameters,
    offer_criteria: list[InputCriteria],
    balances_and_approvals: BalancesAndApprovals,
    throw_on_insufficient_balances=False,
    throw_on_insufficient_approvals=False,
    consideration_contract: Contract,
    proxy: str,
    proxy_strategy: ProxyStrategy,
    time_based_item_params: Optional[TimeBasedItemParams]
):
    if not are_all_currencies_same(
        offer=order_parameters.offer, consideration=order_parameters.consideration
    ):
        raise ValidationError("All currency tokens in the order must be the same token")

    return validate_offer_balances_and_approvals(
        offer=order_parameters.offer,
        order_type=order_parameters.orderType,
        criterias=offer_criteria,
        balances_and_approvals=balances_and_approvals,
        throw_on_insufficient_balances=throw_on_insufficient_balances,
        throw_on_insufficient_approvals=throw_on_insufficient_approvals,
        consideration_contract=consideration_contract,
        proxy=proxy,
        proxy_strategy=proxy_strategy,
        time_based_item_params=time_based_item_params,
    )


def total_items_amount(items: list[Item]):
    start_amount = 0
    end_amount = 0

    for item in items:
        start_amount += item.startAmount
        end_amount += item.endAmount

    return (start_amount, end_amount)


# Maps order offer and consideration item amounts based on the order's filled status
# After applying the fraction, we can view this order as the "canonical" order for which we
# check approvals and balances
def map_order_amounts_from_filled_status(
    order: Order, total_filled: int, total_size: int
):
    if total_filled == 0 or total_size == 0:
        return order

    # i.e if totalFilled is 3 and totalSize is 4, there are 1 / 4 order amounts left to fill.
    basis_points = (total_size - total_filled) * ONE_HUNDRED_PERCENT_BP // total_size

    return order.copy(
        update={
            "parameters": order.parameters.copy(
                update={
                    "offer": list(
                        map(
                            lambda item: item.copy(
                                update={
                                    "startAmount": multiply_basis_points(
                                        item.startAmount, basis_points
                                    ),
                                    "endAmount": multiply_basis_points(
                                        item.endAmount, basis_points
                                    ),
                                }
                            ),
                            order.parameters.offer,
                        )
                    ),
                    "consideration": list(
                        map(
                            lambda item: item.copy(
                                update={
                                    "startAmount": multiply_basis_points(
                                        item.startAmount, basis_points
                                    ),
                                    "endAmount": multiply_basis_points(
                                        item.endAmount, basis_points
                                    ),
                                }
                            ),
                            order.parameters.consideration,
                        )
                    ),
                }
            )
        }
    )


# Maps order offer and consideration item amounts based on the units needed to fulfill
# After applying the fraction, we can view this order as the "canonical" order for which we
# check approvals and balances
def map_order_amounts_from_units_to_fill(
    order: Order, units_to_fill: int, total_filled: int, total_size: int
):
    if units_to_fill <= 0:
        raise ValidationError("Units to fill must be greater than 1")

    max_units = get_maximum_size_for_order(order)

    if total_size == 0:
        total_size = max_units

    # This is the percentage of the order that is left to be fulfilled, and therefore we can't fill more than that.
    remaining_order_percentage_to_be_filled = (
        (total_size - total_filled) * ONE_HUNDRED_PERCENT_BP // total_size
    )

    # i.e if totalSize is 8 and unitsToFill is 3, then we multiply every amount by 3 / 8

    units_to_fill_basis_points = units_to_fill * ONE_HUNDRED_PERCENT_BP // max_units

    # We basically choose the lesser between the units requested to be filled and the actual remaining order amount left
    # This is so that if a user tries to fulfill an order that is 1/2 filled, and supplies a fraction such as 3/4, the maximum
    # amount to fulfill is 1/2 instead of 3/4
    basis_points = min(
        units_to_fill_basis_points, remaining_order_percentage_to_be_filled
    )

    return order.copy(
        update={
            "parameters": order.parameters.copy(
                update={
                    "offer": list(
                        map(
                            lambda item: item.copy(
                                update={
                                    "startAmount": multiply_basis_points(
                                        item.startAmount, basis_points
                                    ),
                                    "endAmount": multiply_basis_points(
                                        item.endAmount, basis_points
                                    ),
                                }
                            ),
                            order.parameters.offer,
                        )
                    ),
                    "consideration": list(
                        map(
                            lambda item: item.copy(
                                update={
                                    "startAmount": multiply_basis_points(
                                        item.startAmount, basis_points
                                    ),
                                    "endAmount": multiply_basis_points(
                                        item.endAmount, basis_points
                                    ),
                                }
                            ),
                            order.parameters.consideration,
                        )
                    ),
                }
            )
        }
    )


def generate_random_salt():
    return int(token_hex(32), 16)

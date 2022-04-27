from itertools import chain
from secrets import token_hex
from typing import Sequence

from web3.constants import ADDRESS_ZERO

from consideration.constants import ONE_HUNDRED_PERCENT_BP, ItemType
from consideration.types import (
    OfferErc721Item,
    OfferErc1155Item,
    ConsiderationItem,
    CreateInputItem,
    Fee,
    Item,
    OfferCurrencyItem,
    OfferErc721ItemWithCriteria,
    OfferErc1155ItemWithCriteria,
    OfferItem,
    Order,
)
from consideration.utils.item import get_maximum_size_for_order, is_currency_item
from consideration.utils.merkletree import MerkleTree


def multiply_basis_points(amount: int, basis_points: int) -> int:
    return amount * basis_points // ONE_HUNDRED_PERCENT_BP


def fee_to_consideration_item(
    *, fee: Fee, token: str, base_amount: int, base_end_amount: int
) -> ConsiderationItem:
    return ConsiderationItem(
        itemType=ItemType.NATIVE if token == ADDRESS_ZERO else ItemType.ERC20,
        token=token,
        identifierOrCriteria=0,
        startAmount=multiply_basis_points(base_amount, fee.basis_points),
        endAmount=multiply_basis_points(base_end_amount, fee.basis_points),
        recipient=fee.recipient,
    )


def deduct_fees(consideration: list[ConsiderationItem], fees: list[Fee] = []):
    total_basis_points = 0

    for fee in fees:
        total_basis_points += fee.basis_points

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
            consideration,
        )
    )


def map_input_item_to_offer_item(item: CreateInputItem) -> OfferItem:
    # Item is an NFT
    if not isinstance(item, OfferCurrencyItem):
        # Item is a criteria based item
        if isinstance(item, OfferErc721ItemWithCriteria) or isinstance(
            item, OfferErc1155ItemWithCriteria
        ):
            leaves = item.identifiers or []
            tree = MerkleTree(leaves)
            # Convert this into a criteria based item

            return OfferItem(
                itemType=item.item_type,
                token=item.token,
                identifierOrCriteria=int.from_bytes(tree.get_root(), "big"),
                startAmount=item.amount or 1,
                endAmount=item.end_amount or item.amount or 1,
            )
        elif isinstance(item, OfferErc721Item):
            return OfferItem(
                itemType=item.item_type,
                token=item.token,
                identifierOrCriteria=item.identifier,
                startAmount=1,
                endAmount=1,
            )
        elif isinstance(item, OfferErc1155Item):
            return OfferItem(
                itemType=item.item_type,
                token=item.token,
                identifierOrCriteria=item.identifier,
                startAmount=item.amount,
                endAmount=item.end_amount or item.amount or 1,
            )

    return OfferItem(
        itemType=ItemType.ERC20
        if item.token and item.token != ADDRESS_ZERO
        else ItemType.NATIVE,
        token=item.token or ADDRESS_ZERO,
        identifierOrCriteria=0,
        startAmount=item.amount,
        endAmount=item.end_amount or item.amount,
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


def total_items_amount(items: Sequence[Item]):
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
    *, order: Order, total_filled: int, total_size: int
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


def map_order_amounts_from_units_to_fill(
    *, order: Order, units_to_fill: int, total_filled: int, total_size: int
):
    """
    Maps order offer and consideration item amounts based on the units needed to fulfill
    After applying the fraction, we can view this order as the "canonical" order for which we
    check approvals and balances

    Args:
        order (Order): order struct
        units_to_fill (int): how many units to fill, which must divide the order cleanly
        total_filled (int): how much the order has already been filled
        total_size (int): the maximum size of the order

    Raises:
        ValueError: when supplied an invalid units to fill value

    Returns:
        _type_: the order with adjusted amounts based on units to fill
    """
    if units_to_fill <= 0:
        raise ValueError("Units to fill must be greater than 1")

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

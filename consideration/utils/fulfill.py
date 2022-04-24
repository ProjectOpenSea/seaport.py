from itertools import chain
from typing import cast

from brownie import Wei
from hexbytes import HexBytes
from web3 import Web3
from web3.constants import ADDRESS_ZERO
from web3.contract import Contract
from web3.types import TxParams

from consideration.constants import (
    LEGACY_PROXY_CONDUIT,
    NO_CONDUIT,
    BasicOrderRouteType,
    ItemType,
    ProxyStrategy,
)
from consideration.types import (
    BalancesAndApprovals,
    ConsiderationItem,
    ExchangeAction,
    FulfillOrderUseCase,
    InputCriteria,
    Order,
    OrderParameters,
    OrderStatus,
)
from consideration.utils.balance_and_approval_check import (
    get_approval_actions,
    use_proxy_from_approvals,
    validate_basic_fulfill_balances_and_approvals,
    validate_standard_fulfill_balances_and_approvals,
)
from consideration.utils.gcd import gcd
from consideration.utils.item import (
    TimeBasedItemParams,
    generate_criteria_resolvers,
    get_maximum_size_for_order,
    get_summed_token_and_identifier_amounts,
    is_criteria_item,
    is_currency_item,
    is_native_currency_item,
)
from consideration.utils.order import (
    are_all_currencies_same,
    map_order_amounts_from_filled_status,
    map_order_amounts_from_units_to_fill,
    total_items_amount,
)
from consideration.utils.pydantic import parse_model_list
from consideration.utils.usecase import execute_all_actions, get_transaction_methods


def should_use_basic_fulfill(
    order_parameters: OrderParameters, total_filled: int
) -> bool:
    """
    We should use basic fulfill order if the order adheres to the following criteria:
    1. The order should not be partially filled.
    2. The order only contains a single offer item and contains at least one consideration item
    3. The order does not offer an item with Ether (or other native tokens) as its item type.
    4. The order only contains a single ERC721 or ERC1155 item and that item is not criteria-based
    5. All other items have the same Native or ERC20 item type and token
    6. All items have the same startAmount and endAmount
    7. First consideration item must contain the offerer as the recipient
    8. If the order has multiple consideration items and all consideration items other than the
       first consideration item have the same item type as the offered item, the offered item
       amount is not less than the sum of all consideration item amounts excluding the
       first consideration item amount
    9. The token on native currency items needs to be set to the null address and the identifier on
       currencies needs to be zero, and the amounts on the 721 item need to be 1

    Args:
        order_parameters (OrderParameters): order parameters struct
        total_filled (int): the total filled amount of the order

    Returns:
        bool: whether we should use basic fulfill or not
    """
    # 1. The order must not be partially filled
    if total_filled != 0:
        return False

    # 2. Must be single offer and at least one consideration item
    if len(order_parameters.offer) > 1 or len(order_parameters.consideration) == 0:
        return False

    all_items = list(chain(order_parameters.offer, order_parameters.consideration))

    nfts = list(
        filter(
            lambda item: item.itemType
            in [ItemType.ERC721.value, ItemType.ERC1155.value],
            all_items,
        )
    )

    nfts_with_criteria = list(
        filter(
            lambda item: is_criteria_item(item.itemType),
            all_items,
        )
    )

    # 3. The order does not offer an item with Ether (or other native tokens) as its item type
    offers_native_currency = is_native_currency_item(order_parameters.offer[0].itemType)

    if offers_native_currency:
        return False

    # 4. The order only contains a single ERC721 or ERC1155 item and that item is not criteria-based
    if len(nfts) != 1 or len(nfts_with_criteria) != 0:
        return False

    # 5. All currencies need to have the same address and item type (Native, ERC20)
    if not are_all_currencies_same(
        offer=order_parameters.offer, consideration=order_parameters.consideration
    ):
        return False

    # 6. All individual items need to have the same startAmount and endAmount
    different_start_and_end_amount = any(
        item.startAmount != item.endAmount for item in all_items
    )

    if different_start_and_end_amount:
        return False

    first_consideration, *rest_consideration = order_parameters.consideration

    # 7. First consideration item must contain the offerer as the recipient
    first_consideration_recipient_is_not_offerer = (
        first_consideration.recipient.lower() != order_parameters.offerer.lower()
    )

    # 8. If the order has multiple consideration items and all consideration items other than the
    # first consideration item have the same item type as the offered item, the offered item
    # amount is not less than the sum of all consideration item amounts excluding the
    # first consideration item amount
    if (
        len(order_parameters.consideration) > 1
        and all(
            item.itemType == order_parameters.offer[0].itemType
            for item in rest_consideration
        )
        and total_items_amount(rest_consideration)[1]
        > order_parameters.offer[0].endAmount
    ):
        return False

    currencies = list(filter(lambda item: is_currency_item(item.itemType), all_items))

    # 9. The token on native currency items needs to be set to the null address and the identifier on
    # currencies needs to be zero, and the amounts on the 721 item need to be 1
    native_currency_is_zero_address = all(
        item.token == ADDRESS_ZERO
        for item in filter(
            lambda item: item.itemType == ItemType.NATIVE.value, currencies
        )
    )

    currency_identifiers_are_zero = all(
        item.identifierOrCriteria == 0 for item in currencies
    )

    erc_721s_are_single_amount = all(
        item.endAmount
        for item in filter(lambda item: item.itemType == ItemType.ERC721.value, nfts)
    )

    return (
        native_currency_is_zero_address
        and currency_identifiers_are_zero
        and erc_721s_are_single_amount
    )


offer_and_consideration_fulfillment_mapping = {
    ItemType.ERC20: {
        ItemType.ERC721: BasicOrderRouteType.ERC721_TO_ERC20,
        ItemType.ERC1155: BasicOrderRouteType.ERC1155_TO_ERC20,
    },
    ItemType.ERC721: {
        ItemType.NATIVE: BasicOrderRouteType.ETH_TO_ERC721,
        ItemType.ERC20: BasicOrderRouteType.ERC20_TO_ERC721,
    },
    ItemType.ERC1155: {
        ItemType.NATIVE: BasicOrderRouteType.ETH_TO_ERC1155,
        ItemType.ERC20: BasicOrderRouteType.ERC20_TO_ERC1155,
    },
}


def get_basic_order_route_type(
    offer_item_type: ItemType, consideration_item_type: ItemType
):
    if offer_item_type == ItemType.ERC20.value:
        if consideration_item_type == ItemType.ERC721.value:
            return BasicOrderRouteType.ERC721_TO_ERC20
        elif consideration_item_type == ItemType.ERC1155.value:
            return BasicOrderRouteType.ERC1155_TO_ERC20

    if offer_item_type == ItemType.ERC721.value:
        if consideration_item_type == ItemType.NATIVE.value:
            return BasicOrderRouteType.ETH_TO_ERC721
        elif consideration_item_type == ItemType.ERC20.value:
            return BasicOrderRouteType.ERC20_TO_ERC721

    if offer_item_type == ItemType.ERC1155.value:
        if consideration_item_type == ItemType.NATIVE.value:
            return BasicOrderRouteType.ETH_TO_ERC1155
        elif consideration_item_type == ItemType.ERC20.value:
            return BasicOrderRouteType.ERC20_TO_ERC1155


def fulfill_basic_order(
    order: Order,
    consideration_contract: Contract,
    offerer_balances_and_approvals: BalancesAndApprovals,
    fulfiller_balances_and_approvals: BalancesAndApprovals,
    time_based_item_params: TimeBasedItemParams,
    fulfiller: str,
    offerer_proxy: str,
    fulfiller_proxy: str,
    proxy_strategy: ProxyStrategy,
    tips: list[ConsiderationItem],
    web3: Web3,
):
    consideration_including_tips = list(chain(order.parameters.consideration, tips))
    offer_item = order.parameters.offer[0]
    for_offerer, *for_additional_recipients = consideration_including_tips

    basic_order_route_type = get_basic_order_route_type(
        offer_item_type=offer_item.itemType,
        consideration_item_type=for_offerer.itemType,
    )

    if not basic_order_route_type:
        raise Exception("Order parameters did not result in a valid basic fulfillment")

    additional_recipients = list(
        map(
            lambda item: {"amount": item.startAmount, "recipient": item.recipient},
            for_additional_recipients,
        )
    )

    consideration_without_offer_item_type = list(
        filter(
            lambda item: item.itemType != order.parameters.offer[0].itemType,
            consideration_including_tips,
        )
    )

    total_native_amount = (
        get_summed_token_and_identifier_amounts(
            items=consideration_without_offer_item_type,
            criterias=[],
            time_based_item_params=time_based_item_params.copy(
                update={"is_consideration_item": True}
            ),
        )
        .get(ADDRESS_ZERO, {})
        .get(0, 0)
    )

    insufficient_approvals = validate_basic_fulfill_balances_and_approvals(
        offer=order.parameters.offer,
        conduit=order.parameters.conduit,
        consideration=consideration_including_tips,
        offerer_balances_and_approvals=offerer_balances_and_approvals,
        fulfiller_balances_and_approvals=fulfiller_balances_and_approvals,
        time_based_item_params=time_based_item_params,
        consideration_contract=consideration_contract,
        offerer_proxy=offerer_proxy,
        fulfiller_proxy=fulfiller_proxy,
        proxy_strategy=proxy_strategy,
    )

    use_fulfiller_proxy = use_proxy_from_approvals(
        insufficient_owner_approvals=insufficient_approvals.insufficient_owner_approvals,
        insufficient_proxy_approvals=insufficient_approvals.insufficient_proxy_approvals,
        proxy_strategy=proxy_strategy,
    )

    approvals_to_use = (
        insufficient_approvals.insufficient_proxy_approvals
        if use_fulfiller_proxy
        else insufficient_approvals.insufficient_owner_approvals
    )

    basic_order_parameters = {
        "offerer": order.parameters.offerer,
        "offererConduit": order.parameters.conduit,
        "zone": order.parameters.zone,
        # Note the use of a "basicOrderType" enum;
        # this represents both the usual order type as well as the "route"
        # of the basic order (a simple derivation function for the basic order
        # type is `basicOrderType = orderType + (4 * basicOrderRoute)`.)
        "basicOrderType": order.parameters.orderType + 4 * basic_order_route_type.value,  # type: ignore
        "offerToken": offer_item.token,
        "offerIdentifier": offer_item.identifierOrCriteria,
        "offerAmount": offer_item.endAmount,
        "considerationToken": for_offerer.token,
        "considerationIdentifier": for_offerer.identifierOrCriteria,
        "considerationAmount": for_offerer.endAmount,
        "startTime": order.parameters.startTime,
        "endTime": order.parameters.endTime,
        "salt": order.parameters.salt,
        "totalOriginalAdditionalRecipients": len(order.parameters.consideration) - 1,
        "signature": order.signature,
        "fulfillerConduit": LEGACY_PROXY_CONDUIT if use_fulfiller_proxy else NO_CONDUIT,
        "additionalRecipients": additional_recipients,
        "zoneHash": order.parameters.zoneHash,
    }

    payable_overrides: TxParams = {"value": Wei(total_native_amount), "from": fulfiller}
    approval_actions = get_approval_actions(
        insufficient_approvals=approvals_to_use,
        web3=web3,
        account_address=fulfiller,
    )
    exchange_action = ExchangeAction(
        transaction_methods=get_transaction_methods(
            consideration_contract.functions.fulfillBasicOrder(basic_order_parameters),
            payable_overrides,
        ),
    )

    actions = list(chain(approval_actions, [exchange_action]))

    return FulfillOrderUseCase(
        actions=actions,
        execute_all_actions=lambda: cast(HexBytes, execute_all_actions(actions)),
    )


def fulfill_standard_order(
    *,
    order: Order,
    units_to_fill: int = 0,
    total_size: int,
    total_filled: int,
    offer_criteria: list[InputCriteria],
    consideration_criteria: list[InputCriteria],
    tips: list[ConsiderationItem],
    extra_data: str = "0x",
    consideration_contract: Contract,
    offerer_balances_and_approvals: BalancesAndApprovals,
    fulfiller_balances_and_approvals: BalancesAndApprovals,
    time_based_item_params: TimeBasedItemParams,
    offerer_proxy: str,
    fulfiller_proxy: str,
    proxy_strategy: ProxyStrategy,
    fulfiller: str,
    web3: Web3
):

    # If we are supplying units to fill, we adjust the order by the minimum of the amount to fill and
    # the remaining order left to be fulfilled
    order_with_adjusted_fills = (
        map_order_amounts_from_units_to_fill(
            order=order,
            units_to_fill=units_to_fill,
            total_filled=total_filled,
            total_size=total_size,
        )
        if units_to_fill
        # Else, we adjust the order by the remaining order left to be fulfilled
        else map_order_amounts_from_filled_status(
            order=order, total_filled=total_filled, total_size=total_size
        )
    )

    offer = order_with_adjusted_fills.parameters.offer
    consideration = order_with_adjusted_fills.parameters.consideration
    conduit = order_with_adjusted_fills.parameters.conduit

    consideration_including_tips = list(chain(consideration, tips))

    total_native_amount = total_native_amount = (
        get_summed_token_and_identifier_amounts(
            items=consideration_including_tips,
            criterias=consideration_criteria,
            time_based_item_params=time_based_item_params.copy(
                update={"is_consideration_item": True}
            ),
        )
        .get(ADDRESS_ZERO, {})
        .get(0, 0)
    )

    offer_criteria_items = list(
        filter(lambda item: is_criteria_item(item.itemType), offer)
    )

    consideration_criteria_items = list(
        filter(
            lambda item: is_criteria_item(item.itemType), consideration_including_tips
        )
    )

    if len(offer_criteria_items) != len(offer_criteria) or len(
        consideration_criteria_items
    ) != len(consideration_criteria):
        raise Exception(
            "You must supply the appropriate criterias for criteria based items"
        )

    insufficient_approvals = validate_standard_fulfill_balances_and_approvals(
        offer=offer,
        conduit=conduit,
        consideration=consideration_including_tips,
        offer_criteria=offer_criteria,
        consideration_criteria=consideration_criteria,
        offerer_balances_and_approvals=offerer_balances_and_approvals,
        fulfiller_balances_and_approvals=fulfiller_balances_and_approvals,
        time_based_item_params=time_based_item_params,
        consideration_contract=consideration_contract,
        offerer_proxy=offerer_proxy,
        fulfiller_proxy=fulfiller_proxy,
        proxy_strategy=proxy_strategy,
    )

    use_proxy_for_fulfiller = use_proxy_from_approvals(
        insufficient_owner_approvals=insufficient_approvals.insufficient_owner_approvals,
        insufficient_proxy_approvals=insufficient_approvals.insufficient_proxy_approvals,
        proxy_strategy=proxy_strategy,
    )

    approvals_to_use = (
        insufficient_approvals.insufficient_proxy_approvals
        if use_proxy_for_fulfiller
        else insufficient_approvals.insufficient_owner_approvals
    )

    has_criteria_items = offer_criteria_items or consideration_criteria_items

    approval_actions = get_approval_actions(
        insufficient_approvals=approvals_to_use, web3=web3, account_address=fulfiller
    )

    use_advanced = bool(units_to_fill) or has_criteria_items

    # Used for advanced order cases
    max_units = get_maximum_size_for_order(order)

    # Reduce the numerator/denominator as optimization
    units_gcd = gcd(units_to_fill, max_units)

    numerator = units_to_fill // units_gcd if units_to_fill else 1
    denominator = max_units // units_gcd if units_to_fill else 1

    order_accounting_for_tips = order.copy(
        update={
            "parameters": order.parameters.copy(
                update={
                    "consideration": list(chain(order.parameters.consideration, tips)),
                    "totalOriginalConsiderationItems": len(consideration),
                }
            )
        }
    )

    fulfiller_conduit = LEGACY_PROXY_CONDUIT if use_proxy_for_fulfiller else NO_CONDUIT

    payable_overrides: TxParams = {
        "value": Wei(total_native_amount),
        "from": fulfiller,
    }

    exchange_action = ExchangeAction(
        transaction_methods=get_transaction_methods(
            consideration_contract.functions.fulfillAdvancedOrder(
                {
                    **order_accounting_for_tips.dict(),
                    "numerator": numerator,
                    "denominator": denominator,
                    "extraData": extra_data,
                },
                parse_model_list(
                    generate_criteria_resolvers(
                        orders=[order],
                        offer_criterias=[offer_criteria],
                        consideration_criterias=[consideration_criteria],
                    )
                )
                if has_criteria_items
                else [],
                fulfiller_conduit,
            ),
            payable_overrides,
        )
        if use_advanced
        else get_transaction_methods(
            consideration_contract.functions.fulfillOrder(
                order_accounting_for_tips.dict(), fulfiller_conduit
            ),
            payable_overrides,
        )
    )

    actions = list(chain(approval_actions, [exchange_action]))

    return FulfillOrderUseCase(
        actions=actions,
        execute_all_actions=lambda: cast(HexBytes, execute_all_actions(actions)),
    )


def validate_and_sanitize_from_order_status(
    order: Order, order_status: OrderStatus
) -> Order:
    if (
        order_status.total_size > 0
        and order_status.total_filled // order_status.total_size == 1
    ):
        raise Exception("The order you are trying to fulfill is already filled")

    if order_status.is_cancelled:
        raise Exception("The order you are trying to fulfill is cancelled")

    if order_status.is_validated:
        # If the order is already validated, manually wipe the signature off of the order to save gas
        return Order(parameters=order.parameters, signature="0x")

    return order

from collections import deque
from itertools import chain
from typing import Optional, Sequence

from consideration.constants import ItemType
from consideration.types import InputCriteria, Item, Order
from consideration.utils.gcd import find_gcd

from pydantic import BaseModel


def is_currency_item(item_type: ItemType):
    return item_type in [ItemType.NATIVE, ItemType.ERC20]


def is_native_currency_item(item_type: ItemType):
    return item_type == ItemType.NATIVE


def is_erc20_item(item_type: ItemType):
    return item_type == ItemType.ERC20


def is_erc721_item(item_type: ItemType):
    return item_type in [ItemType.ERC721, ItemType.ERC721_WITH_CRITERIA]


def is_erc1155_item(item_type: ItemType):
    return item_type in [ItemType.ERC1155, ItemType.ERC1155_WITH_CRITERIA]


def is_criteria_item(item_type: ItemType):
    return item_type in [ItemType.ERC721_WITH_CRITERIA, ItemType.ERC1155_WITH_CRITERIA]


class TimeBasedItemParams(BaseModel):
    is_consideration_item: Optional[bool]
    current_block_timestamp: int
    ascending_amount_timestamp_buffer: int
    start_time: int
    end_time: int


def get_present_item_amount(
    start_amount: int,
    end_amount: int,
    time_based_item_params: Optional[TimeBasedItemParams],
) -> int:
    if not time_based_item_params:
        return max(start_amount, end_amount)

    duration = time_based_item_params.end_time - time_based_item_params.start_time

    is_ascending = end_amount > start_amount

    adjusted_block_timestamp = (
        time_based_item_params.current_block_timestamp
        + time_based_item_params.ascending_amount_timestamp_buffer
        if is_ascending
        else time_based_item_params.current_block_timestamp
    )

    if adjusted_block_timestamp < time_based_item_params.start_time:
        return start_amount

    elapsed = (
        max(adjusted_block_timestamp, time_based_item_params.end_time)
        - time_based_item_params.start_time
    )

    remaining = duration - elapsed

    # Adjust amounts based on current time
    # For offer items, we round down
    # For consideration items, we round up
    return (
        (start_amount * remaining)
        + (end_amount * elapsed)
        + ((duration - 1) if time_based_item_params.is_consideration_item else 0)
    ) // duration


TokenAndIdentifierAmounts = dict[str, dict[int, int]]


def get_summed_token_and_identifier_amounts(
    *,
    items: Sequence[Item],
    criterias: list[InputCriteria],
    time_based_item_params: Optional[TimeBasedItemParams] = None,
) -> TokenAndIdentifierAmounts:
    item_index_to_criteria = get_item_index_to_criteria_map(
        items=items, criterias=criterias
    )
    token_and_identifier_to_summed_amount: TokenAndIdentifierAmounts = {}

    for index, item in enumerate(items):
        identifier_or_criteria = (
            item_index_to_criteria[index].identifier
            if index in item_index_to_criteria
            else item.identifierOrCriteria
        )

        if item.token not in token_and_identifier_to_summed_amount:
            token_and_identifier_to_summed_amount[item.token] = {}

        if (
            identifier_or_criteria
            not in token_and_identifier_to_summed_amount[item.token]
        ):
            token_and_identifier_to_summed_amount[item.token][
                identifier_or_criteria
            ] = 0

        token_and_identifier_to_summed_amount[item.token][
            identifier_or_criteria
        ] += get_present_item_amount(
            start_amount=item.startAmount,
            end_amount=item.endAmount,
            time_based_item_params=time_based_item_params,
        )

    return token_and_identifier_to_summed_amount


#  Returns the maximum size of units possible for the order
#  If any of the items on a partially fillable order specify a different "startAmount" and "endAmount
#  (e.g. they are ascending-amount or descending-amount items), the fraction will be applied to both amounts
#  prior to determining the current price. This ensures that cleanly divisible amounts can be chosen when
#  constructing the order without a dependency on the time when the order is ultimately fulfilled.
def get_maximum_size_for_order(order: Order):
    all_items = list(chain(order.parameters.offer, order.parameters.consideration))

    amounts = list(
        chain.from_iterable(
            list(map(lambda x: (x.startAmount, x.endAmount), all_items))
        )
    )

    return find_gcd(amounts)


def get_item_index_to_criteria_map(
    items: Sequence[Item], criterias: list[InputCriteria]
):
    criterias_copy = deque(criterias)
    criteria_map: dict[int, InputCriteria] = {}
    for index, item in enumerate(items):
        if is_criteria_item(item.itemType):
            criteria_map[index] = criterias_copy.popleft()

    return criteria_map

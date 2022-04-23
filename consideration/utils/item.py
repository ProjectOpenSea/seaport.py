from collections import deque
from itertools import chain
from typing import Literal, Optional, Sequence, Union

from pydantic import BaseModel

from consideration.constants import ItemType, Side
from consideration.types import (
    ConsiderationItem,
    CriteriaResolver,
    InputCriteria,
    Item,
    OfferItem,
    Order,
)
from consideration.utils.gcd import find_gcd
from consideration.utils.merkletree import MerkleTree


def is_currency_item(item_type: ItemType):
    return item_type in [ItemType.NATIVE.value, ItemType.ERC20.value]


def is_native_currency_item(item_type: ItemType):
    return item_type == ItemType.NATIVE.value


def is_erc20_item(item_type: ItemType):
    return item_type == ItemType.ERC20.value


def is_erc721_item(item_type: ItemType):
    return item_type in [ItemType.ERC721.value, ItemType.ERC721_WITH_CRITERIA.value]


def is_erc1155_item(item_type: ItemType):
    return item_type in [ItemType.ERC1155.value, ItemType.ERC1155_WITH_CRITERIA.value]


def is_criteria_item(item_type: ItemType):
    return item_type in [
        ItemType.ERC721_WITH_CRITERIA.value,
        ItemType.ERC1155_WITH_CRITERIA.value,
    ]


class TimeBasedItemParams(BaseModel):
    is_consideration_item: Optional[bool] = None
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


def generate_criteria_resolvers(
    orders: list[Order],
    offer_criterias: list[list[InputCriteria]] = [[]],
    consideration_criterias: list[list[InputCriteria]] = [[]],
) -> list[CriteriaResolver]:
    offer_criteria_items: list[tuple[int, OfferItem, int, Literal[Side.OFFER]]] = []
    consideration_criteria_items: list[
        tuple[int, ConsiderationItem, int, Literal[Side.CONSIDERATION]]
    ] = []

    for order_index, order in enumerate(orders):
        for index, item in enumerate(
            filter(lambda item: is_criteria_item(item.itemType), order.parameters.offer)
        ):
            offer_criteria_items.append((order_index, item, index, Side.OFFER))

    for order_index, order in enumerate(orders):
        for index, item in enumerate(
            filter(
                lambda item: is_criteria_item(item.itemType),
                order.parameters.consideration,
            )
        ):
            consideration_criteria_items.append(
                (order_index, item, index, Side.CONSIDERATION)
            )

    def map_criteria_items_to_resolver(
        criteria_items: Union[
            list[tuple[int, OfferItem, int, Literal[Side.OFFER]]],
            list[tuple[int, ConsiderationItem, int, Literal[Side.CONSIDERATION]]],
        ],
        criterias: list[list[InputCriteria]],
    ):
        criteria_resolvers: list[CriteriaResolver] = []

        for i, (order_index, item, index, side) in enumerate(criteria_items):
            merkle_root = item.identifierOrCriteria or 0
            input_criteria = criterias[order_index][i]
            tree = MerkleTree(input_criteria.valid_identifiers or [])
            criteria_proof = tree.get_proof(input_criteria.identifier)

            criteria_resolvers.append(
                CriteriaResolver(
                    order_index=order_index,
                    side=side,
                    index=index,
                    identifier=input_criteria.identifier,
                    criteria_proof=[] if merkle_root == 0 else criteria_proof,
                )
            )

        return criteria_resolvers

    criteria_resolvers = map_criteria_items_to_resolver(
        offer_criteria_items, offer_criterias
    ) + map_criteria_items_to_resolver(
        consideration_criteria_items, consideration_criterias
    )

    return criteria_resolvers


def get_item_index_to_criteria_map(
    items: Sequence[Item], criterias: list[InputCriteria]
):
    criterias_copy = deque(criterias)
    criteria_map: dict[int, InputCriteria] = {}
    for index, item in enumerate(items):
        if is_criteria_item(item.itemType):
            criteria_map[index] = criterias_copy.popleft()

    return criteria_map


def hash_identifier(identifier: int):
    return hex(identifier)[2:].zfill(64)

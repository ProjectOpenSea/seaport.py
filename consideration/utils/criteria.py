from collections import deque
from functools import reduce
from typing import Sequence
from consideration.types import InputCriteria, Item
from consideration.utils.item import is_criteria_item


def get_item_index_to_criteria_map(
    items: Sequence[Item], criterias: list[InputCriteria]
):
    criterias_copy = deque(criterias)
    criteria_map: dict[int, InputCriteria] = {}
    for index, item in enumerate(items):
        if is_criteria_item(item.itemType):
            criteria_map[index] = criterias_copy.popleft()

    return criteria_map

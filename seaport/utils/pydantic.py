from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Sequence, Union, cast

from pydantic import BaseModel
from pydantic.utils import deep_update

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


class BaseModelWithEnumValues(BaseModel):
    """
    Using this helper model class as the built-in pydantic use_enum_values breaks type guarantees
    when accessing enums on the model directly

    Args:
        BaseModel (_type_): _description_
    """

    def dict(self, *args, **kwargs) -> "DictStrAny":
        resolved_dict = super().dict(**kwargs)

        return with_enum_values(resolved_dict)


def with_enum_values(element):
    if isinstance(element, dict):
        return {k: with_enum_values(v) for k, v in element.items()}
    elif isinstance(element, list):
        return [with_enum_values(el) for el in element]
    elif isinstance(element, Enum):
        return element.value
    return element


def parse_model_list(models: Sequence[BaseModel]):
    return list(map(lambda x: x.dict(), models))


def with_int_to_str(element: Any):
    if isinstance(element, dict):
        return {k: with_int_to_str(v) for k, v in element.items()}
    elif isinstance(element, list):
        return [with_int_to_str(el) for el in element]
    elif isinstance(element, int):
        return str(element)
    return element


def dict_int_to_str(d: dict):
    return {key: str(val) if isinstance(val, int) else val for key, val in d.items()}

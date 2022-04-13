from typing import Any, Sequence, Union

from pydantic import BaseModel


class BaseModelWithEnumValues(BaseModel):
    class Config:
        use_enum_values = True


def parse_model_list(models: Sequence[BaseModel]):
    return list(map(lambda x: x.dict(), models))


def to_struct(dict_or_list: Union[dict, list]):
    return tuple(
        [
            to_struct(x) if isinstance(x, dict) or isinstance(x, list) else x
            for x in (
                isinstance(dict_or_list, dict) and dict_or_list.values() or dict_or_list
            )
        ]
    )


def dict_int_to_str(d: dict):
    return {key: str(val) if isinstance(val, int) else val for key, val in d.items()}

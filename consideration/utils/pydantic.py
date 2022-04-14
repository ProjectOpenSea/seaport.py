from typing import Sequence

from pydantic import BaseModel


class BaseModelWithEnumValues(BaseModel):
    class Config:
        use_enum_values = True


def parse_model_list(models: Sequence[BaseModel]):
    return list(map(lambda x: x.dict(), models))


def dict_int_to_str(d: dict):
    return {key: str(val) if isinstance(val, int) else val for key, val in d.items()}

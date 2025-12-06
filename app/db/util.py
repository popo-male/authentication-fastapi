from enum import Enum as PyEnum
from typing import List, Type


def get_enum_values(enum_class: Type[PyEnum]) -> List[str]:
    """Callable for SQLAlchemy Enum's `values_callable` parameter."""
    return [e.value for e in enum_class]

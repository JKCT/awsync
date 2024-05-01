from enum import Enum


class StrEnum(str, Enum):
    "A backwards compatible StrEnum (introduced python 3.11) for python 3.8 support."

    def __str__(self) -> str:
        return str(self.value)

    def _generate_next_value_(name, *_) -> str:  # type: ignore
        return name

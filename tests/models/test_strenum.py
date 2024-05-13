"Test custom StrEnum class."
from awsync.models.strenum import StrEnum


class TestStrEnum:
    "Test StrEnum class."

    def test_str(self) -> None:
        "Test __str__ method."

        class TestEnum(StrEnum):
            one = "ONE"
            two = "TWO"

        assert str(TestEnum.one) == "ONE"
        assert str(TestEnum.two) == "TWO"

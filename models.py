from enum import Enum


class Period:
    def __init__(
            self,
            current: float | None = None,
            day: float | None = None,
            week: float | None = None,
            month: float | None = None,
            month_three: float | None = None,
            month_six: float | None = None,
            year: float | None = None,
            all_time: float | None = None
    ):
        self.current = current
        self.day = day
        self.week = week
        self.month = month
        self.month_three = month_three
        self.month_six = month_six
        self.year = year
        self.all_time = all_time


class Source:
    def __init__(self, lending: str, chain: str, name: str, url: str):
        self.lending = lending
        self.chain = chain
        self.name = name
        self.url = url
        self.period = Period()


class Pair:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class MorphoCheckboxCoordinates:
    week = Pair(430, 500)
    month = Pair(430, 470)
    month_three = Pair(430, 440)
    all_time = Pair(430, 410)


class FluidPeriodsBtnCoordinates:
    day = Pair(885, 197)
    week = Pair(920, 197)
    month = Pair(955, 197)
    year = Pair(990, 197)


class LendingToSearch(Enum):
    AAVE = 1
    FLUID = 2
    COMPOUND = 3
    MORPHO = 4
    ALL = 5


class Mode(Enum):
    SYNC = 1
    ASYNC = 2

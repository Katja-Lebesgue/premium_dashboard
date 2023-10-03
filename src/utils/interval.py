from enum import Enum
from numbers import Number

# TODO: finish normalisation implementation


class Border(str, Enum):
    open = "open"
    closed = "closed"


border_to_str = {
    "left": {Border.open: "<", Border.closed: "["},
    "right": {Border.open: ">", Border.closed: "]"},
}


class MyInterval:
    def __init__(
        self,
        left: Number,
        right: Number,
        left_border: Border = Border.closed,
        right_border: Border = Border.closed,
    ):
        self.left = left
        self.right = right
        self.left_border = left_border
        self.right_border = right_border

    @property
    def length(self):
        return max(self.right - self.left, 0)

    @property
    def mid(self):
        return (self.left + self.right) / 2

    @property
    def is_empty(self):
        return self.length == 0

    def __contains__(self, elem: Number) -> bool:
        if self.left_border == Border.open:
            left_cond = self.left < elem
        else:
            left_cond = self.left <= elem

        if self.right_border == Border.open:
            right_cond = self.right > elem
        else:
            right_cond = self.right >= elem
        return left_cond and right_cond

    def overlaps(self, other):
        if self.right < other.left or self.left > other.right:
            return False
        if self.right == other.left:
            return any([border == Border.closed for border in (self.right, other.left)])
        if self.left == other.right:
            return any([border == Border.closed for border in (self.lefrightther.right)])
        return True

    def __and__(self, other):
        left = max(self.left, other.left)

        left_borders = [interval_.left_border for interval_ in (self, other) if interval_.left == left]
        if any([border == Border.open for border in left_borders]):
            left_border = Border.open
        else:
            left_border = Border.closed

        right = min(self.right, self.right)
        right_borders = [interval_.right_border for interval_ in (self, other) if interval_.right == right]
        if any([border == Border.open for border in right_borders]):
            right_border = Border.open
        else:
            right_border = Border.closed

        return MyInterval(left=left, right=right, left_border=left_border, right_border=right_border)

    def __str__(self):
        left_border = border_to_str["left"][self.left_border]
        right_border = border_to_str["right"][self.right_border]
        return f"{left_border}{self.left}, {self.right}{right_border}"


class MyArea:
    def __init__(self, intervals: list[MyInterval]):
        self.intervals = intervals

    def normalise(self):
        ...


def __or__(i1: MyInterval, i2: MyInterval) -> MyArea:
    if not i1.overlaps(i2):
        return [i1, i2]
    if i1.left < i2.left:
        left_interval = i1
        right_interval = i2
    else:
        left_interval = i2
        right_interval = i1
    return MyInterval(
        left=left_interval.left,
        left_border=left_interval.left_border,
        right=right_interval.right,
        right_border=right_interval.right_border,
    )


def normalise(intervals: list[MyInterval]) -> list[MyInterval]:
    result = []
    if len(intervals) < 2:
        return intervals

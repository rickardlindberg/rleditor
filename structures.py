class Node:

    def __init__(self, name, start, end, value, children=[]):
        self.name = name
        self.range = Range(start, end)
        self.value = value
        self.children = children
        self.parent = None
        for child in self.children:
            child.parent = self

    def get_path(self):
        if self.parent is None:
            prefix = []
        else:
            prefix = self.parent.get_path()
        return prefix + [self.name]

    def get_next_sibling(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_sibling(self, +1)

    def get_previous_sibling(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_sibling(self, -1)

    def get_sibling(self, child, offset):
        index = 0
        for index, x in enumerate(self.children):
            if x is child:
                break
        return self.children[(index + offset) % len(self.children)]

    def tokenize(self):
        pos = self.range.start
        result = []
        for child in self.children:
            for name, child_start, child_end, d in child.tokenize():
                if pos != child_start:
                    result.append([self.name, pos, child_start, self])
                result.append([name, child_start, child_end, d])
                pos = child_end
        if pos != self.range.end:
            result.append([self.name, pos, self.range.end, self])
        return result

    def as_list(self):
        return [
            self.name,
            self.value,
        ] + [child.as_list() for child in self.children]


class Range:

    def __init__(self, start, end=None):
        self.start = start
        if end is None:
            self.end = start
        else:
            self.end = end

    def contains(self, value):
        if value == self.start == self.end:
            return True
        else:
            return self.start <= value < self.end

    def extend_left(self, amount):
        self.start -= amount

    def extend_right(self, amount):
        self.end += amount

    @property
    def size(self):
        return self.end - self.start

    def overlap(self, other):
        """
        >>> Range(0, 5).overlap(Range(1, 8))
        Range(1, 5)
        """
        if other.end <= self.start:
            return Range(0, 0)
        elif other.start >= self.end:
            return Range(0, 0)
        else:
            return Range(max(self.start, other.start), min(self.end, other.end))

    def is_same(self, other):
        return self.start == other.start and self.end == other.end

    def __repr__(self):
        return f"Range({self.start!r}, {self.end!r})"

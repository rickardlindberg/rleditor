class Node:

    def __init__(self, name, start, end, value, children=[]):
        self.name = name
        self.range = Range(start, end)
        self.value = value
        self.children = children

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

    def __init__(self, start, end):
        self.start = start
        self.end = end

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

    def __repr__(self):
        return f"Range({self.start!r}, {self.end!r})"

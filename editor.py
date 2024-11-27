class Editor:
    """
    >>> buffer = Editor.from_text("[1,2]", json_parse, json_pretty)
    >>> print(buffer.text, end="")
    [
        1,
        2
    ]
    """

    @classmethod
    def from_text(cls, text, parse, pretty):
        return cls(text, parse, pretty)

    def __init__(self, text, parse, pretty):
        self.text = ""
        self.selection = Range(0, 0)
        self.parse = parse
        self.pretty = pretty
        self.update_text(text)

    def update_text(self, text):
        self.text = (
            self.text[: self.selection.start] + text + self.text[self.selection.end :]
        )
        self.tree = self.parse(self.text)
        self.text = self.pretty(self.tree)
        self.raw_tokens = self.parse(self.text).tokenize()


class Token:

    def __init__(self, rectangle, node, range_):
        self.rectangle = rectangle
        self.node = node
        self.range = range_

    def hit(self, x, y):
        return self.rectangle.contains(x, y)

    def overlap(self, range_):
        return self.range.overlap(range_)


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


class Tokens:

    def __init__(self):
        self.tokens = []

    def add(self, token):
        self.tokens.append(token)

    def hit(self, x, y):
        for token in self.tokens:
            if token.hit(x, y):
                return token.node

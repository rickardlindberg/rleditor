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
        return self.to_lines()

    def to_lines(self):
        lines = []
        for name, start, end, node in self.raw_tokens:
            text = self.text[start:end]
            for index, sub_part in enumerate(text.split("\n")):
                if index > 0 or len(lines) == 0:
                    lines.append([])
                lines[-1].append(
                    Token(
                        name=name,
                        text=sub_part,
                        range_=Range(start, end),
                        selection=Range(start, end).overlap(self.selection),
                        node=node,
                    )
                )
        return lines


class Token:

    def __init__(self, name, text, range_, selection, node):
        self.name = name
        self.text = text
        self.range = range_
        self.selection = selection
        self.node = node


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

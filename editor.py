class Editor:
    """
    >>> editor = Editor.from_text("[1,2]", json_parse, json_pretty)
    >>> for line in editor.get_lines():
    ...     print(f"Line {line.number}")
    ...     for token in line:
    ...         print(f"  Token {token.name} {token.text!r}")
    Line 1
      Token List '['
    Line 2
      Token List '    '
      Token Number '1'
      Token List ','
    Line 3
      Token List '    '
      Token Number '2'
      Token List ''
    Line 4
      Token List ']'
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
        self.selection = Range(self.selection.start + len(text))
        try:
            self.text = self.pretty(self.parse(self.text))
        except SystemExit:
            self.raw_tokens = Node("Unknown", 0, len(self.text), None).tokenize()
        else:
            self.raw_tokens = self.parse(self.text).tokenize()

    def select(self, range_):
        self.selection = range_

    def get_lines(self):
        lines = Lines()
        for name, start, end, node in self.raw_tokens:
            text = self.text[start:end]
            for index, sub_part in enumerate(text.split("\n")):
                if index > 0:
                    lines.newline()
                lines.add_token(
                    Token(
                        name=name,
                        text=sub_part,
                        range_=Range(start, end),
                        selection=Range(start, end).overlap(self.selection),
                        node=node,
                    )
                )
        return list(lines.get())


class Lines:
    """
    >>> lines = Lines()
    """

    def __init__(self):
        self.lines = []
        self.pending = Line(number=1)

    def add_token(self, token):
        self.pending.add_token(token)

    def newline(self):
        self.lines.append(self.pending)
        self.pending = Line(number=len(self.lines) + 1)

    def get(self):
        for line in self.lines:
            yield line
        if self.pending.tokens:
            yield self.pending


class Line:

    def __init__(self, number):
        self.number = number
        self.tokens = []

    def add_token(self, token):
        self.tokens.append(token)

    def __iter__(self):
        return iter(self.tokens)


class Token:

    def __init__(self, name, text, range_, selection, node):
        self.name = name
        self.text = text
        self.range = range_
        self.selection = selection
        self.node = node

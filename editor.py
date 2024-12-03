class Editor:

    @classmethod
    def from_text(cls, text, parse, pretty):
        return cls(text, parse, pretty)

    @classmethod
    def from_file(cls, path):
        with open(path) as f:
            return cls(f.read(), json_parse, json_pretty, path=path)

    def __init__(self, text, parse, pretty, path=None):
        self.text = ""
        self.selection = Range(0, 0)
        self.parse = parse
        self.pretty = pretty
        self.path = path
        self.update_text(text)

    def save(self):
        if self.path is not None:
            with open(self.path, "w") as f:
                f.write(self.text)

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

    def selection_expand(self):
        """
        >>> editor = Editor.from_text('{"key": [1,2]}', json_parse, json_pretty)
        >>> editor.select(Range(23))
        >>> print(editor.text_with_selection_markers, end="")
        {
            "key": [
                <>1,
                2
            ]
        }
        >>> editor.selection_expand()
        >>> print(editor.text_with_selection_markers, end="")
        {
            "key": [
                <1>,
                2
            ]
        }
        >>> editor.selection_expand()
        >>> print(editor.text_with_selection_markers, end="")
        {
            "key": <[
                1,
                2
            ]>
        }
        >>> editor.selection_expand()
        >>> print(editor.text_with_selection_markers, end="")
        {
            <"key": [
                1,
                2
            ]>
        }
        >>> editor.selection_expand()
        >>> print(editor.text_with_selection_markers, end="")
        <{
            "key": [
                1,
                2
            ]
        }>
        >>> editor.selection_expand()
        >>> print(editor.text_with_selection_markers, end="")
        <{
            "key": [
                1,
                2
            ]
        }
        >
        """
        node = self.get_selected_node()
        if node.range.is_same(self.selection) and node.parent:
            self.selection = node.parent.range
        else:
            self.selection = node.range

    def select_next_node(self):
        self.selection = self.get_selected_node().get_next_sibling().range

    def select_previous_node(self):
        self.selection = self.get_selected_node().get_previous_sibling().range

    def get_selected_node(self):
        for line in self.get_lines():
            for token in line:
                if token.range.contains(self.selection.start):
                    return self.get_outermost_node(token.node)
        raise ValueError("Could not find node with selection.")

    def get_outermost_node(self, node):
        if node.parent and node.parent.range.is_same(self.selection):
            return self.get_outermost_node(node.parent)
        else:
            return node

    def select(self, range_):
        self.selection = range_

    @property
    def text_with_selection_markers(self):
        return "".join(
            [
                self.text[: self.selection.start],
                "<",
                self.text[self.selection.start : self.selection.end],
                ">",
                self.text[self.selection.end :],
            ]
        )

    def cursor_forward(self):
        self.select(Range(min(len(self.text), self.selection.start + 1)))

    def cursor_backward(self):
        self.select(Range(max(0, self.selection.start - 1)))

    def get_path(self):
        """
        >>> editor = Editor.from_text("[1,2]", json_parse, json_pretty)
        >>> editor.select(Range(6))
        >>> print(editor.text, end="")
        [
            1,
            2
        ]
        >>> for name, start, end, node in editor.raw_tokens:
        ...     print(f"{name}: {start}-{end}")
        List: 0-6
        Number: 6-7
        List: 7-13
        Number: 13-14
        List: 14-16
        Document: 16-17

        >>> editor.get_path()
        ['Document', 'List', 'Number']
        """
        return self.get_selected_node().get_path()

    def get_lines(self):
        """
        >>> editor = Editor.from_text("[1]", json_parse, json_pretty)
        >>> print(editor.text, end="")
        [
            1
        ]
        >>> for line in editor.get_lines():
        ...     print(f"Line {line.number}")
        ...     for token in line:
        ...         print(f"  Token {token.name} {token.text!r} {token.range}")
        Line 1
          Token List '[' Range(0, 1)
          Token Invisible '\\\\n' Range(1, 2)
        Line 2
          Token List '    ' Range(2, 6)
          Token Number '1' Range(6, 7)
          Token Invisible '\\\\n' Range(7, 8)
        Line 3
          Token List ']' Range(8, 9)
          Token Invisible '\\\\n' Range(9, 10)
        Line 4
          Token Invisible 'EOF' Range(10, 10)
        """
        lines = Lines()
        for name, start, end, node in self.raw_tokens:
            text = self.text[start:end]
            pos = start
            for index, sub_part in enumerate(text.split("\n")):
                if index > 0:
                    lines.add_token(
                        Token(
                            name="Invisible",
                            text="\\n",
                            range_=Range(pos, pos + 1),
                            selection=self.selection,
                            node=node,
                        )
                    )
                    lines.newline()
                    pos += 1
                range_ = Range(pos, pos + len(sub_part))
                if range_.size > 0:
                    lines.add_token(
                        Token(
                            name=name,
                            text=sub_part,
                            range_=range_,
                            selection=self.selection,
                            node=node,
                        )
                    )
                    pos += range_.size
        lines.add_token(
            Token(
                name="Invisible",
                text="EOF",
                range_=Range(end),
                selection=self.selection,
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
    """
    >>> Token(
    ...     name="Invisible",
    ...     text="EOF",
    ...     range_=Range(4),
    ...     selection=Range(0),
    ...     node=None,
    ... ).cursor is None
    True

    >>> Token(
    ...     name="Invisible",
    ...     text="EOF",
    ...     range_=Range(4),
    ...     selection=Range(4),
    ...     node=None,
    ... ).cursor
    0
    """

    def __init__(self, name, text, range_, selection, node):
        self.name = name
        self.text = text
        self.range = range_
        self.selection = range_.overlap(selection)
        if range_.size == 0 and range_.start == selection.start:
            self.cursor = 0
            self.cursor_offset_percent = 0
        elif range_.start <= selection.start < range_.end:
            self.cursor = selection.start - range_.start
            self.cursor_offset_percent = self.cursor / self.range.size
        else:
            self.cursor = None
        self.node = node

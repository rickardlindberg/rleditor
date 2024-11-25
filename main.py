import doctest
import sys


def parse(text):
    return compile_chain(["JsonParser.file"], text)


def pretty(tree):
    return compile_chain(["JsonPrettyPrinter.pretty"], tree.as_list())


def json_parse(text):
    return compile_chain(["JsonParser.file"], text)


def json_pretty(tree):
    return compile_chain(["JsonPrettyPrinter.pretty"], tree.as_list())


def tokens(tree):
    return tree.tokenize()


class Node:

    def __init__(self, name, start, end, value, children=[]):
        self.name = name
        self.start = start
        self.end = end
        self.value = value
        self.children = children

    def tokenize(self):
        pos = self.start
        result = []
        for child in self.children:
            for name, child_start, child_end, d in child.tokenize():
                if pos != child_start:
                    result.append([self.name, pos, child_start, self])
                result.append([name, child_start, child_end, d])
                pos = child_end
        if pos != self.end:
            result.append([self.name, pos, self.end, self])
        return result

    def as_list(self):
        return [
            self.name,
            self.start,
            self.end,
            self.value,
        ] + [child.as_list() for child in self.children]

    def __repr__(self):
        return f"Node(name={self.name!r}, start={self.start!r}, end={self.end!r}, ...)"


def selftest():
    """
    String:

    >>> text = ' "hello" '
    >>> parse(text).as_list()
    ['Document', 0, 9, '', ['String', 1, 8, 'hello']]

    True:

    >>> text = ' true '
    >>> parse(text).as_list()
    ['Document', 0, 6, '', ['True', 1, 5, '']]

    False:

    >>> text = ' false '
    >>> parse(text).as_list()
    ['Document', 0, 7, '', ['False', 1, 6, '']]

    Null:

    >>> text = ' null '
    >>> parse(text).as_list()
    ['Document', 0, 6, '', ['Null', 1, 5, '']]

    Number:

    >>> text = ' 134 '
    >>> parse(text).as_list()
    ['Document', 0, 5, '', ['Number', 1, 4, 134]]

    List:

    >>> text = ' [ 1 , 2 , 3 ] '
    >>> parse(text).as_list()
    ['Document', 0, 15, '', ['List', 1, 14, '', ['Number', 3, 4, 1], ['Number', 7, 8, 2], ['Number', 11, 12, 3]]]

    Dict:

    >>> text = ' { "hello" : 5 } '
    >>> parse(text).as_list()
    ['Document', 0, 17, '', ['Dict', 1, 16, '', ['Entry', 2, 14, '', ['Key', 3, 10, 'hello'], ['Number', 13, 14, 5]]]]

    Full roundtrip example:

    >>> text = ' { "hello" : [1, false, true, null], "there": "hello" } '
    >>> pretty = pretty(parse(text))
    >>> print(pretty, end="")
    {
        "hello": [
            1,
            false,
            true,
            null
        ],
        "there": "hello"
    }

    Tokens:

    >>> for token in tokens(parse("[1, 2]")):
    ...     print(token[:3])
    ['List', 0, 1]
    ['Number', 1, 2]
    ['List', 2, 4]
    ['Number', 4, 5]
    ['List', 5, 6]

    >>> for token in tokens(parse('{"key": 4}')):
    ...     print(token[:3])
    ['Dict', 0, 1]
    ['Key', 1, 6]
    ['Entry', 6, 8]
    ['Number', 8, 9]
    ['Dict', 9, 10]
    """
    doctest.testmod()
    print("ok")


class Rectangle:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, x, y):
        return (self.x <= x <= (self.x + self.width)) and (
            self.y <= y <= (self.y + self.height)
        )


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        GtkUi.create().run()

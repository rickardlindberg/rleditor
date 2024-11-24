import doctest
import sys


def parse(text):
    return compile_chain(["JsonParser.file"], text)


def pretty(text):
    return compile_chain(["JsonParser.file", "JsonPrettyPrinter.pretty"], text)


def selftest():
    """
    String:

    >>> text = ' "hello" '
    >>> parse(text)
    ['Document', 0, 9, '', ['String', 2, 7, 'hello']]
    >>> pretty(text)
    Tokens:
    Token('string', '"hello"')

    True:

    >>> text = ' true '
    >>> parse(text)
    ['Document', 0, 6, '', ['True', 1, 5, '']]
    >>> pretty(text)
    Tokens:
    Token('bool', 'true')

    False:

    >>> text = ' false '
    >>> parse(text)
    ['Document', 0, 7, '', ['False', 1, 6, '']]
    >>> pretty(text)
    Tokens:
    Token('bool', 'false')

    Null:

    >>> text = ' null '
    >>> parse(text)
    ['Document', 0, 6, '', ['Null', 1, 5, '']]
    >>> pretty(text)
    Tokens:
    Token('null', 'null')

    Number:

    >>> text = ' 134 '
    >>> parse(text)
    ['Document', 0, 5, '', ['Number', 1, 4, 134]]
    >>> pretty(text)
    Tokens:
    Token('number', '134')

    List:

    >>> text = ' [ 1 , 2 , 3 ] '
    >>> parse(text)
    ['Document', 0, 15, '', ['List', 1, 14, '', ['Number', 3, 4, 1], ['Number', 7, 8, 2], ['Number', 11, 12, 3]]]
    >>> pretty(text)
    Tokens:
    Token('text', '[\\n    ')
    Token('number', '1')
    Token('text', ',\\n    ')
    Token('number', '2')
    Token('text', ',\\n    ')
    Token('number', '3')
    Token('text', '\\n]')

    Dict:

    >>> text = ' { "hello" : 5 } '
    >>> parse(text)
    ['Document', 0, 17, '', ['Dict', 1, 16, '', ['Entry', 2, 14, ['Key', 4, 9, 'hello'], ['Number', 13, 14, 5]]]]
    >>> pretty(text)
    Tokens:
    Token('text', '{\\n    ')
    Token('string', '"hello"')
    Token('text', ': ')
    Token('number', '5')
    Token('text', '\\n}')

    Full roundtrip example:

    >>> text = ' { "hello" : [1, false, true, null], "there": "hello" } '
    >>> print(pretty(text).as_text(), end="")
    {
        "hello": [
            1,
            false,
            true,
            null
        ],
        "there": "hello"
    }

    Full roundtrip example new style:

    >>> text = ' { "hello" : [1, false, true, null], "there": "hello" } '
    >>> pretty = compile_chain(["JsonParser.file", "JsonPrettyPrinterWithoutTokens.pretty"], text)
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
    """
    doctest.testmod()
    print("ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()

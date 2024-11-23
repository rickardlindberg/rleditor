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
    ['String', Range(2, 7), 'hello']
    >>> pretty(text)
    Tokens:
    Token('string', '"hello"')

    True:

    >>> text = ' true '
    >>> parse(text)
    ['True', Range(1, 5)]
    >>> pretty(text)
    Tokens:
    Token('bool', 'true')

    False:

    >>> text = ' false '
    >>> parse(text)
    ['False', Range(1, 6)]
    >>> pretty(text)
    Tokens:
    Token('bool', 'false')

    Null:

    >>> text = ' null '
    >>> parse(text)
    ['Null', Range(1, 5)]
    >>> pretty(text)
    Tokens:
    Token('null', 'null')

    Number:

    >>> text = ' 134 '
    >>> parse(text)
    ['Number', Range(1, 4), 134]
    >>> pretty(text)
    Tokens:
    Token('number', '134')

    List:

    >>> text = ' [ 1 , 2 , 3 ] '
    >>> parse(text)
    ['List', ['Number', Range(3, 4), 1], ['Number', Range(7, 8), 2], ['Number', Range(11, 12), 3]]
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
    ['Dict', Range(1, 16), ['Entry', ['Key', Range(4, 9), 'hello'], ['Number', Range(13, 14), 5]]]
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
    """
    doctest.testmod()
    print("ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()

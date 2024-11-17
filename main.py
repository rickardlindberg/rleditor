import doctest
import sys


def selftest():
    """
    >>> compile_chain(["Json.file"], ' "hello" ')
    ['String', Range(2, 7), 'hello']

    >>> compile_chain(["Json.file"], ' true ')
    ['True', Range(1, 5)]

    >>> compile_chain(["Json.file"], ' false ')
    ['False', Range(1, 6)]

    >>> compile_chain(["Json.file"], ' null ')
    ['Null', Range(1, 5)]

    >>> compile_chain(["Json.file"], ' 134 ')
    ['Number', Range(1, 4), 134]

    >>> compile_chain(["Json.file"], ' [ 1 , 2 , 3 ] ')
    ['List', ['Number', Range(3, 4), 1], ['Number', Range(7, 8), 2], ['Number', Range(11, 12), 3]]

    >>> compile_chain(["Json.file"], ' { "hello" : 5 } ')
    ['Dict', Range(1, 16), ['Entry', ['Key', Range(4, 9), 'hello'], ['Number', Range(13, 14), 5]]]

    >>> print(compile_chain(["Json.file", "Json.pretty"], ' { "hello" : [1, false, true, null], "there": "hello" } '), end="")
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

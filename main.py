import doctest
import sys


def selftest():
    """
    >>> compile_chain(["Json.file"], ' "hello" ')
    ['String', 'hello']

    >>> compile_chain(["Json.file"], ' true ')
    ['True']

    >>> compile_chain(["Json.file"], ' false ')
    ['False']

    >>> compile_chain(["Json.file"], ' null ')
    ['Null']

    >>> compile_chain(["Json.file"], ' 134 ')
    ['Number', 134]

    >>> compile_chain(["Json.file"], ' [ 1 , 2 , 3 ] ')
    ['List', ['Number', 1], ['Number', 2], ['Number', 3]]

    >>> compile_chain(["Json.file"], ' { "hello" : 5 } ')
    ['Dict', ['Entry', 'hello', ['Number', 5]]]

    >>> print(compile_chain(["Json.file", "Json.pretty"], ' { "hello" : [1, false, true, null], "there": 88 } '), end="")
    {
        "hello": [
            1,
            false,
            true,
            null
        ],
        "there": 88
    }
    """
    doctest.testmod()
    print("ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()

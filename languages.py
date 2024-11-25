def json_parse(text):
    """
    String:

    >>> text = ' "hello" '
    >>> json_parse(text).as_list()
    ['Document', 0, 9, '', ['String', 1, 8, 'hello']]

    True:

    >>> text = ' true '
    >>> json_parse(text).as_list()
    ['Document', 0, 6, '', ['True', 1, 5, '']]

    False:

    >>> text = ' false '
    >>> json_parse(text).as_list()
    ['Document', 0, 7, '', ['False', 1, 6, '']]

    Null:

    >>> text = ' null '
    >>> json_parse(text).as_list()
    ['Document', 0, 6, '', ['Null', 1, 5, '']]

    Number:

    >>> text = ' 134 '
    >>> json_parse(text).as_list()
    ['Document', 0, 5, '', ['Number', 1, 4, 134]]

    List:

    >>> text = ' [ 1 , 2 , 3 ] '
    >>> json_parse(text).as_list()
    ['Document', 0, 15, '', ['List', 1, 14, '', ['Number', 3, 4, 1], ['Number', 7, 8, 2], ['Number', 11, 12, 3]]]

    Dict:

    >>> text = ' { "hello" : 5 } '
    >>> json_parse(text).as_list()
    ['Document', 0, 17, '', ['Dict', 1, 16, '', ['Entry', 2, 14, '', ['Key', 3, 10, 'hello'], ['Number', 13, 14, 5]]]]

    Tokens:

    >>> for token in json_parse("[1, 2]").tokenize():
    ...     print(token[:3])
    ['List', 0, 1]
    ['Number', 1, 2]
    ['List', 2, 4]
    ['Number', 4, 5]
    ['List', 5, 6]

    >>> for token in json_parse('{"key": 4}').tokenize():
    ...     print(token[:3])
    ['Dict', 0, 1]
    ['Key', 1, 6]
    ['Entry', 6, 8]
    ['Number', 8, 9]
    ['Dict', 9, 10]
    """
    return compile_chain(["JsonParser.file"], text)


def json_pretty(tree):
    """
    Roundtrip example:

    >>> text = ' { "hello" : [1, false, true, null], "there": "hello" } '
    >>> print(json_pretty(json_parse(text)), end="")
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
    return compile_chain(["JsonPrettyPrinter.pretty"], tree.as_list())

def json_parse(text):
    """
    String:

    >>> text = ' "hello" '
    >>> json_parse(text).as_list()
    ['Document', '', ['String', 'hello']]

    True:

    >>> text = ' true '
    >>> json_parse(text).as_list()
    ['Document', '', ['True', '']]

    False:

    >>> text = ' false '
    >>> json_parse(text).as_list()
    ['Document', '', ['False', '']]

    Null:

    >>> text = ' null '
    >>> json_parse(text).as_list()
    ['Document', '', ['Null', '']]

    Number:

    >>> text = ' 134 '
    >>> json_parse(text).as_list()
    ['Document', '', ['Number', 134]]

    List:

    >>> text = ' [ 1 , 2 , 3 ] '
    >>> json_parse(text).as_list()
    ['Document', '', ['List', '', ['Number', 1], ['Number', 2], ['Number', 3]]]

    Dict:

    >>> text = ' { "hello" : 5 } '
    >>> json_parse(text).as_list()
    ['Document', '', ['Dict', '', ['Entry', '', ['Key', 'hello'], ['Number', 5]]]]

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


def txt_list_parse(text):
    """
    >>> text = "* hello\\n* there\\n  hoho"
    >>> txt_list_parse(text).as_list()
    ['Document', '', ['Item', '', ['Line', 'hello']], ['Item', '', ['Line', 'there'], ['Line', 'hoho']]]
    """
    return compile_chain(["TxtListParser.file"], text)


def txt_list_pretty(tree):
    """
    >>> text = "* hello\\n* there\\n  hoho"
    >>> print(txt_list_pretty(txt_list_parse(text)), end="")
    * hello
    * there
      hoho
    """
    return compile_chain(["TxtListPrettyPrinter.pretty"], tree.as_list())


def rlmeta_parse(text):
    return compile_chain(["Parser.file"], text)


def rlmeta_pretty(tree):
    """
    >>> print(rlmeta_pretty(rlmeta_parse("Grammar { foo = . }")), end="")
    Grammar {
      foo =
        | .
    }
    """
    return compile_chain(["PrettyPrinter.pretty"], tree.as_list())

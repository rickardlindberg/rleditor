rules = {}


class Stream:

    def __init__(self, items):
        self.items = items
        self.index = 0
        self.latest_error = None
        self.scope = None

    def operator_or(self, matchers):
        for matcher in matchers:
            backtrack_index = self.index
            try:
                return matcher.run(self)
            except MatchError:
                self.index = backtrack_index
        self.error("no or match")

    def operator_and(self, matchers):
        result = self.action()
        for matcher in matchers:
            result = matcher.run(self)
        return result

    def operator_star(self, matcher):
        results = []
        while True:
            backtrack_index = self.index
            try:
                results.append(matcher.run(self))
            except MatchError:
                self.index = backtrack_index
                return self.action(lambda self: [x.eval(self.runtime) for x in results])

    def operator_not(self, matcher):
        backtrack_index = self.index
        try:
            matcher.run(self)
        except MatchError:
            return self.action()
        finally:
            self.index = backtrack_index
        self.error("not matched")

    def action(self, fn=lambda self: None):
        return SemanticAction(self.scope, fn)

    def with_scope(self, matcher):
        current_scope = self.scope
        self.scope = {}
        try:
            return matcher.run(self)
        finally:
            self.scope = current_scope

    def bind(self, name, semantic_action):
        self.scope[name] = semantic_action
        return semantic_action

    def match_list(self, matcher):
        if self.index < len(self.items):
            items, index = self.items, self.index
            try:
                self.items = self.items[self.index]
                self.index = 0
                result = matcher.run(self)
                index += 1
            finally:
                self.items, self.index = items, index
            return result
        self.error("no list found")

    def match_call_rule(self, namespace):
        name = namespace + "." + self.items[self.index]
        if name in rules:
            rule = rules[name]
            self.index += 1
            return rule.run(self)
        else:
            self.error("unknown rule")

    def match_pos(self):
        index = self.index
        return self.action(lambda self: index)

    def match(self, fn, description):
        if self.index < len(self.items):
            item = self.items[self.index]
            if fn(item):
                self.index += 1
                return self.action(lambda self: item)
        self.error(f"expected {description}")

    def error(self, name):
        if not self.latest_error or self.index > self.latest_error[2]:
            self.latest_error = (name, self.items, self.index)
        raise MatchError(*self.latest_error)


class MatchError(Exception):

    def __init__(self, name, items, index):
        Exception.__init__(self, name)
        self.items = items
        self.index = index


class SemanticAction:

    def __init__(self, scope, fn):
        self.scope = scope
        self.fn = fn

    def eval(self, runtime):
        self.runtime = runtime
        return self.fn(self)

    def bind(self, name, value, continuation):
        self.runtime = self.runtime.bind(name, value)
        return continuation()

    def lookup(self, name):
        if name in self.scope:
            return self.scope[name].eval(self.runtime)
        else:
            return self.runtime.lookup(name)


class Runtime:

    def __init__(self, extra={"len": len, "repr": repr, "int": int}):
        self.vars = extra

    def bind(self, name, value):
        return Runtime(dict(self.vars, **{name: value}))

    def lookup(self, name):
        if name in self.vars:
            return self.vars[name]
        else:
            return getattr(self, name)

    def append(self, list, thing):
        list.append(thing)

    def join(self, items, delimiter=""):
        return delimiter.join(
            self.join(item, delimiter) if isinstance(item, list) else str(item)
            for item in items
        )

    def indent(self, text, prefix="    "):
        return "".join(prefix + line for line in text.splitlines(True))

    def splice(self, depth, item):
        if depth == 0:
            return [item]
        else:
            return self.concat([self.splice(depth - 1, subitem) for subitem in item])

    def concat(self, lists):
        return [x for xs in lists for x in xs]

    def Node(self, *args):
        return Node(*args)


class Node:

    def __init__(self, name, start, end, value, children=[]):
        self.name = name
        self.range = Range(start, end)
        self.value = value
        self.children = children
        self.parent = None
        for child in self.children:
            child.parent = self

    def get_first_child(self):
        for child in self.children:
            return child
        return self

    def get_path(self):
        if self.parent is None:
            prefix = []
        else:
            prefix = self.parent.get_path()
        return prefix + [self.name]

    def get_next_sibling(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_sibling(self, +1)

    def get_previous_sibling(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_sibling(self, -1)

    def get_sibling(self, child, offset):
        index = 0
        for index, x in enumerate(self.children):
            if x is child:
                break
        return self.children[(index + offset) % len(self.children)]

    def tokenize(self):
        pos = self.range.start
        result = []
        for child in self.children:
            for name, child_start, child_end, d in child.tokenize():
                if pos != child_start:
                    result.append([self.name, pos, child_start, self])
                result.append([name, child_start, child_end, d])
                pos = child_end
        if pos != self.range.end:
            result.append([self.name, pos, self.range.end, self])
        return result

    def as_list(self):
        return [
            self.name,
            self.value,
        ] + [child.as_list() for child in self.children]


class Range:

    def __init__(self, start, end=None):
        self.start = start
        if end is None:
            self.end = start
        else:
            self.end = end

    def contains(self, value):
        if value == self.start == self.end:
            return True
        else:
            return self.start <= value < self.end

    def extend_left(self, amount):
        self.start -= amount

    def extend_right(self, amount):
        self.end += amount

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

    def is_same(self, other):
        return self.start == other.start and self.end == other.end

    def __repr__(self):
        return f"Range({self.start!r}, {self.end!r})"


def compile_chain(grammars, source):
    import os
    import sys
    import pprint

    runtime = Runtime()
    for rule in grammars:
        try:
            source = rules[rule].run(Stream(source)).eval(runtime)
        except MatchError as e:
            marker = "<ERROR POSITION>"
            if os.isatty(sys.stderr.fileno()):
                marker = f"\033[0;31m{marker}\033[0m"
            if isinstance(e.items, str):
                stream_string = e.items[: e.index] + marker + e.items[e.index :]
            else:
                stream_string = pprint.pformat(e.items)
            sys.exit(
                "ERROR: {}\nPOSITION: {}\nSTREAM:\n{}".format(
                    str(e), e.index, runtime.indent(stream_string)
                )
            )
    return source

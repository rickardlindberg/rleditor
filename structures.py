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
            self.value,
        ] + [child.as_list() for child in self.children]

    def __repr__(self):
        return f"Node(name={self.name!r}, start={self.start!r}, end={self.end!r}, ...)"

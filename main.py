import doctest
import sys

import cairo

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib


def parse(text):
    return compile_chain(["JsonParser.file"], text)


def pretty(tree):
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
            for name, child_start, child_end in child.tokenize():
                if pos != child_start:
                    result.append([self.name, pos, child_start])
                result.append([name, child_start, child_end])
                pos = child_end
        if pos != self.end:
            result.append([self.name, pos, self.end])
        return result

    def as_list(self):
        return [
            self.name,
            self.start,
            self.end,
            self.value,
        ] + [child.as_list() for child in self.children]


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
    ...     print(token)
    ['List', 0, 1]
    ['Number', 1, 2]
    ['List', 2, 4]
    ['Number', 4, 5]
    ['List', 5, 6]

    >>> for token in tokens(parse('{"key": 4}')):
    ...     print(token)
    ['Dict', 0, 1]
    ['Key', 1, 6]
    ['Entry', 6, 8]
    ['Number', 8, 9]
    ['Dict', 9, 10]
    """
    doctest.testmod()
    print("ok")


class Canvas(Gtk.DrawingArea):

    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.add_events(self.get_events() | Gdk.EventMask.POINTER_MOTION_MASK)
        self.connect("draw", self.on_draw)
        self.connect("motion-notify-event", self.on_motion_notify_event)

    def on_draw(self, widget, context):
        context.set_source_rgb(1, 0.7, 1)
        context.paint()
        context.select_font_face("Monospace")
        context.set_font_size(20)
        src = ' { "hello" : [1, false,\n true, null],\n "there": "hello" } '
        self.render_text(context, 20, src)
        self.render_text(
            context,
            400,
            pretty(parse(src)),
        )

    def render_text(self, context, start_x, text):
        tree = parse(text)
        ascent, descent, font_height, _, _ = context.font_extents()
        x = start_x
        y = 40
        for name, start, end in tokens(tree):
            context.set_source_rgb(0.1, 0.1, 0.1)
            part = text[start:end]
            for index, sub_part in enumerate(part.split("\n")):
                if index > 0:
                    y += font_height
                    x = start_x
                context.set_source_rgb(*self.name_to_color(name))
                context.move_to(x, y)
                extents = context.text_extents(sub_part)
                context.text_path(sub_part)
                x += extents.x_advance
                context.fill()

    def name_to_color(self, name):
        names = [
            "Document",
            "Dict",
            "List",
            "Entry",
            "Number",
            "False",
            "True",
            "Null",
            "Key",
            "String",
        ]
        if name in names:
            index = names.index(name)
            percent = (index + 1) / len(names)
            extra = percent * 0.9
            return (0.1, 1.0 - extra, 0.1 + extra)
        else:
            return (0.1, 0.1, 0.1)

    def on_motion_notify_event(self, widget, event):
        self.x, self.y = self.translate_coordinates(self, event.x, event.y)
        self.queue_draw()


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        window = Gtk.Window()
        window.connect("destroy", Gtk.main_quit)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box.pack_start(Canvas(), True, True, 0)
        window.add(box)
        window.show_all()
        Gtk.main()

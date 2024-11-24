import doctest
import sys

import cairo

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib


def parse(text):
    return compile_chain(["JsonParser.file"], text)


def pretty(text):
    return compile_chain(["JsonParser.file", "JsonPrettyPrinter.pretty"], text)


def cut(name, start, end, children):
    result = []
    for child_name, child_start, child_end in children:
        if start != child_start:
            result.append([name, start, child_start])
        result.append([child_name, child_start, child_end])
        start = child_end
    if start != end:
        result.append([name, start, end])
    return result


def selftest():
    """
    String:

    >>> text = ' "hello" '
    >>> parse(text)
    ['Document', 0, 9, '', ['String', 1, 8, 'hello']]
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
    ['Document', 0, 17, '', ['Dict', 1, 16, '', ['Entry', 2, 14, '', ['Key', 3, 10, 'hello'], ['Number', 13, 14, 5]]]]
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

    >>> for position in compile_chain(
    ...     ["JsonParser.file", "JsonPositions.positions"],
    ...     "[1, 2]"
    ... ):
    ...     print(position)
    ['List', 0, 1]
    ['Number', 1, 2]
    ['List', 2, 4]
    ['Number', 4, 5]
    ['List', 5, 6]

    >>> for position in compile_chain(
    ...     ["JsonParser.file", "JsonPositions.positions"],
    ...     '{"key": 4}'
    ... ):
    ...     print(position)
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
            compile_chain(
                ["JsonParser.file", "JsonPrettyPrinterWithoutTokens.pretty"], src
            ),
        )

    def render_text(self, context, start_x, text):
        tree = compile_chain(["JsonParser.file"], text)
        ascent, descent, font_height, _, _ = context.font_extents()
        x = start_x
        y = 40
        for name, start, end in compile_chain(["JsonPositions.positions"], tree):
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

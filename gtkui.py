import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk


class GtkUi:

    @classmethod
    def create(cls):
        return cls()

    def run(self):
        window = Gtk.Window()
        window.connect("destroy", Gtk.main_quit)
        gtk_editor = GtkEditor(
            Editor.from_text(
                ' { "hello" : [1, false,\n true, null],\n "there": "hello" } ',
                json_parse,
                json_pretty,
            )
        )
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box.pack_start(gtk_editor, True, True, 0)
        window.add(box)
        window.show_all()
        Gtk.main()


class GtkEditor(Gtk.DrawingArea):

    def __init__(self, editor):
        Gtk.DrawingArea.__init__(self)
        self.add_events(
            self.get_events()
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.KEY_PRESS_MASK
        )
        self.connect("draw", self.on_draw)
        self.connect("motion-notify-event", self.on_motion_notify_event)
        self.connect("key-press-event", self.on_key_press_event)
        self.set_can_focus(True)
        self.editor = editor

    def on_draw(self, widget, context):
        context.set_source_rgb(1, 0.7, 1)
        context.paint()
        context.select_font_face("Monospace")
        context.set_font_size(20)
        self.tokens = Tokens()
        ascent, descent, font_height, _, _ = context.font_extents()
        start_x = 20
        x = start_x
        y = 40
        for name, start, end, node in self.editor.raw_tokens:
            context.set_source_rgb(0.1, 0.1, 0.1)
            part = self.editor.text[start:end]
            for index, sub_part in enumerate(part.split("\n")):
                if index > 0:
                    y += font_height
                    x = start_x

                extents = context.text_extents(sub_part)
                token = Token(
                    rectangle=Rectangle(x, y - ascent, extents.x_advance, font_height),
                    node=node,
                    range_=Range(start, end),
                )
                self.tokens.add(token)

                if token.overlap(self.editor.selection).size > 0:
                    context.set_source_rgb(0.8, 0.5, 0.8)
                    context.rectangle(
                        token.rectangle.x,
                        token.rectangle.y,
                        token.rectangle.width,
                        token.rectangle.height,
                    )
                    context.fill()

                context.set_source_rgb(*self.name_to_color(name))
                context.move_to(x, y)
                context.text_path(sub_part)
                context.fill()

                x += extents.x_advance

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
        x, y = self.translate_coordinates(self, event.x, event.y)
        foo = self.tokens.hit(x, y)
        if foo:
            self.editor.selection = Range(foo.start, foo.end)
        else:
            self.editor.selection = Range(0, 0)
        self.queue_draw()

    def on_key_press_event(self, widget, event):
        if event.string:
            self.editor.update_text(event.string)
            self.queue_draw()


class Rectangle:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, x, y):
        return (self.x <= x <= (self.x + self.width)) and (
            self.y <= y <= (self.y + self.height)
        )

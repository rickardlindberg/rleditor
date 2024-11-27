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
        self.ui_tokens = UiTokens()
        ascent, descent, font_height, _, _ = context.font_extents()
        start_x = 20
        x = start_x
        y = 40
        for line in self.editor.get_lines():
            for token in line:
                context.set_source_rgb(0.1, 0.1, 0.1)
                extents = context.text_extents(token.text)
                rectangle = Rectangle(x, y - ascent, extents.x_advance, font_height)
                self.ui_tokens.add(
                    UiToken(
                        rectangle=rectangle,
                        token=token,
                    )
                )
                if token.selection.size > 0:
                    context.set_source_rgb(0.8, 0.5, 0.8)
                    context.rectangle(
                        rectangle.x,
                        rectangle.y,
                        rectangle.width,
                        rectangle.height,
                    )
                    context.fill()
                if token.cursor is not None:
                    context.set_source_rgb(0.2, 0.2, 0.2)
                    context.rectangle(
                        rectangle.x,
                        rectangle.y,
                        2,
                        rectangle.height,
                    )
                    context.fill()
                context.set_source_rgb(*self.name_to_color(token.name))
                context.move_to(x, y)
                context.text_path(token.text)
                context.fill()
                x += extents.x_advance
            y += font_height
            x = start_x

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
        token = self.ui_tokens.hit(x, y)
        if token:
            self.editor.select(token.node.range)
        else:
            self.editor.select(Range(0, 0))
        self.queue_draw()

    def on_key_press_event(self, widget, event):
        unicode = Gdk.keyval_to_unicode(event.keyval)
        if unicode >= 32:
            self.editor.update_text(chr(unicode))
            self.queue_draw()


class UiTokens:

    def __init__(self):
        self.ui_tokens = []

    def add(self, ui_token):
        self.ui_tokens.append(ui_token)

    def hit(self, x, y):
        for ui_token in self.ui_tokens:
            if ui_token.contains(x, y):
                return ui_token.token


class UiToken:

    def __init__(self, rectangle, token):
        self.rectangle = rectangle
        self.token = token

    def contains(self, x, y):
        return self.rectangle.contains(x, y)


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

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
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        canvas = Canvas()
        box.pack_start(canvas, True, True, 0)
        window.add(box)
        window.show_all()
        canvas.set_can_focus(True)
        canvas.grab_focus()
        Gtk.main()


class Canvas(Gtk.DrawingArea):

    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        self.add_events(
            self.get_events()
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.KEY_PRESS_MASK
        )
        self.connect("draw", self.on_draw)
        self.connect("motion-notify-event", self.on_motion_notify_event)
        self.connect("key-press-event", self.on_key_press_event)
        self.selection = Range(0, 0)
        self.update_src(' { "hello" : [1, false,\n true, null],\n "there": "hello" } ')

    def on_draw(self, widget, context):
        context.set_source_rgb(1, 0.7, 1)
        context.paint()
        context.select_font_face("Monospace")
        context.set_font_size(20)
        self.tokens = Tokens()
        self.render_text(
            context,
            200,
            self.src,
        )

    def render_text(self, context, start_x, text):
        ascent, descent, font_height, _, _ = context.font_extents()
        x = start_x
        y = 40
        for name, start, end, node in self.raw_tokens:
            context.set_source_rgb(0.1, 0.1, 0.1)
            part = text[start:end]
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

                if token.overlap(self.selection).size > 0:
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

    def update_src(self, src):
        self.src = src
        try:
            self.src = pretty(parse(self.src))
        except SystemExit:
            self.raw_tokens = [
                [
                    "",
                    0,
                    len(self.src),
                    Node("", 0, len(self.src), ""),
                ]
            ]
        else:
            self.raw_tokens = tokens(parse(self.src))
        self.queue_draw()

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
            self.selection = Range(foo.start, foo.end)
        else:
            self.selection = Range(0, 0)
        self.queue_draw()

    def on_key_press_event(self, widget, event):
        if event.string:
            self.update_src(
                self.src[: self.selection.start]
                + event.string
                + self.src[self.selection.end :]
            )

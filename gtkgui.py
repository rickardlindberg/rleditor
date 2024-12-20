import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk


class GtkUi:

    @classmethod
    def create(cls):
        return cls()

    def run(self, args):
        if len(args) == 1:
            editor = Editor.from_file(args[0])
        else:
            editor = Editor.from_text(
                ' { "hello" : [1, false,\n true, null],\n "there": "hello" } ',
                json_parse,
                json_pretty,
            )
        window = Gtk.Window()
        window.connect("destroy", Gtk.main_quit)
        gtk_editor = GtkEditor(editor)
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
        self.gui_tokens = GuiTokens()
        ascent, descent, font_height, _, _ = context.font_extents()

        padding = 4
        start_x = padding
        x = start_x
        y = padding + ascent

        context.set_source_rgb(0.9, 0.6, 0.9)
        context.rectangle(0, 0, widget.get_allocated_width(), font_height + 2 * padding)
        context.fill()

        context.set_source_rgb(0.1, 0.1, 0.1)
        context.move_to(x, y)
        context.text_path(" > ".join(self.editor.get_path()))
        context.fill()
        y += font_height + 2 * padding
        x = start_x

        for line in self.editor.get_lines():
            for token in line:
                context.set_source_rgb(0.1, 0.1, 0.1)
                extents = context.text_extents(token.text)
                rectangle = Rectangle(x, y - ascent, extents.x_advance, font_height)
                self.gui_tokens.add(
                    GuiToken(
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
                        rectangle.x + rectangle.width * token.cursor_offset_percent,
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
        if name == "Invisible":
            return (0.9, 0.6, 0.9)
        if name in names:
            index = names.index(name)
            percent = (index + 1) / len(names)
            extra = percent * 0.9
            return (0.1, 1.0 - extra, 0.1 + extra)
        else:
            return (0.1, 0.1, 0.1)

    def on_motion_notify_event(self, widget, event):
        x, y = self.translate_coordinates(self, event.x, event.y)
        token = self.gui_tokens.hit(x, y)
        if token:
            self.editor.select(token.node.range)
        else:
            self.editor.select(Range(0, 0))
        self.queue_draw()

    def on_key_press_event(self, widget, event):
        unicode = Gdk.keyval_to_unicode(event.keyval)
        if event.keyval == 65361:
            self.editor.cursor_backward()
        elif event.keyval == 65363:
            self.editor.cursor_forward()
        elif event.keyval == 65288:  # backspace
            self.editor.delete_whole_or_before()
        elif event.keyval == 65535:  # del
            self.editor.delete_whole_or_after()
        elif event.keyval == 65293:  # enter
            self.editor.update_text("\n")
        elif event.state & Gdk.ModifierType.CONTROL_MASK and unicode == ord("h"):
            self.editor.selection_expand()
        elif event.state & Gdk.ModifierType.CONTROL_MASK and unicode == ord("l"):
            self.editor.selection_contract()
        elif event.state & Gdk.ModifierType.CONTROL_MASK and unicode == ord("j"):
            self.editor.select_next_node()
        elif event.state & Gdk.ModifierType.CONTROL_MASK and unicode == ord("k"):
            self.editor.select_previous_node()
        elif event.state & Gdk.ModifierType.CONTROL_MASK and unicode == ord("s"):
            self.editor.save()
        elif unicode >= 32:
            self.editor.update_text(chr(unicode))
        else:
            return
        self.queue_draw()

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import subprocess

class EmojiSelector(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Emoji Selector")
        self.set_size_request(300, 200)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        # Sample emojis (you can expand this list)
        emojis = ["😀", "😂", "🤔", "👍", "❤️", "🎉", "🌈", "🍕"]

        for i, emoji in enumerate(emojis):
            button = Gtk.Button(label=emoji)
            button.connect("clicked", self.on_emoji_clicked)
            self.grid.attach(button, i % 4, i // 4, 1, 1)

    def on_emoji_clicked(self, widget):
        emoji = widget.get_label()
        subprocess.run(["wl-copy", emoji])
        self.close()

win = EmojiSelector()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

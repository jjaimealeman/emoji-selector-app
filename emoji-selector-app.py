import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import subprocess
import json

class EmojiSelector(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Emoji Selector")
        self.set_size_request(300, 300)

        # Load emoji data
        with open('emoji_data.json', 'r', encoding='utf-8') as f:
            self.emoji_data = json.load(f)

        # Create main vertical box
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.vbox)

        # Create search entry
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search emojis...")
        self.search_entry.connect("changed", self.on_search_changed)
        self.vbox.pack_start(self.search_entry, False, False, 0)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.vbox.pack_start(scrolled, True, True, 0)

        # Create grid for emojis
        self.grid = Gtk.Grid()
        scrolled.add(self.grid)

        self.display_emojis(self.emoji_data['emojis'])

    def display_emojis(self, emojis):
        # Clear existing buttons
        for child in self.grid.get_children():
            self.grid.remove(child)

        # Create new buttons
        for i, emoji_data in enumerate(emojis):
            button = Gtk.Button(label=emoji_data['emoji'])
            button.connect("clicked", self.on_emoji_clicked)
            self.grid.attach(button, i % 4, i // 4, 1, 1)

        self.show_all()

    def on_emoji_clicked(self, widget):
        emoji = widget.get_label()
        subprocess.run(["wl-copy", emoji])
        self.close()

    def on_search_changed(self, entry):
        text = entry.get_text().lower()
        filtered_emojis = [
            emoji for emoji in self.emoji_data['emojis']
            if text in emoji['name'].lower() or
            text in emoji['category'].lower() or
            any(text in keyword.lower() for keyword in emoji['keywords'])
        ]
        self.display_emojis(filtered_emojis)

win = EmojiSelector()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
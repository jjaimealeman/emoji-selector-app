import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
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
        self.search_entry.connect("key-press-event", self.on_key_press)
        self.vbox.pack_start(self.search_entry, False, False, 0)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.vbox.pack_start(scrolled, True, True, 0)

        # Create grid for emojis
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(5)
        self.grid.set_row_spacing(5)
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        scrolled.add(self.grid)

        # Add status bar
        self.statusbar = Gtk.Statusbar()
        self.vbox.pack_end(self.statusbar, False, False, 0)

        # Set up CSS for better focus visibility
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        button:focus {
            border: 2px solid #3584e4;
        }
        """)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.display_emojis(self.emoji_data['emojis'])

        # Set focus to search entry
        GLib.idle_add(self.search_entry.grab_focus)

    def display_emojis(self, emojis):
        # Clear existing buttons
        for child in self.grid.get_children():
            self.grid.remove(child)

        # Create new buttons
        self.buttons = []
        for i, emoji_data in enumerate(emojis):
            button = Gtk.Button(label=emoji_data['emoji'])
            button.connect("clicked", self.on_emoji_clicked)
            button.set_property("width-request", 50)
            button.set_property("height-request", 50)
            self.grid.attach(button, i % 4, i // 4, 1, 1)
            self.buttons.append(button)

        self.grid.show_all()

        # Update status bar
        self.update_status_bar(len(emojis))

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

    def on_key_press(self, widget, event):
        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        
        if keyval_name == 'Tab':
            if self.buttons:
                self.buttons[0].grab_focus()
            return True
        elif keyval_name in ['Return', 'space']:
            focused = self.get_focus()
            if isinstance(focused, Gtk.Button):
                self.on_emoji_clicked(focused)
            return True
        elif keyval_name in ['Up', 'Down', 'Left', 'Right']:
            self.navigate_grid(keyval_name)
            return True
        
        return False

    def navigate_grid(self, direction):
        focused = self.get_focus()
        if not isinstance(focused, Gtk.Button):
            return

        current_index = self.buttons.index(focused)
        total_buttons = len(self.buttons)
        columns = 4

        if direction == 'Up':
            new_index = (current_index - columns) % total_buttons
        elif direction == 'Down':
            new_index = (current_index + columns) % total_buttons
        elif direction == 'Left':
            new_index = (current_index - 1) % total_buttons
        elif direction == 'Right':
            new_index = (current_index + 1) % total_buttons

        self.buttons[new_index].grab_focus()

    def update_status_bar(self, count):
        self.statusbar.push(0, f"Emojis available: {count}")

win = EmojiSelector()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import sqlite3

class EmojiSelector(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Emoji Selector")
        self.set_size_request(300, 400)

        # Connect to the SQLite database
        self.conn = sqlite3.connect('emojis.db')
        self.cursor = self.conn.cursor()

        # Create main vertical box
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.vbox)

        # Create search box (horizontal box for search entry and count label)
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.vbox.pack_start(search_box, False, False, 0)

        # Create search entry
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search emojis...")
        self.search_entry.connect("changed", self.on_search_changed)
        self.search_entry.connect("key-press-event", self.on_key_press)
        search_box.pack_start(self.search_entry, True, True, 0)

        # Create count label
        self.count_label = Gtk.Label()
        search_box.pack_start(self.count_label, False, False, 0)

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

        self.display_emojis("")

        # Set focus to search entry
        GLib.idle_add(self.search_entry.grab_focus)

    def display_emojis(self, search_term):
        # Clear existing buttons
        for child in self.grid.get_children():
            self.grid.remove(child)

        # Query the database
        if search_term:
            self.cursor.execute('''
            SELECT emoji, name, category, keywords FROM emojis
            WHERE name LIKE ? OR category LIKE ? OR keywords LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            self.cursor.execute('SELECT emoji, name, category, keywords FROM emojis LIMIT 100')  # Limit for initial load

        emojis = self.cursor.fetchall()

        # Create new buttons
        self.buttons = []
        for i, (emoji, name, category, keywords) in enumerate(emojis):
            button = Gtk.Button(label=emoji)
            button.connect("clicked", self.on_emoji_clicked)
            button.connect("focus-in-event", self.on_emoji_focus, (name, category, keywords))
            button.set_property("width-request", 50)
            button.set_property("height-request", 50)
            self.grid.attach(button, i % 4, i // 4, 1, 1)
            self.buttons.append(button)

        self.grid.show_all()

        # Update count label
        self.update_count_label(len(emojis))

    def on_emoji_clicked(self, widget):
        emoji = widget.get_label()
        subprocess.run(["wl-copy", emoji])
        self.close()

    def on_emoji_focus(self, widget, event, emoji_info):
        name, category, keywords = emoji_info
        self.update_status_bar(f"Name: {name} | Category: {category} | Keywords: {keywords}")

    def on_search_changed(self, entry):
        text = entry.get_text().lower()
        self.display_emojis(text)

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

    def update_count_label(self, count):
        self.count_label.set_text(f"Emojis: {count}")

    def update_status_bar(self, message):
        self.statusbar.pop(0)  # Remove any previous message
        self.statusbar.push(0, message)

    def do_destroy(self):
        # Close the database connection when the window is closed
        self.conn.close()
        Gtk.main_quit()

win = EmojiSelector()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
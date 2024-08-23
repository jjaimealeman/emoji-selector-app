import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import json
import math
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Script started")

class EmojiSelector(Gtk.Window):
    def __init__(self):
        logging.info("Initializing EmojiSelector")
        Gtk.Window.__init__(self, title="Emoji Selector")
        self.set_default_size(300, 400)

        # Load emoji data
        try:
            with open('emoji_data.json', 'r', encoding='utf-8') as f:
                self.emoji_data = json.load(f)
            logging.info(f"Loaded {len(self.emoji_data['emojis'])} emojis from JSON file")
        except Exception as e:
            logging.error(f"Error loading JSON file: {e}")
            self.emoji_data = {'emojis': []}

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
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.vbox.pack_start(self.scrolled, True, True, 0)

        # Create grid for emojis
        self.grid = Gtk.Grid()
        self.scrolled.add(self.grid)

        # Set focus to search entry
        GLib.idle_add(self.search_entry.grab_focus)

        # Connect size-allocate signal
        self.connect("size-allocate", self.on_size_allocate)

        print("Initialization complete, about to display emojis")
        self.display_emojis(self.emoji_data['emojis'])

    def display_emojis(self, emojis):
        logging.info(f"Displaying {len(emojis)} emojis")
        # Clear existing buttons
        for child in self.grid.get_children():
            self.grid.remove(child)

        # Calculate number of columns based on window width
        width = self.get_allocation().width
        button_width = 40  # Estimated width of each emoji button
        columns = max(4, math.floor(width / button_width))
        logging.debug(f"Window width: {width}, Columns: {columns}")

        # Create new buttons
        self.buttons = []
        for i, emoji_data in enumerate(emojis):
            button = Gtk.Button(label=emoji_data['emoji'])
            button.connect("clicked", self.on_emoji_clicked)
            self.grid.attach(button, i % columns, i // columns, 1, 1)
            self.buttons.append(button)

        self.show_all()
        logging.info(f"Created {len(self.buttons)} emoji buttons")

    def on_emoji_clicked(self, widget):
        emoji = widget.get_label()
        subprocess.run(["wl-copy", emoji])
        print(f"Copied emoji: {emoji}")
        self.close()

    def on_search_changed(self, entry):
        logging.info("Search changed")
        text = entry.get_text().lower()
        filtered_emojis = [
            emoji for emoji in self.emoji_data['emojis']
            if text in emoji['name'].lower() or
            text in emoji['category'].lower() or
            any(text in keyword.lower() for keyword in emoji['keywords'])
        ]
        logging.info(f"Found {len(filtered_emojis)} matching emojis")
        self.display_emojis(filtered_emojis)

    def on_key_press(self, widget, event):
        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        print(f"Key pressed: {keyval_name}")
        
        if keyval_name == 'Tab':
            if self.buttons:
                self.buttons[0].grab_focus()
            return True
        elif keyval_name in ['Return', 'space']:
            focused = self.get_focus()
            if isinstance(focused, Gtk.Button):
                self.on_emoji_clicked(focused)
            return True
        
        return False

    def on_size_allocate(self, widget, allocation):
        print("Window resized")
        # Redisplay emojis when window size changes
        self.display_emojis(self.emoji_data['emojis'])

logging.info("Creating EmojiSelector instance")
win = EmojiSelector()
win.connect("destroy", Gtk.main_quit)
win.show_all()
logging.info("Starting main GTK loop")
Gtk.main()
logging.info("Application closed")

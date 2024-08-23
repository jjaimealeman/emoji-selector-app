import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import json
import math
import logging
import os

# Configure logging
log_file = 'emoji_selector.log'
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),
                        logging.StreamHandler()
                    ])

logging.info("Script started")
logging.info(f"Log file created at: {os.path.abspath(log_file)}")
logging.info("GTK Version: %s.%s.%s", Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())

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
        self.grid.set_column_spacing(5)
        self.grid.set_row_spacing(5)
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
<<<<<<< HEAD
        self.scrolled.add(self.grid)
=======
        scrolled.add(self.grid)

        self.display_emojis(self.emoji_data['emojis'])
>>>>>>> working-version

        # Set focus to search entry
        GLib.idle_add(self.search_entry.grab_focus)

        # Connect size-allocate signal
        self.connect("size-allocate", self.on_size_allocate)

        logging.info("Initialization complete, about to display emojis")
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
            button.set_property("width-request", button_width)
            button.set_property("height-request", button_width)
            button.connect("clicked", self.on_emoji_clicked)
<<<<<<< HEAD
            self.grid.attach(button, i % columns, i // columns, 1, 1)
            self.buttons.append(button)

        self.grid.show_all()
        logging.info(f"Created {len(self.buttons)} emoji buttons")
=======
            button.set_property("width-request", 50)
            button.set_property("height-request", 50)
            self.grid.attach(button, i % 4, i // 4, 1, 1)
            self.buttons.append(button)

        self.grid.show_all()
>>>>>>> working-version

    def on_emoji_clicked(self, widget):
        emoji = widget.get_label()
        subprocess.run(["wl-copy", emoji])
        logging.info(f"Copied emoji: {emoji}")
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
        logging.debug(f"Key pressed: {keyval_name}")
        
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
        logging.debug("Window resized")
        # Redisplay emojis when window size changes
        self.display_emojis(self.emoji_data['emojis'])

logging.info("Creating EmojiSelector instance")
win = EmojiSelector()
win.connect("destroy", Gtk.main_quit)
win.show_all()
<<<<<<< HEAD
logging.info("Starting main GTK loop")
Gtk.main()
logging.info("Application closed")
=======
Gtk.main()
>>>>>>> working-version

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import sqlite3

class EmojiSelector(Gtk.Window):
    def __init__(self):
        """Initialize the EmojiSelector window and set up the UI."""
        Gtk.Window.__init__(self, title="Emoji Selector")
        self.set_size_request(400, 500)

        # Connect to the SQLite database
        self.conn = sqlite3.connect('emojis.db')
        self.cursor = self.conn.cursor()

        # Get total number of emojis
        self.cursor.execute('SELECT COUNT(*) FROM emojis')
        self.total_emojis = self.cursor.fetchone()[0]

        # Set up the main layout
        self.setup_layout()

        # Initialize selected emojis list
        self.selected_emojis = []

        self.display_emojis([])
        self.update_status_bar(None, None)  # Show shortcuts initially

        # Set focus to search entry
        GLib.idle_add(self.search_entry.grab_focus)

    def setup_layout(self):
        """Set up the main layout of the application."""
        # Create main vertical box
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.vbox)

        # Create search box
        self.create_search_box()

        # Create scrolled window for emoji grid
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

        # Create status bar
        self.create_status_bar()

        # Set up CSS for styling
        self.setup_css()

        # Connect key-press-event to the window
        self.connect("key-press-event", self.on_window_key_press)

    def create_search_box(self):
        """Create the search box with entry and count label."""
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        search_box.set_margin_start(10)
        search_box.set_margin_end(10)
        search_box.set_margin_top(10)
        search_box.set_margin_bottom(10)
        self.vbox.pack_start(search_box, False, False, 0)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search emojis (comma-separated)...")
        self.search_entry.connect("changed", self.on_search_changed)
        self.search_entry.connect("key-press-event", self.on_key_press)
        search_box.pack_start(self.search_entry, True, True, 0)

        self.count_label = Gtk.Label()
        self.count_label.set_margin_start(10)
        search_box.pack_start(self.count_label, False, False, 0)

    def create_status_bar(self):
        """Create the status bar with emoji information and shortcuts."""
        self.status_grid = Gtk.Grid()
        self.status_grid.set_column_spacing(5)
        self.status_grid.set_row_spacing(2)
        self.vbox.pack_end(self.status_grid, False, False, 0)

        self.emoji_label = Gtk.Label(xalign=0)
        self.emoji_label.set_line_wrap(True)
        self.emoji_label.set_max_width_chars(40)
        self.keywords_label = Gtk.Label(xalign=0)
        self.keywords_label.set_line_wrap(True)
        self.keywords_label.set_max_width_chars(30)
        self.selected_label = Gtk.Label(xalign=0)
        self.shortcuts_label = Gtk.Label(xalign=0)
        self.shortcuts_label.set_line_wrap(True)
        self.shortcuts_label.set_max_width_chars(40)

        self.status_grid.attach(self.emoji_label, 0, 0, 2, 1)
        self.status_grid.attach(self.keywords_label, 0, 1, 2, 1)
        self.status_grid.attach(self.selected_label, 0, 2, 2, 1)
        self.status_grid.attach(self.shortcuts_label, 0, 3, 2, 1)

        self.status_grid.set_column_homogeneous(True)
        self.status_grid.set_column_spacing(10)
        self.status_grid.set_row_spacing(5)
        self.status_grid.set_border_width(5)

    def setup_css(self):
        """Set up CSS for styling the application."""
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        button:focus { border: 2px solid #3584e4; }
        label { padding: 2px 5px; }
        #emoji_label, #keywords_label, #selected_label, #shortcuts_label {
            margin-left: 10px;
            margin-right: 10px;
        }
        #search_entry { margin: 5px; }
        #count_label { margin-right: 5px; }
        """)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Set widget names for CSS styling
        self.emoji_label.set_name("emoji_label")
        self.keywords_label.set_name("keywords_label")
        self.selected_label.set_name("selected_label")
        self.shortcuts_label.set_name("shortcuts_label")
        self.search_entry.set_name("search_entry")
        self.count_label.set_name("count_label")

    def display_emojis(self, search_terms):
        """Display emojis based on search terms."""
        for child in self.grid.get_children():
            self.grid.remove(child)

        if search_terms:
            query = '''
            SELECT DISTINCT emoji, keywords FROM emojis
            WHERE '''
            conditions = []
            params = []
            for term in search_terms:
                condition = 'keywords LIKE ?'
                conditions.append(condition)
                params.append(f'%{term}%')
            query += ' AND '.join(conditions)
            self.cursor.execute(query, params)
        else:
            self.cursor.execute('SELECT DISTINCT emoji, keywords FROM emojis LIMIT 100')

        emojis = self.cursor.fetchall()

        self.buttons = []
        for i, (emoji, keywords) in enumerate(emojis):
            button = Gtk.Button()
            label = Gtk.Label()
            label.set_markup(f'<span size="xx-large">{emoji}</span>')
            button.add(label)
            button.connect("clicked", self.on_emoji_clicked)
            button.connect("focus-in-event", self.on_emoji_focus, (emoji, keywords))
            button.set_property("width-request", 100)
            button.set_property("height-request", 100)
            self.grid.attach(button, i % 3, i // 3, 1, 1)
            self.buttons.append(button)

        self.grid.show_all()
        self.update_count_label(len(emojis))

    def on_emoji_clicked(self, widget):
        """Handle emoji button click event."""
        emoji = widget.get_child().get_text()
        if emoji in self.selected_emojis:
            self.selected_emojis.remove(emoji)
            widget.get_style_context().remove_class('selected')
        else:
            self.selected_emojis.append(emoji)
            widget.get_style_context().add_class('selected')
        self.update_selected_label()

    def on_emoji_focus(self, widget, event, emoji_info):
        """Handle emoji button focus event."""
        emoji, keywords = emoji_info
        self.update_status_bar(emoji, keywords)

    def on_search_changed(self, entry):
        """Handle search entry text change event."""
        text = entry.get_text().lower()
        search_terms = [term.strip() for term in text.split(',') if term.strip()]
        self.display_emojis(search_terms)
        
        # Hide shortcuts when user starts typing
        if text:
            self.shortcuts_label.set_text("")
        else:
            self.update_status_bar(None, None)  # Show shortcuts again if search is cleared

    def on_window_key_press(self, widget, event):
        """Handle window key press events."""
        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        state = event.state
        
        if keyval_name == 'Return':
            self.copy_selected_and_quit()
            return True
        elif keyval_name == 'Escape':
            self.search_entry.grab_focus()
            return True
        elif (state & Gdk.ModifierType.CONTROL_MASK) and keyval_name == 'c':
            self.close()
            return True
        
        return False

    def on_key_press(self, widget, event):
        """Handle key press events in the search entry."""
        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        
        if keyval_name in ['Tab', 'Down', 'Right']:
            if self.buttons:
                self.buttons[0].grab_focus()
            return True
        elif keyval_name == 'space':
            focused = self.get_focus()
            if isinstance(focused, Gtk.Button):
                self.on_emoji_clicked(focused)
            return True
        elif keyval_name in ['Up', 'Left']:
            if self.buttons:
                self.buttons[-1].grab_focus()
            return True
        
        return False

    def update_count_label(self, count):
        """Update the count label with the number of displayed emojis."""
        if count == self.total_emojis:
            self.count_label.set_text(f"Emojis: {count}")
        else:
            self.count_label.set_text(f"Emojis loaded: {count} of {self.total_emojis}")

    def update_status_bar(self, emoji, keywords):
        """Update the status bar with emoji information or shortcuts."""
        if emoji is None and keywords is None:
            self.emoji_label.set_text("")
            self.keywords_label.set_text("")
            self.shortcuts_label.set_markup(
                "<b>Keyboard Shortcuts:</b>\n"
                "Space: Select/Unselect emoji\n"
                "Enter: Copy selected and quit\n"
                "Esc: Focus search field\n"
                "Ctrl+C: Quit application"
            )
        else:
            self.emoji_label.set_text(f"Emoji: {emoji}")
            formatted_keywords = "  ".join(keywords.split(","))
            self.keywords_label.set_text(f"Keywords: {formatted_keywords}")
            self.shortcuts_label.set_text("")

    def update_selected_label(self):
        """Update the label showing selected emojis."""
        if self.selected_emojis:
            self.selected_label.set_text(f"Selected: {''.join(self.selected_emojis)}")
        else:
            self.selected_label.set_text("No emojis selected")

    def copy_selected_and_quit(self):
        """Copy selected emojis to clipboard and close the application."""
        if self.selected_emojis:
            subprocess.run(["wl-copy", ''.join(self.selected_emojis)])
        self.close()

    def do_destroy(self):
        """Clean up resources when the window is destroyed."""
        self.conn.close()
        Gtk.main_quit()

win = EmojiSelector()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
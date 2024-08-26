# Emoji Selector App

A simple GTK-based emoji selector application for Linux.

## Prerequisites

- Python 3
- GTK 3
- SQLite3

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/emoji-selector-app.git
   cd emoji-selector-app
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up the emoji database:
   ```
   python create_emoji_db.py
   ```

## Usage

Run the application:

```
python emoji-selector-app-sqlite.py
```

## Optional: Create a launch script

For easier launching, create a bash script:

1. Create a file named `launch-emoji-selector.sh` with the following content:
   ```bash
   #!/bin/bash
   cd ~/home/jaime/python_projects/emoji-selector-app
   python emoji-selector-app-sqlite.py
   ```

2. Make it executable:
   ```
   chmod +x launch-emoji-selector.sh
   ```

3. Move it to a directory in your PATH:
   ```
   mv launch-emoji-selector.sh ~/bin/
   ```

Now you can launch the app from anywhere by typing `launch-emoji-selector.sh` in the terminal.

## Create a Desktop File for Rofi

To launch the Emoji Selector App from Rofi, create a desktop file:

1. Create a new file named `emoji-selector.desktop` in `~/.local/share/applications/`:
   ```
   nvim ~/.local/share/applications/emoji-selector.desktop
   ```

2. Add the following content to the file:
   ```
   [Desktop Entry]
   Type=Application
   Name=Emoji Selector
   Comment=Select and copy emojis easily
   Exec=/home/jaime/Applications/launch-emoji-selector.sh
   Icon=/home/jaime/python_projects/emoji-selector-app/emoji.png
   Categories=Utility;
   ```

   Replace `/path/to/emoji-selector-app/` with the actual path to your app's directory.

3. Save the file and exit the text editor.

4. Make the desktop file executable:
   ```
   chmod +x ~/.local/share/applications/emoji-selector.desktop
   ```

Now, you should be able to find and launch the Emoji Selector App using Rofi.

## License

[MIT License](LICENSE)
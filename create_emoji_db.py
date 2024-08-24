# create_emoji_db.py
import sqlite3
import json

# Create a connection to the SQLite database
conn = sqlite3.connect('emojis.db')
cursor = conn.cursor()

# Create the emojis table
cursor.execute('''
CREATE TABLE IF NOT EXISTS emojis (
    id INTEGER PRIMARY KEY,
    emoji TEXT,
    name TEXT,
    category TEXT,
    keywords TEXT
)
''')

# Create indexes for faster searching
cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON emojis(name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON emojis(category)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords ON emojis(keywords)')

# Load emoji data from JSON file
with open('emoji_data.json', 'r', encoding='utf-8') as f:
    emoji_data = json.load(f)

# Prepare data for batch insert
emoji_list = [(emoji['emoji'], emoji['name'], emoji['category'], ','.join(emoji['keywords']))
              for emoji in emoji_data['emojis']]

# Batch insert emoji data into the database
cursor.executemany('''
INSERT INTO emojis (emoji, name, category, keywords)
VALUES (?, ?, ?, ?)
''', emoji_list)

# Commit changes and close the connection
conn.commit()
conn.close()

print(f"Emoji database created successfully with {len(emoji_list)} emojis!")
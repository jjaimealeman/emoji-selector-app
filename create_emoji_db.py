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

# Load emoji data from JSON file
with open('emoji_data.json', 'r', encoding='utf-8') as f:
    emoji_data = json.load(f)

# Insert emoji data into the database
for emoji in emoji_data['emojis']:
    cursor.execute('''
    INSERT INTO emojis (emoji, name, category, keywords)
    VALUES (?, ?, ?, ?)
    ''', (emoji['emoji'], emoji['name'], emoji['category'], ','.join(emoji['keywords'])))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Emoji database created successfully!")

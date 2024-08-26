# create_emoji_db.py
import sqlite3
import json

def create_emoji_database(json_file, db_file):
    """
    Create a SQLite database from a JSON file containing emoji data.
    
    :param json_file: Path to the JSON file with emoji data
    :param db_file: Path to the SQLite database file to be created
    """
    # Establish a connection to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the emojis table with the new structure
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emojis (
        id INTEGER PRIMARY KEY,
        emoji TEXT,
        keywords TEXT
    )
    ''')

    # Create an index on keywords for faster searching
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords ON emojis(keywords)')

    # Load emoji data from JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        emoji_data = json.load(f)

    # Prepare data for batch insert
    emoji_list = [(emoji['emoji'], ','.join(emoji['keywords']))
                  for emoji in emoji_data['emojis']]

    # Batch insert emoji data into the database
    cursor.executemany('''
    INSERT INTO emojis (emoji, keywords)
    VALUES (?, ?)
    ''', emoji_list)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print(f"Emoji database created successfully with {len(emoji_list)} emojis!")

if __name__ == "__main__":
    create_emoji_database('emoji_data.json', 'emojis.db')
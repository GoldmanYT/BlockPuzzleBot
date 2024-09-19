from sqlite3 import connect

db = connect('data/block_puzzle.db')
cursor = db.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    score INTEGER,
    figure1 INTEGER,
    figure2 INTEGER,
    figure3 INTEGER,
    field TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY,
    name STRING,
    value INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    all_buttons_on_screen BOOLEAN
) 
''')

cursor.execute('''DELETE FROM records
''')

db.commit()

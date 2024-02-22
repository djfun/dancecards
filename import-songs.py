#
# This is a work in progress; do not use in production yet.
import csv
import os.path
import random
import sqlite3
import sys
import string
import time

DATABASE = './dancecards.db'

with open('songlist.csv', newline='') as f:
  reader = csv.DictReader(f)
  data = list(reader)

db = sqlite3.connect(DATABASE)
cur = db.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS "songs" (
  "id"  INTEGER PRIMARY KEY AUTOINCREMENT,
  "title" INTEGER NOT NULL,
  "keysig"  TEXT NOT NULL DEFAULT '',
  "composer"  TEXT NOT NULL DEFAULT '',
  "arranger"  TEXT NOT NULL DEFAULT '',
  "brigade" TEXT NOT NULL DEFAULT 'XQHB',
  "order" INTEGER DEFAULT 0,
  "year" INTEGER DEFAULT 0,
  "coretype"  TEXT NOT NULL DEFAULT 'Core',
  "optional" INTEGER NOT NULL DEFAULT 0
)''')

# Futhre data structure.
#  cur.execute('''CREATE TABLE IF NOT EXISTS "setlist" (
#    "id"  INTEGER PRIMARY KEY AUTOINCREMENT,
#    "songid"  INTEGER,
#    "brigade" TEXT NOT NULL DEFAULT 'XQHB',
#    "order" INTEGER DEFAULT 0,
#    "year" INTEGER DEFAULT 0,
#    "coretype"  TEXT NOT NULL DEFAULT 'Core',
#    "opt" INTEGER NOT NULL DEFAULT 0
#  )''')

for line in data:
  cur.execute("INSERT into songs(title, keysig, ) values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (line['PARTNUM'], line['NICK'], line['NAME'], line['EMAIL'], code, line['VOICEPART'].lower(), line['PHONE'], photo, line['LOCATION']))

db.commit()
db.close()

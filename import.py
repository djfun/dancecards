import csv
import os.path
import random
import sqlite3
import sys
import string
import time

# Assign these to the position of the column containing the relevant data in the .csv.
# We calculate the unique ID and the photo fields on the fly.
PARTNUM = 0
NICK = 1
NAME = 2
EMAIL = 3
VOICEPART = 4
PHONE = 5
LOCATION = 6

DATABASE = './dancecards.db'

def random_generator(size=6, chars=string.ascii_lowercase + string.digits):
  return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(size))

if os.path.isfile(DATABASE):
  print("Database file already exists.")
  if not input("Do you want to continue? (y/n): ").lower().strip()[:1] == "y": sys.exit(1)
  os.remove(DATABASE)

with open('dancecards.csv', newline='') as f:
  reader = csv.DictReader(f)
  data = list(reader)

db = sqlite3.connect(DATABASE)
cur = db.cursor()

cur.execute('''CREATE TABLE "singers" (
  "id"  INTEGER PRIMARY KEY AUTOINCREMENT,
  "partnum" INTEGER NOT NULL UNIQUE,
  "prefname"  TEXT NOT NULL,
  "name"  TEXT NOT NULL,
  "location"  TEXT NOT NULL DEFAULT '',
  "email" TEXT NOT NULL,
  "phone" TEXT NOT NULL DEFAULT '',
  "code"  TEXT NOT NULL UNIQUE,
  "voicepart" TEXT NOT NULL,
  "supertramp" INTEGER NOT NULL DEFAULT 0,
  "asleep" INTEGER NOT NULL DEFAULT 0,
  "left" INTEGER NOT NULL DEFAULT 0,
  "opt" INTEGER NOT NULL DEFAULT 0,
  "photo" TEXT NOT NULL DEFAULT ''
)''')
cur.execute('''CREATE TABLE "stickers" (
  "id"  INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,
  "receiver_id" INTEGER NOT NULL,
  "time"  INTEGER NOT NULL
)''')

for line in data:
  code = random_generator(size=8)
  photo = line['EMAIL'].replace('.', '_')
  photo = photo.replace('@', '_')
  cur.execute("INSERT into singers(partnum, prefname, name, email, code, voicepart, phone, photo, location) values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (line['PARTNUM'], line['NICK'], line['NAME'], line['EMAIL'], code, line['VOICEPART'].lower(), line['PHONE'], photo, line['LOCATION']))

db.commit()
db.close()

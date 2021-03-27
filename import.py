import csv
import os.path
import random
import sqlite3
import sys
import string
import time

DATABASE = './dancecards.db'

def random_generator(size=6, chars=string.ascii_lowercase + string.digits):
  return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(size))

if os.path.isfile(DATABASE):
  print("Database file already exists.")
  if not input("Do you want to continue? (y/n): ").lower().strip()[:1] == "y": sys.exit(1)
  os.remove(DATABASE)

with open('dancecards.csv', newline='') as f:
  reader = csv.reader(f)
  data = list(reader)

db = sqlite3.connect(DATABASE)
cur = db.cursor()

cur.execute('''CREATE TABLE "singers" (
  "id"  INTEGER PRIMARY KEY AUTOINCREMENT,
  "name"  TEXT NOT NULL,
  "location"  TEXT NOT NULL,
  "email" TEXT NOT NULL,
  "code"  TEXT NOT NULL UNIQUE,
  "voicepart" TEXT NOT NULL
)''')
cur.execute('''CREATE TABLE "stickers" (
  "id"  INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,
  "receiver_id" INTEGER NOT NULL,
  "time"  INTEGER NOT NULL
)''')

for line in data:
  code = random_generator(size=8)
  cur.execute("INSERT into singers(name, location, email, code, voicepart) values (?, ?, ?, ?, ?)", (line[0], line[1], line[2], code, line[3]))

db.commit()
db.close()
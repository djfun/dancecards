import csv
import os.path
import random
import sqlite3
import sys
import string
import time

DATABASE = './dancecards.db'

if os.path.isfile(DATABASE):
  print("Database file already exists.")
  if not input("Do you want to continue? (y/n): ").lower().strip()[:1] == "y": sys.exit(1)
else:
  printf("Database file doesn't exist; stopping without further action")
  sys.exit(1)

db = sqlite3.connect(DATABASE)
cur = db.cursor()

cur.execute('''DELETE FROM "stickers"''')
db.commit()
print("stickers reset.")
db.close()

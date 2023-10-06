#!/usr/bin/python3
import os.path
import random
import sqlite3
import sys
import string
import time

DATABASE = './dancecards.db'

db = sqlite3.connect(DATABASE)
cur = db.cursor()


cur.execute("SELECT name, email, voicepart, code \
from singers order by id")

singers = cur.fetchall()

print("---------------------------------------------------------------------------")
print("              All singers")
print("---------------------------------------------------------------------------")

for singer in singers:
  s_name = singer[0]
  s_email = singer[1]
  s_voicepart = singer[2]
  s_code = singer[3]

  print(f'''{s_name:<30} {s_email:<40} {s_voicepart:<20} https://dancecards.europeanharmonybrigade.org/card/{s_code}''')

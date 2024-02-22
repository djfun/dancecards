#!/usr/bin/python3
import os.path
import random
import sqlite3
import sys
import string
import time

DATABASE = './dancecards.db'

tld = 'xqhb.ddns.net'

db = sqlite3.connect(DATABASE)
cur = db.cursor()


cur.execute("SELECT name, email, voicepart, code, partnum \
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
  s_partnum = singer[4]

# dancecards.europeanharmonybrigade.org
  print(f'''{s_name:<30} ({s_partnum:<2}) {s_email:<40} {s_voicepart:<20} https://{tld}/card/{s_code}''')

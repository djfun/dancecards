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


cur.execute("SELECT s1.name, s1.voicepart, count(st1.user_id) as received_stickers, \
(select count(singers.name) from singers left join stickers on stickers.user_id = singers.id and stickers.receiver_id = s1.id where stickers.id is null and singers.voicepart != s1.voicepart) as missing_count, \
case when count(st1.user_id) == (select count(*) from singers as s3 where s3.voicepart != s1.voicepart) then 1 else 0 end as tramp, \
(select group_concat(singers.name, \", \") from singers left join stickers on stickers.user_id = singers.id and stickers.receiver_id = s1.id where stickers.id is null and singers.voicepart != s1.voicepart) as missing \
from singers as s1 \
left join stickers as st1 on st1.receiver_id=s1.id and st1.user_id != s1.id \
left join singers as s2 on s2.id=st1.user_id and s2.voicepart != s1.voicepart \
group by s1.id")

singers = cur.fetchall()

print("---------------------------------------------------------------------------")
print("              TRAMP")
print("---------------------------------------------------------------------------")

for singer in singers:
  s_name = singer[0]
  s_voicepart = singer[1]
  s_received_count = singer[2]
  s_missing_count = singer[3]
  s_tramp = singer[4]
  s_missing = singer[5]

  print(f'''{s_name:<30} {s_voicepart:<20} {s_received_count} (missing: {s_missing_count})''', end='')
  if s_tramp:
    print("\tTramp!\t")
  else:
    print("")
  #  print(f'''\t\t\tMissing: {s_missing}''')

cur.execute("SELECT s1.name, s1.voicepart, count(st1.user_id) as received_stickers, \
(select count(singers.name) from singers left join stickers on stickers.user_id = singers.id and stickers.receiver_id = s1.id where stickers.id is null and singers.id != s1.id) as missing_count, \
case when count(st1.user_id) == (select count(*) from singers) then 1 else 0 end as supertramp, \
(select group_concat(singers.name, \", \") from singers left join stickers on stickers.user_id = singers.id and stickers.receiver_id = s1.id where stickers.id is null and singers.id != s1.id) as missing \
from singers as s1 \
left join stickers as st1 on st1.receiver_id=s1.id and st1.user_id != s1.id \
group by s1.id")

singers = cur.fetchall()

print("---------------------------------------------------------------------------")
print("              SUPERTRAMP")
print("---------------------------------------------------------------------------")

for singer in singers:
  s_name = singer[0]
  s_voicepart = singer[1]
  s_received_count = singer[2]
  s_missing_count = singer[3]
  s_supertramp = singer[4]
  s_missing = singer[5]

  print(f'''{s_name:<30} {s_voicepart:<20} {s_received_count} (missing: {s_missing_count})''', end='')
  if s_supertramp:
    print("\tSupertramp!\t")
  else:
    print("")
  #  print(f'''\t\t\tMissing: {s_missing}''')


db.close()

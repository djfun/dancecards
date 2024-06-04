#!/usr/bin/python3
import os.path
import random
import sqlite3
import sys
import string
import time
from config import *
from termcolor import colored

db = sqlite3.connect(DATABASE)
cur = db.cursor()

cur.execute("""SELECT voicepart,
                    count(id) as numberofsingers
                    from singers
                    group by voicepart""")
v_count = {}

allsingers = cur.fetchall()
for v in allsingers:
  v_count[v[0]] = v[1]

cur.execute("""SELECT s1.name,
s1.voicepart,
s1.code,
count(st1.user_id) as received_stickers,
count(s_tenor.id) as count_tenor,
count(s_lead.id) as count_lead,
count(s_bari.id) as count_bari,
count(s_bass.id) as count_bass,
(select group_concat(singers.name, \", \") from singers left join stickers on stickers.user_id = singers.id and stickers.receiver_id = s1.id where stickers.id is null and singers.voicepart != s1.voicepart) as missing,
(select group_concat(singers.name, \", \") from singers left join stickers on stickers.user_id = singers.id and stickers.receiver_id = s1.id where stickers.id is null and singers.id != s1.id and singers.voicepart != 'guest') as missing_stramp
from singers as s1
left join stickers as st1 on st1.receiver_id=s1.id and st1.user_id != s1.id
left join singers as s2 on s2.id=st1.user_id
left join singers as s_tenor on s_tenor.id=st1.user_id and s_tenor.voicepart = 'tenor'
left join singers as s_lead on s_lead.id=st1.user_id and s_lead.voicepart = 'lead'
left join singers as s_bari on s_bari.id=st1.user_id and s_bari.voicepart = 'baritone'
left join singers as s_bass on s_bass.id=st1.user_id and s_bass.voicepart = 'bass'
group by s1.id
order by s1.name ASC""")
singers = cur.fetchall()

print("---------------------------------------------------------------------------")
print("              TRAMP STATS")
print("---------------------------------------------------------------------------")

for singer in singers:
  s_name = singer[0]
  s_voicepart = singer[1]
  s_code = singer[2]
  s_rec_count = singer[3]
  s_rec_count_tenor = singer[4]
  s_rec_count_lead = singer[5]
  s_rec_count_bari = singer[6]
  s_rec_count_bass = singer[7]
  s_missing = singer[8]
  s_missing_stramp = singer[9]

  color = "black"

  if (s_voicepart == 'tenor' and s_rec_count_lead == v_count['lead'] and s_rec_count_bari == v_count['baritone'] and s_rec_count_bass == v_count['bass']) or \
     (s_voicepart == 'lead' and s_rec_count_tenor == v_count['tenor'] and s_rec_count_bari == v_count['baritone'] and s_rec_count_bass == v_count['bass']) or \
     (s_voicepart == 'baritone' and s_rec_count_tenor == v_count['tenor'] and s_rec_count_lead == v_count['lead'] and s_rec_count_bass == v_count['bass']) or \
     (s_voicepart == 'bass' and s_rec_count_tenor == v_count['tenor'] and s_rec_count_lead == v_count['lead'] and s_rec_count_bari == v_count['baritone']):
    tramp = True
    color = "light_blue"
  else:
    tramp = False

  if s_missing_stramp == None:
    supertramp = True
    color = "red"
  else:
    supertramp = False


  print(colored(f'''{s_name:<30} {s_voicepart:<20} {s_rec_count_tenor}/{v_count['tenor']} {s_rec_count_lead}/{v_count['lead']} {s_rec_count_bari}/{v_count['baritone']} {s_rec_count_bass}/{v_count['bass']}    {s_code}''', color, no_color = not tramp))

if (len(sys.argv) > 1 and sys.argv[1] == "--verbose"):
  print("\n\n============================\n\n")
  for singer in singers:
    s_name = singer[0]
    s_missing_stramp = singer[9]

    print(f'''{s_name}: {s_missing_stramp}''')

db.close()

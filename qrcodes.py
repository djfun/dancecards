#!/usr/bin/python3
import os.path
import random
import sqlite3
import sys
import string
import time
import qrcode

RALLY = 'NEHB 2023'
RALLYSITE = 'https://xqhb.ddns.net'

DATABASE = '/home/ubuntu/nehb2023/dancecards/dancecards.db'

db = sqlite3.connect(DATABASE)
cur = db.cursor()


cur.execute("SELECT name, email, voicepart, code, partnum, location \
from singers order by id")

singers = cur.fetchall()


#print("              All singers")
print(f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{RALLY} QR codes</title><style>@media print {{ tr {{ break-inside: avoid; }} }}</style></head><body>''')

print('<table>')

row = 0

boilerplate = "Use the link or the QR code below to access your dancecard. Please do NOT share this link with others!"

for singer in singers:
  row = row + 1
  if ((row % 2) == 1):
    print('<tr>')

  s_name = singer[0]
  s_email = singer[1]
  s_voicepart = singer[2]
  s_code = singer[3]
  s_partnum = singer[4]
  s_fullname = singer[5]

# dancecards.europeanharmonybrigade.org
#  print(f'''{s_name:<30} {s_email:<40} {s_voicepart:<20} https://nehb-demo.hopto.org/card/{s_code}''')
#  uri = "https://nehb-demo.hopto.org/card/" + s_code
  uri = RALLYSITE + "/card/" + s_code
  qrimage_name = 'qrcode-'+s_code+'.png'
  print('<td style="width: 100mm; max-width: 101mm; min-width: 99mm;">')
  print(f'''<b>{s_name} ({s_voicepart})</b> <i>{s_fullname}</i><br>{boilerplate}<br><b>{uri}</b><br><img src="{qrimage_name}">''')
  print('</td>')
  qr = qrcode.QRCode(
    version=1,
    box_size=5,
    border=5)

  qr.add_data(uri)
  qr.make(fit=True)

  img = qr.make_image(fill='black', back_color='white')
  img.save(qrimage_name)

  if ((row % 2) == 0):
    print('</tr>')

print('</table>')

print('</body></html>')

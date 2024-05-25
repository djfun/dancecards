#!/usr/bin/python3
import os.path
import random
import sqlite3
import sys
import string
import time
import qrcode
from slugify import slugify
from config import *

db = sqlite3.connect(DATABASE)
cur = db.cursor()


cur.execute("SELECT name, email, voicepart, code, partnum, location \
from singers order by id")

singers = cur.fetchall()

for singer in singers:
  s_name = singer[0]
  s_email = singer[1]
  s_voicepart = singer[2]
  s_code = singer[3]
  s_partnum = singer[4]
  s_fullname = singer[5]

  uri = RALLYSITE + "/card/" + s_code
  qrimage_name = 'qrcode-' + slugify(s_name)+ '.png'
  qr = qrcode.QRCode(
    version=1,
    box_size=5,
    border=5)

  qr.add_data(uri)
  qr.make(fit=True)

  img = qr.make_image(fill='black', back_color='white')
  img.save(qrimage_name)

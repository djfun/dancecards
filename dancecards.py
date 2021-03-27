import json
import sqlite3
from flask import Flask, g
from flask_socketio import SocketIO, emit, join_room
import time

app = Flask(__name__)
app.config['DEBUG'] = True
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

DATABASE = './dancecards.db'
TITLE = 'EHB 2021 - Quartet Tramp Dance Card'

def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  return db


@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()

def renderList(singers, voicepart):
  rlist = ""
  for singer in singers:
    s_id = singer[0]
    s_name = singer[1]
    s_location = singer[2]
    s_email = singer[3]
    s_voicepart = singer[4]
    s_filled = singer[5]
    s_sent = singer[6]
    if s_voicepart == voicepart:
      rlist = rlist + f'''<div id="user{s_id}" class="namebox '''
      if s_filled:
        rlist = rlist + "filled "
      else:
        rlist = rlist + "empty "
      if s_sent:
        rlist = rlist + "sent "
      else:
        rlist = rlist + "ready "
      rlist = rlist + f'''"><span class="name">{s_name}</span>'''
      if s_sent:
        rlist = rlist + f'''<div class="image" title="You already sent a sticker to {s_name}."></div>'''
      if s_filled:
        rlist = rlist + f'''<span class="address">{s_location}<br />{s_email}</span>'''
      rlist = rlist + "</div>"
  return rlist

@app.route('/')
def root():
  return ""

@app.route('/card/<code>')
def displayCard(code):
  cur = get_db().cursor()

  cur.execute("SELECT singers.id,singers.name from singers where singers.code=?", (code,))
  currentUser = cur.fetchone()

  if not currentUser:
    return "invalid code"

  username = currentUser[1]
  user_id = currentUser[0]
  cur.execute("SELECT distinct singers.id,singers.name,singers.location,singers.email,singers.voicepart, \
case when stickers.id != '' then 1 else 0 end as filled, \
case when back.id != '' then 1 else 0 end as sent \
from singers \
left join stickers \
on stickers.receiver_id=? and stickers.user_id=singers.id \
left join stickers as back \
on back.receiver_id=singers.id and back.user_id=?", (user_id,user_id))
  singers = cur.fetchall()
  tenorlist = renderList(singers, "tenor")
  leadlist = renderList(singers, "lead")
  baritonelist = renderList(singers, "baritone")
  basslist = renderList(singers, "bass")

  return f'''<html>
<head>
  <title>{TITLE}</title>
  <meta name="viewport" content="width=device-width, maximum-scale=1.0" />
  <meta charset="utf-8">
  <link rel="stylesheet" type="text/css" href="/static/style.css" />
</head>
<body>
  <h1>{TITLE}</h1>
  <h2><span>{username}</span></h2>
  <div id="infos"></div>
  <div class="tenor">
    <h3>Tenor:</h3>
    {tenorlist}
  </div>
  <div class="lead">
    <h3>Lead:</h3>
    {leadlist}
  </div>
  <div class="baritone">
    <h3>Baritone:</h3>
    {baritonelist}
  </div>
  <div class="bass">
    <h3>Bass:</h3>
    {basslist}
  </div>
  <div id="cover" class="cover hidden"><div class="popup"><div id="popup-message"></div><button id="popup-confirm" class="confirm" value="yes">Yes</button><button id="popup-deny" class="deny" value="no">No</button></div></div>
  <script src="/static/socket.io/socket.io.js"></script>
  <script src="/static/dancecards.js"></script>
</body>
</html>'''


def update_node(user_id, node_user_id, code):
  cur = get_db().cursor()
  cur.execute("SELECT singers.id,singers.name,singers.location,singers.email,singers.voicepart, \
case when stickers.id != '' then 1 else 0 end as filled, \
case when back.id != '' then 1 else 0 end as sent \
from singers \
left join stickers \
on stickers.receiver_id=? and stickers.user_id=singers.id \
left join stickers as back \
on back.receiver_id=singers.id and back.user_id=? \
where singers.id=?", (user_id,user_id,node_user_id))
  singers = cur.fetchall()
  emit("updateNode", {"nodeid": "user" + str(node_user_id), "html": renderList(singers, singers[0][4])}, room=code)

@socketio.on('connect')
def test_connect():
  emit('message', {'data': 'Connected'})

@socketio.on('join')
def handle_join(code):
  join_room(code)

@socketio.on('click')
def handle_click(userstring, code):
  receiver_id = userstring[4:]

  cur = get_db().cursor()

  cur.execute("SELECT singers.id,singers.name from singers where singers.code=?", (code,))
  currentUser = cur.fetchone()

  if not currentUser:
    return "invalid code"

  cur.execute("SELECT singers.id,singers.name,singers.code from singers where singers.id=?", (receiver_id,))
  receiverUser = cur.fetchone()

  if not receiverUser:
    return "invalid userstring"

  cur.execute("SELECT id from stickers where user_id=? and receiver_id=?", (currentUser[0], receiverUser[0]))
  if len(cur.fetchall()) > 0:
    return "sticker transaction already exists"

  # save sticker transaction to database
  cur.execute("INSERT into stickers(user_id, receiver_id, time) values (?, ?, ?)", (currentUser[0], receiverUser[0], int(time.time())))
  get_db().commit()

  timestring = time.strftime("%d.%m.%Y %H:%M:%S")
  print(f"[{timestring}] {receiverUser[1]} received a sticker from {currentUser[1]}")
  # and notify receiver to update his dancecard
  emit("stickerReceived", currentUser[1], room=receiverUser[2])
  update_node(currentUser[0], receiverUser[0], code)
  update_node(receiverUser[0], currentUser[0], receiverUser[2])

if __name__ == '__main__':
  socketio.run(app, host="::")
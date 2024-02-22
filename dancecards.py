import os
import json
import sqlite3
from flask import Flask, flash, g, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import time

UPLOAD_FOLDER = './static/pix' # Simplicity

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

socketio.init_app(app, cors_allowed_origins="*")

DATABASE = './dancecards.db'

RALLY = 'UKHB'
RALLYYEAR = '2024'
RALLYWYEAR = f'''{RALLY} {RALLYYEAR}'''

RALLYSITE = ''
APP_ADMIN = 'Del'

# RALLYSPIN = 'https://spinthewheel.app/J8kjENMCAt'
# RALLYSPIN = 'https://spinthewheel.app/Y4AEhvXJnX' # Added song numbers for preparedness checkers to use
#  <li><a href="{RALLYSPIN}" target="_blank" rel="noopener noreferrer">Spin the Wheel</a> <i>(opens in a new tab)</i> This is a song randomizer many have used in the past. It is an app that has no association with our rally and will include ads. Use at your own risk.</li>

TITLE = f'{RALLYWYEAR} Quartet Tramp Dance Card'

RALLYSCHEDULE= '/static/schedule.html'

FAQ = f'''
<ul>
  <li><a href="{RALLYSCHEDULE}" target="_blank" rel="noopener noreferrer">{RALLYWYEAR} Schedule</a> <i>(opens in a new tab)</i></li>
  <li>When in doubt, refresh the page, either by tapping/clicking on "{TITLE}" at the top of the page or using your browser's refresh feature</li>
  <li>Using the venue's WiFi is usually more reliable than your cell carrier's network</li>
  <li>A "Quartet Tramp" is a person who sings one or more of the <i>current</i> Rally's official songs with everyone at the Rally who has a <i>different</i> voice part</li>
  <li>A "Quartet Super Tramp" is a Quartet Tramp who <i>also</i> sings with <i>everyone of their voice part</i></li>
  <li>This app is how you keep track and earn the appropriate award</li>
  <li>Tap/Click on a person's name to see their contact info and/or send them a sticker after you sing with them</li>
  <li>A checkmark in the upper-right corner of a name box means you sent them a sticker</li>
  <li>A pulsing name box means the person sent you a sticker and is waiting for yours - click on the box and send them their sticker!</li>
  <li>Collapse a whole voicepart by tapping/clicking on the triangle or text</li>
  <li>Your voicepart section is collapsed by default unless you are trying for Quartet Super Tramp</li>
  <li>Your voicepart section will expand if someone is going for ST and you haven't sung with them yet</li>
  <li>A voicepart section will will collapse if you have sung with everyone in that part (congrats!)</li>
  <li>Tap/Click on your name at the top of the page to:
    <ul>
      <li>change or add your picture</li>
      <li>indicate whether or not you are trying to be a Quartet Super Tramp; by default you aren't</li>
    </ul>
  </li>
  <li>"I sang with everyone, but I'm not a Super Tramp?"
    <ul>
      <li>Go to your name at the top of the page (see above) and indicate you are trying to be a Super Tramp</li>
      <li>Make sure none of your boxes are pulsing; if so, send those folk a sticker</li>
      <li>Make sure all your checked folk also have a filled in background; if not, try to find those folk and have them send you a sticker</li>
    </ul>
  </li>
  <li>"I heard <i>insert name</i> left the rally early; what happens?" In most cases we will mark the person as optional on the dancecard; please be patient and keep singing!</li>
  <li>This "app" will work on your phone, tablet, laptop, or wherever there's a decent internet browser</li>
  <li>Use your phone or tablet's "Add to Home Screen" option to make it easy to open</li>
  <li>Still stumped? Find {APP_ADMIN}, who will help you <i>after</i> you sing together...</li>
  <li><a href="{RALLYSITE}/static/credits.html" target="_blank" rel="noopener noreferrer">Credits/About</a> <i>(opens in a new tab)</i></li>
</ul>
'''

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def renderList(singers, voicepart, cursinger):
  """
  :rtype val1: string, HTML of rendered list
  :rtype val2: int, number of parts with neither sent nor received stickers, excluding current singer
  :rtype val3: int, number of parts with no sent supertramp stickers (?)
  """
  rlist = ""
  rtosing = 0

  cur_id = 0 # defaults
  cur_voice = ""
  cur_stramp = 0

  if cursinger is not None: # Careful: fields in cursinger aren't 1:1 with entries in singers.
    cur_id = cursinger[0]
    cur_voicepart = cursinger[3]
    cur_stramp = cursinger[4]

  for singer in singers:
    #app.logger.info('Got singer: %s', singer)
    s_id = singer[0]
    s_prefname = singer[1]
    s_name = singer[2]
    s_location = singer[3]
    s_email = singer[4]
    s_voicepart = singer[5]
    s_partnum = singer[6] # what is displayed on the badge for checker process at some brigades
    s_phone = singer[7]
    s_photo = singer[8]
    s_supertramp = singer[9]
    s_asleep = singer[10]
    s_left = singer[11]
    s_optional = singer[12]
    # These fields come from the join on the stickers table:
    s_filled = singer[13]
    s_sent = singer[14]

    if s_voicepart == voicepart:
      # Don't include current singer in the count, or folk we've already sung with.
      if cursinger is not None:
          if cur_id != s_id:
              if ((s_filled == 0 or s_sent == 0) and
                  ((s_voicepart != cur_voicepart) or
                   (s_supertramp != 0) or
                   (cur_stramp != 0 and s_voicepart == cur_voicepart))):
                  rtosing = rtosing + 1

      rlist = rlist + f'''<div id="user{s_id}" class="namebox '''

      if s_filled:
        rlist = rlist + "filled "
      else:
        rlist = rlist + "empty "
      if s_sent:
        rlist = rlist + "sent "
      else:
        rlist = rlist + "ready "
      if s_supertramp:
        rlist = rlist + "stramp "

      rlist = rlist + f'''"''' # Close the class list

      # Add a title to this div to make it more accessible to the sight-impaired:
      if s_sent and s_filled:
          div_title_text = f'''You and {s_prefname} sent each other a sticker!'''
          a_label_text = f'''You and {s_prefname} sent each other a sticker!'''
      elif s_sent and not s_filled:
          div_title_text = f'''You sent {s_prefname} a sticker; {s_prefname} hasn't responded'''
          a_label_text = f'''You sent {s_prefname} a sticker; {s_prefname} hasn't responded'''
      elif not s_sent and s_filled:
          div_title_text = f'''{s_prefname} sent you a sticker; you haven't responded'''
          a_label_text = f'''{s_prefname} sent you a sticker; you haven't responded'''
      else:
          div_title_text = f'''You and {s_prefname} haven't sung together yet'''
          a_label_text = f'''You and {s_prefname} haven't sung together yet'''

      div_title = 'title="' + div_title_text + '"'
      div_aria_label = 'aria-label="' + a_label_text + '"'

      rlist = rlist + div_title + div_aria_label + f'''>''' # Close the opening div

      # These must be in this order since the JavaScript current assumes they are thus.
      rlist = rlist + f'''<span class="name">{s_prefname}</span>''' #  ({s_partnum})
      rlist = rlist + f'''<span class="email hidden">{s_email}</span>'''
      rlist = rlist + f'''<span class="phone hidden">{s_phone}</span>'''
      rlist = rlist + f'''<span class="photo hidden">{RALLYSITE}/static/pix/{s_photo}.jpg</span>'''

      # These fields are for display vs. data passing.
      if s_filled:
        rlist = rlist + f'''<span class="address">{s_name}, {s_location}</span>'''
      else:
        rlist = rlist + f'''<span class="address">{s_name}</span>'''

      if s_sent:
        rlist = rlist + f'''<div class="image" title="You already sent a sticker to {s_name}."></div>'''

      if s_filled:
        rlist = rlist + f'''<br/><span class="email">{s_email}</span>'''
      else:
        rlist = rlist + f'''<br/><span class="address hidden">{s_location}</span>'''

      rlist = rlist + "</div>\n    "

  return rlist, rtosing

@app.route('/')
def root():
  return f'''<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>{RALLYWYEAR}</title></head><body>Harmony is for everyone!</body></html>'''

@app.route('/selfserve/<code>', methods=['GET', 'POST'])
def selfService(code):
  cur = get_db().cursor()

  cur.execute("SELECT singers.id,singers.prefname,singers.name,singers.location,singers.email,singers.voicepart,singers.partnum,singers.phone,singers.photo,singers.supertramp from singers where singers.code=?", (code,))
  singer = cur.fetchone()

  if not singer:
    return "invalid code" # ToDo: Improve error handling.

  s_id = singer[0]
  s_prefname = singer[1]
  s_name = singer[2]
  s_location = singer[3]
  s_email = singer[4]
  s_voicepart = singer[5]
  s_partnum = singer[6] # what is displayed on the badge for checker process at some brigades
  s_phone = singer[7]
  s_photo = singer[8]
  s_supertramp = singer[9]

  formMsg = "" # Nothing for now.

  if request.method == 'POST':
    # First look for non-file form options
    if request.form.get('supertramp'):
        s_supertramp = 1
        results = cur.execute("UPDATE singers set supertramp=1 where id=?", (s_id,))
        get_db().commit()
    else:
        s_supertramp = 0
        results = cur.execute("UPDATE singers set supertramp=0 where id=?", (s_id,))
        get_db().commit()

    # check if the post request has the file part
    if 'file' in request.files:
      file = request.files['file']
      # If the user does not select a file, the browser submits an
      # empty file without a filename.
      if file.filename == '':
        formMsg = formMsg + " No (new) file selected"
      else:
        if file and allowed_file(file.filename):
          # We won't save the file with the user-supplied filename; we'll use our own "safe" name!
          filename = f'''{s_photo}.jpg''' # secure_filename(file.filename)
          tmpfilename = os.path.join(app.config['UPLOAD_FOLDER'], f'''{filename}.tmp''')
          file.save(tmpfilename)
          file.close()
          image = Image.open(tmpfilename)
          if image is None:
            formMsg = "Image.open failed: {tmpfilename}"
          else:
            image.load()
            imgsz = image.size

            imgSize = 512, 512
            image.thumbnail(imgSize, Image.Resampling.LANCZOS) # was Image.ANTIALIAS (now deprecated)
            if image is None:
              formMsg = f'''Image.thumbnail failed for {imgsz} to {imgSize}'''
            else:
              ImageOps.exif_transpose(image, in_place=True) # Update in place. ToDo: Check for error.
              image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
              formMsg = "New picture saved."

          if os.path.isfile(tmpfilename):
            os.remove(tmpfilename)

  # If not a POST, or after a POST, put up the form (again).
  stchecked = ""
  if s_supertramp != 0:
      stchecked = "checked"

  return f'''<!DOCTYPE html><html>
<head>
  <title>{TITLE} Self Service</title>
  <meta name="viewport" content="width=device-width, maximum-scale=1.0" />
  <meta charset="utf-8">
  <link rel="stylesheet" type="text/css" href="{RALLYSITE}/static/style.css" />
</head>
<body>
<img id="popup-image-a" height="256" src="{RALLYSITE}/static/pix/{s_photo}.jpg" onerror="this.src='{RALLYSITE}/static/pix/no_picture.jpg';" />
<br/>
<form method="post" enctype="multipart/form-data">
  <table>
  <tr><td><label for="self-picture">Tap/Click this to take/upload your picture:</label><br/><i>What it actually does is device and browser dependent...</i></td><td><input id="self-picture" type="file" value="New Picture" name="file" accept="image/*" /></td></tr>

  <tr><td><label for="self-st">Tick the box if you are going for Quartet Super Tramp:</label></td><td><input id="self-st" type="checkbox" name="supertramp" {stchecked} ></td></tr>
  <tr><td><label for="self-submit">Tap/Click to make changes:</label></td><td><input id="self-submit" type="submit" value="Upload/Save" /></td></tr>
  </table>
</form>
<br/>When you are done: <button value="done" onclick="window.location.href='{RALLYSITE}/card/{code}';">Back to your dancecard...</button>
<br/><span class="alert">{formMsg}</span>
</body>
</html>'''


@app.route('/card/<code>')
def displayCard(code):
  cur = get_db().cursor()

  cur.execute("SELECT singers.id,singers.prefname,singers.partnum,singers.voicepart,singers.supertramp from singers where singers.code=?", (code,))
  currentUser = cur.fetchone()

  if not currentUser:
    return "invalid code"

  username = currentUser[1]
  user_id = currentUser[0]
  partnum = currentUser[2]
  voicepart = currentUser[3]
  cur_super = currentUser[4]
  cur_super_string = ""

  cur.execute("SELECT distinct singers.id,singers.prefname,singers.name,singers.location,singers.email,singers.voicepart,singers.partnum,singers.phone,singers.photo,singers.supertramp,singers.asleep,singers.left,singers.opt, \
case when stickers.id != '' then 1 else 0 end as filled, \
case when back.id != '' then 1 else 0 end as sent \
from singers \
left join stickers \
on stickers.receiver_id=? and stickers.user_id=singers.id \
left join stickers as back \
on back.receiver_id=singers.id and back.user_id=? ORDER BY prefname, partnum", (user_id,user_id))

  tenoropen = ""
  leadopen = ""
  baritoneopen = ""
  bassopen = ""
  guestopen = ""

  singers = cur.fetchall()

  tenorlist = renderList(singers, "tenor", currentUser)
  if tenorlist[1] > 0:
      tenoropen = "open"
  leadlist = renderList(singers, "lead", currentUser)
  if leadlist[1] > 0:
      leadopen = "open"
  baritonelist = renderList(singers, "baritone", currentUser)
  if baritonelist[1] > 0:
      baritoneopen = "open"
  basslist = renderList(singers, "bass", currentUser)
  if basslist[1] > 0:
      bassopen = "open"

  guestlist = renderList(singers, "guest", currentUser)
  #  if basslist[1] > 0: # For now, guest list is always closed.
  #      bassopen = "open"

  # Ugly for now: Determine Tramp/SuperTramp status
  toSingList = {'tenor': tenorlist[1], 'lead': leadlist[1], 'baritone': baritonelist[1], 'bass': basslist[1]}
  trampToSingCount = 0
  supertrampToSingCount = 0
  for part, count in toSingList.items():
      if part != voicepart:
          trampToSingCount += count
      else:
          supertrampToSingCount = count

  if trampToSingCount == 0:
      cur_super_string = " TRAMP!"

  if cur_super == 1 and trampToSingCount == 0 and supertrampToSingCount == 0:
      cur_super_string = " SUPER TRAMP!"

# <h4> tags added in block below to aid in accessibility for the blind

  returnstring = f'''<!DOCTYPE html><html>
<head>
  <title>{TITLE}</title>
  <meta name="viewport" content="width=device-width, maximum-scale=1.0" />
  <meta charset="utf-8">
  <link rel="stylesheet" type="text/css" href="{RALLYSITE}/static/style.css" />
</head>
<body>
  <h1><a onClick="window.location.reload()">{TITLE}</a></h1>
  <h2><span class="selfservice {voicepart}"><a href="{RALLYSITE}/selfserve/{code}">{username}</a> ({voicepart}){cur_super_string}</span></h2>
    <h4>Notes</h4>
  <details>
  <summary>Notes/Help/FAQ <i>(tap/click to expand/collapse)</i></summary>
  {FAQ}
  </details>
  <div id="infos"></div>
    <h4>Tenor</h4>
  <details class="tenor" {tenoropen}>
    <summary>Tenor ({tenorlist[1]} to sing with):</summary>
    <div class="tenor">
    {tenorlist[0]}
    </div>
  </details>
    <h4>Lead</h4>
  <details class="lead" {leadopen}>
    <summary>Lead ({leadlist[1]} to sing with):</summary>
    <div class="lead">
    {leadlist[0]}
    </div>
  </details>
    <h4>Baritone</h4>
  <details class="baritone" {baritoneopen}>
    <summary>Baritone ({baritonelist[1]} to sing with):</summary>
    <div class="baritone">
    {baritonelist[0]}
    </div>
  </details>
    <h4>Bass</h4>
  <details class="bass" {bassopen}>
    <summary>Bass ({basslist[1]} to sing with):</summary>
    <div class="bass">
    {basslist[0]}
    </div>
  </details>'''

  if guestlist[0] != "" :
      returnstring += f'''<h4>Optional</h4><details class="guest" {guestopen}>
    <summary>Optional ({guestlist[1]} to sing with):</summary>
    <div class="guest">
    {guestlist[0]}
    </div>
  </details>'''

  returnstring += f'''<div id="cover" class="cover hidden"><div class="popup"><div id="popup-message-photo"><img id="popup-image-a" height="256" src="" onerror="this.src='{RALLYSITE}/static/pix/no_picture.jpg';" /></div><div id="popup-message-email" class="hidden"><a id="popup-email-a" href=""></a></div><div id="popup-message-phone" class="hidden"></div><div id="popup-message"></div><button id="popup-confirm" class="confirm" value="yes">Send</button><button id="popup-deny" class="deny" value="no">Cancel</button></div></div>
  <script src="{RALLYSITE}/static/socket.io/socket.io.js"></script>
  <script src="{RALLYSITE}/static/dancecards.js"></script>
</body>
</html>'''

  return returnstring

def update_node(user_id, node_user_id, code):
  cur = get_db().cursor()
  cur.execute("SELECT singers.id,singers.prefname,singers.name,singers.location,singers.email,singers.voicepart,singers.partnum,singers.phone,singers.photo,singers.supertramp,singers.asleep,singers.left,singers.opt, \
case when stickers.id != '' then 1 else 0 end as filled, \
case when back.id != '' then 1 else 0 end as sent \
from singers \
left join stickers \
on stickers.receiver_id=? and stickers.user_id=singers.id \
left join stickers as back \
on back.receiver_id=singers.id and back.user_id=? \
where singers.id=?", (user_id,user_id,node_user_id))
  singers = cur.fetchall()
  if singers is not None:
      renderedList = renderList(singers, singers[0][5], None)
      emit("updateNode", {"nodeid": "user" + str(node_user_id), "html": renderedList[0]}, room=code)
  else:
      printf(f'''update_node(): oops, singers didn't match for id {node_user_id}''')

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

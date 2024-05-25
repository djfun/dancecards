var socket = io();
var pathname = window.location.pathname;
var code = pathname.substring(6)
var targetID;
addEvents();

socket.emit("join", code);

socket.on("updateNode", data => {
  var element = document.getElementById(data.nodeid);
  element.outerHTML = data.html;
  addEvents();
});

socket.on("stickerReceived", data => {
  var element = document.getElementById("infos");
  var newDiv = document.createElement("div");
  newDiv.classList.add("infobox");
  newDiv.style.opacity = 1;
  var newContent = document.createTextNode("Sticker received from " + data);
  newDiv.appendChild(newContent);
  if (element.childNodes.length == 3) {
    element.removeChild(element.lastChild);
  }
  element.prepend(newDiv);
  window.setTimeout(function() {
    newDiv.style.opacity = 0;
  }, 2000);
  window.setTimeout(function() {
    newDiv.style.display = "none";
  }, 5000);

});

function handleClick(event) {
    targetID = event.currentTarget.id;

    hreftxt = event.currentTarget.querySelector(".email").innerText
    imgsrc = event.currentTarget.querySelector(".photo").innerText
    nametxt = event.currentTarget.querySelector(".name").innerText
    phonetxt = event.currentTarget.querySelector(".phone").innerText

    // document.getElementById("popup-message-phone").innerText = "Phone: " + phonetxt

    img = document.getElementById("popup-image-a")
    img.setAttribute('src', imgsrc)

    anchor = document.getElementById("popup-email-a")
    anchor.setAttribute('href', "mailto:"+ hreftxt)
    anchor.innerText = hreftxt

    document.getElementById("popup-confirm").classList.remove("hidden");
    document.getElementById("popup-message").innerText = "Do you want to send a sticker to " + nametxt + "?"
    document.getElementById("cover").classList.remove("hidden");
}

function handleInfoClick(event) {
    targetID = event.currentTarget.id;

    hreftxt = event.currentTarget.querySelector(".email").innerText
    imgsrc = event.currentTarget.querySelector(".photo").innerText
    nametxt = event.currentTarget.querySelector(".name").innerText
    phonetxt = event.currentTarget.querySelector(".phone").innerText

    // document.getElementById("popup-message-phone").innerText = "Phone: " + phonetxt

    document.getElementById("popup-confirm").classList.add("hidden");
    document.getElementById("popup-message").innerText = "You already sent a sticker to " + nametxt + "!"

    anchor = document.getElementById("popup-email-a")
    anchor.setAttribute('href', "mailto:"+ hreftxt)
    anchor.innerText = hreftxt

    img = document.getElementById("popup-image-a")
    img.setAttribute('src', imgsrc)

    document.getElementById("cover").classList.remove("hidden");
}

function confirmClick(event) {
  document.getElementById("cover").classList.add("hidden");
  socket.emit("click", targetID, code);
  targetID = null;
}

function denyClick(event) {
  document.getElementById("cover").classList.add("hidden");
  targetID = null;
}

function addEvents() {
  var elements = document.getElementsByClassName("namebox ready");

  for (let item of elements) {
    item.removeEventListener('click', handleClick);
    item.removeEventListener('click', handleInfoClick);
    item.addEventListener('click', handleClick);
  }

  var elements = document.getElementsByClassName("namebox sent");

  for (let item of elements) {
    item.removeEventListener('click', handleClick);
    item.removeEventListener('click', handleInfoClick);
    item.addEventListener('click', handleInfoClick);
  }
}

document.getElementById("popup-confirm").addEventListener('click', confirmClick);
document.getElementById("popup-deny").addEventListener('click', denyClick);

// Songlist tools; see https://stackoverflow.com/questions/57907979/javascript-shuffle-table-rows
function sortSongList() {
  //get the parent table for convenience
  let table = document.getElementById("songlist"); // ToDo: Fix hardcode

  //1. get all rows
  let rowsCollection = table.querySelectorAll("tr");

  //2. convert to array
  let rowsHeaders = Array.from(rowsCollection).slice(1,1);
  let rows = Array.from(rowsCollection).slice(1);

  //3. shuffle
  shuffleArray(rows);

  //4. add back to the DOM
//  for (const row of rowsHeaders) {
//    table.appendChild(row);
//  }
  for (const row of rows) {
    table.appendChild(row);
  }
}

function shuffleArray(array) {
  for (var i = array.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var temp = array[i];
    array[i] = array[j];
    array[j] = temp;
  }
}

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function compareValues(a, b) {
  // return -1/0/1 based on what you "know" a and b
  // are here. Numbers, text, some custom case-insensitive
  // and natural number ordering, etc. That's up to you.
  // A typical "do whatever JS would do" is:
    if (isNumeric(a) && isNumeric(b)) {return a - b}
    return (a<b) ? -1 : (a>b) ? 1 : 0;
}

function sortTable(colnum) {
  // get all the rows in this table:
  let table = document.getElementById("songlist"); // ToDo: Fix hardcode

  let rows = Array.from(table.querySelectorAll(`tr`));

  // but ignore the heading row:
  rows = rows.slice(1);

  // set up the queryselector for getting the indicated
  // column from a row, so we can compare using its value:
  let qs = `td:nth-child(${colnum})`;

  // and then just... sort the rows:
  rows.sort( (r1,r2) => {
    // get each row's relevant column
    let t1 = r1.querySelector(qs);
    let t2 = r2.querySelector(qs);

    // and then effect sorting by comparing their content:
    return compareValues(t1.textContent,t2.textContent);
  });

  // and then the magic part that makes the sorting appear on-page:
  rows.forEach(row => table.appendChild(row));
}

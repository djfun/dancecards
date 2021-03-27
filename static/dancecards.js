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
  document.getElementById("popup-message").innerText = "Do you want to send a sticker to " + event.currentTarget.firstChild.innerText + "?"
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
    item.addEventListener('click', handleClick);
  }
}

document.getElementById("popup-confirm").addEventListener('click', confirmClick);
document.getElementById("popup-deny").addEventListener('click', denyClick);

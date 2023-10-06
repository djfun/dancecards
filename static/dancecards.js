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
    document.getElementById("popup-confirm").classList.remove("hidden");
    document.getElementById("popup-message").innerText = "Do you want to send a sticker to " + event.currentTarget.firstChild.innerText + "?"

    /* Order of these must match order as output, with no spurious whitespace
     * "elements", at least until more logic is added to check for that. */
    nxtSib = event.currentTarget.firstChild.nextSibling
    nxtSib = nxtSib.nextSibling
    /* document.getElementById("popup-message-phone").innerText = "phone: " + nxtSib.innerText */

    nxtSib = nxtSib.nextSibling
    img = document.getElementById("popup-image-a")
    img.setAttribute('src', nxtSib.innerText)
    nxtSib = event.currentTarget.firstChild.nextSibling

    hreftxt = nxtSib.innerText
    anchor = document.getElementById("popup-email-a")
    anchor.setAttribute('href', "mailto:"+ hreftxt)
    anchor.innerText = hreftxt

    document.getElementById("cover").classList.remove("hidden");
}

function handleInfoClick(event) {
    targetID = event.currentTarget.id;
    document.getElementById("popup-confirm").classList.add("hidden");
    document.getElementById("popup-message").innerText = "You already sent a sticker to " + event.currentTarget.firstChild.innerText + "!"

    /* Order of these must match order as output, with no spurious whitespace
     * "elements", at least until more logic is added to check for that. */
    nxtSib = event.currentTarget.firstChild.nextSibling
    hreftxt = nxtSib.innerText
    anchor = document.getElementById("popup-email-a")
    anchor.setAttribute('href', "mailto:"+ hreftxt)
    anchor.innerText = hreftxt

    nxtSib = nxtSib.nextSibling
    /* document.getElementById("popup-message-phone").innerText = "phone: " + nxtSib.innerText */

    nxtSib = nxtSib.nextSibling
    img = document.getElementById("popup-image-a")
    img.setAttribute('src', nxtSib.innerText)

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

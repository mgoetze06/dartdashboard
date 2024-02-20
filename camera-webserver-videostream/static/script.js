var mouseX = 0;
var mouseY = 0;
const imgbox = document.querySelector(".imgbox");
imgbox.addEventListener("mousemove", updatePosition, false);

function updatePosition(event) {
    //pageX.innerText = event.pageX;
    mouseX = event.pageX;
    //pageY.innerText = event.pageY;
    mouseY = event.pageY;

}




function sendValue(valueID) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("console").innerHTML = this.responseText;
        }
    };
    var button = document.getElementById(valueID);
    var valueSlider = button.value;
    var urlCommand = window.location.href + "send/" + valueID + "-" + valueSlider;
    console.log(urlCommand);
    //var buttonName = document.getElementById("button" + buttonId);
    button.style.opacity = 0.5;
    button.disabled = true;
    xhttp.open("GET", urlCommand, true);
    xhttp.send();
    setTimeout(function () { button.style.opacity = 1; button.disabled = false; }, 150);
};

function getClickPosition(e) {
    var img = document.getElementById(e);
    var currentClickPosX = mouseX - img.offsetLeft;
    var currentClickPosY = mouseY - img.offsetTop;

    var currentWidth = img.width;
    var currentHeight = img.height;

    var naturalWidth = img.naturalWidth;
    var naturalHeight = img.naturalHeight;

    var naturalClickPosX = ((naturalWidth / currentWidth) * currentClickPosX).toFixed(0);
    var naturalClickPosY = ((naturalHeight / currentHeight) * currentClickPosY).toFixed(0);


    console.log("Current X: " + currentClickPosX + " Current Y: " + currentClickPosY +
        "\r\nNatural X: " + naturalClickPosX + " Natural Y: " + naturalClickPosY);


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("console").innerHTML = this.responseText;
        }
    };
    var urlCommand = window.location.href + "send/x" + naturalClickPosX + "-y" + naturalClickPosY;
    console.log(urlCommand);
    xhttp.open("GET", urlCommand, true);
    xhttp.send();
};
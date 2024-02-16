var socket = io();
    var double = false;
    var triple = false;
    var spieler = true;
    var counter = 1;
    var überworfen = false;
    var wurf_nr = 0;
    var type = "S";
    

    // When the user clicks the button, open the modal 
    function openModalMenu() {
        var modal = document.getElementById("myModal");
        modal.style.display = "block";

    }
      // When the user clicks the button, open the modal 
    function openModalWinner() {
        var modal = document.getElementById("winner");
        modal.style.display = "block";

    }
  
    // When the user clicks on <span> (x), close the modal
    function closeModal() {
        var modal = document.getElementById("myModal");
        modal.style.display = "none";
        modal = document.getElementById("winner");
        if (modal != null){
          modal.style.display = "none";

        }
    }
    
    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        var modal = document.getElementById("myModal");

      if (event.target == modal) {
        modal.style.display = "none";
      }

      //var modal = document.getElementById("winnerModal");
      //if (event.target == modal) {
      //  modal.style.display = "none";
      // }
    }
    socket.on('init_names', function(msg) {
      //$('#textBox').append('<p>Received: ' + msg.data + '</p>');
      document.getElementById('name1').value = msg.spieler1;
      document.getElementById('name2').value = msg.spieler2;

    });
    socket.on('spielstand_update', function(msg) {
      //$('#textBox').append('<p>Received: ' + msg.data + '</p>');
      document.getElementById('punkteSpieler1').value = msg.punktstand1;
      document.getElementById('punkteSpieler2').value = msg.punktstand2;

    });
    socket.on('wurf_historie', function(msg) {
      wurf_id = "wurf" + msg.spielerid + msg.wurfnummer;
      document.getElementById(wurf_id).value = msg.wert;
      if(msg.wert.startsWith("E")){
        document.getElementById(wurf_id).style.backgroundColor = "Red";
      }
    });

    socket.on('winner', function(msg) {
      //var modal = document.getElementById("winnerModal");
      //modal.style.display = "block";

      document.getElementById('Winner').value = msg.name;
      document.getElementById('WinnerAvg').value = msg.avg;
      document.getElementById('WinnerDarts').value = msg.darts;

      var id = "Spieler" + msg.winner;
      document.getElementsByClassName(id)[0].style.backgroundColor = "green";
      openModalWinner();


    });

    socket.on('spieler_wechsel', function(msg) {
      //$('#textBox').append('<p>Received: ' + msg.data + '</p>');
      if (msg.spieler == "Spieler1"){
        spieler = true;
        
        wurf_id_pre = "wurf1"
        var spielerindex = "0"
        document.getElementsByClassName("Spieler1")[0].style.backgroundColor = "#bfe0c4";
        document.getElementsByClassName("Spieler2")[0].style.backgroundColor = "#ecedef";
      }else{
        spieler = false;
        wurf_id_pre = "wurf2"
        var spielerindex = "1"
        document.getElementsByClassName("Spieler1")[0].style.backgroundColor = "#ecedef";
        document.getElementsByClassName("Spieler2")[0].style.backgroundColor = "#bfe0c4";
        }
        //socket.emit('spielerwechselZumESP', {data: spielerindex});
        for(var i = 1; i < 4; i++){
            wurf_id = wurf_id_pre + i
            document.getElementById(wurf_id).value = "";
            document.getElementById(wurf_id).style.backgroundColor = null;
        }
    });
    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });
    socket.on('avg', function(msg) {

        var id = "avgSpieler" + msg.spielerid;
        console.log(id);
        document.getElementById(id).value = msg.avg;

        id = "dartscount" + msg.spielerid;
        console.log(id);

        document.getElementById(id).value = msg.dartscount;


    });
    socket.on('visit_score', function(msg) {
        if(spieler){
          document.getElementById("visitscoreSpieler1").value = msg.visit_score;
        }else{
          document.getElementById("visitscoreSpieler2").value = msg.visit_score;

        }
    });

    function sendZurueck(){
      socket.emit('zurueck');
      closeModal();
    }

  function sendekorrektur(object,spielerkorrektur){
    var confirmtext = "Korrektur " + object.value + " für " + spielerkorrektur + " durchführen?"
    if (confirm(confirmtext) == true) {
      socket.emit('korrektur', {data: object.value, currentSpieler: spielerkorrektur});
    }
    
  }

function fordereSpielerwechsel(){
  socket.emit('fordereSpielerwechsel', {data: "wechsel"});

}

  function sendData(object){
    socket.emit('message', {data: 'I\'m connected!'});

  }

  function turnOffDoubleTriple(){
    document.getElementById("bull").disabled = false;
    document.getElementById("bull").style.backgroundColor = "#ecedef";

    document.getElementById("double").style.backgroundColor = "#ecedef";
    document.getElementById("triple").style.backgroundColor = "#ecedef";
    double = false;
    triple = false;
  }

  function toggleTriple(){
    triple = !triple;
    double = false;
    document.getElementById("bull").disabled = false;
    document.getElementById("bull").style.backgroundColor = "#ecedef";
    ColorsTripleDouble();
  }
  function toggleDouble(){
    double = !double;
    triple = false;
    ColorsTripleDouble();
  }

  function ColorsTripleDouble(){
    document.getElementById("double").style.backgroundColor = "#ecedef";
    document.getElementById("triple").style.backgroundColor = "#ecedef";
    document.getElementById("bull").disabled = false;
    document.getElementById("bull").style.backgroundColor = "#ecedef";


    if(double){
      document.getElementById("double").style.backgroundColor = "red";
    }
    if(triple){
      document.getElementById("triple").style.backgroundColor = "red";
      document.getElementById("bull").disabled = true;
      document.getElementById("bull").style.backgroundColor = "#3d3d3d";
    }

  }


  function sendWurf(object){

    var wert = object.value;
    type = "S";
    if(triple){
        type = "T";
    }else{
        if(double){
          type = "D";
        }
    }
    socket.emit('wurf', {wert: wert, type: type});
    turnOffDoubleTriple();
    //document.getElementById('sound1').play();
  }

  function noscore(){
    for(var i = (wurf_nr + 1); i < 4; i++){
      sendWurf(document.getElementById('zero'))
    }
  }

  function sendBroadcast(){
    //SPIEL STARTEN
    if (confirm("Spiel starten?") == true) {
        //text = "You pressed OK!";
      closeModal()
      counter++;
      socket.emit('init event', {data: counter});
      document.getElementsByClassName("Spieler1")[0].style.backgroundColor = "#bfe0c4";
      document.getElementsByClassName("Spieler2")[0].style.backgroundColor = "#ecedef";
      //document.getElementById('PunktEingabeFrei').value = "";
      for(var i = 1; i < 4; i++){
              wurf_id = "wurf1" + i;
              wurf_id2 = "wurf2" + i;
              document.getElementById(wurf_id).value = "";
              document.getElementById(wurf_id2).value = "";
      }
      document.getElementById("avgSpieler1").value = "";
      document.getElementById("avgSpieler2").value = "";
      document.getElementById("visitscoreSpieler1").value = "";
      document.getElementById("visitscoreSpieler2").value = "";
      document.getElementById("dartscount1").value = "";
      document.getElementById("dartscount2").value = "";
      document.getElementById("double").style.backgroundColor = "#ecedef";
      document.getElementById("triple").style.backgroundColor = "#ecedef";
      document.getElementById("bull").disabled = false;
      document.getElementById("bull").style.backgroundColor = "#ecedef";
    } else {
      //text = "You canceled!";
    }

  }
  function setColor(object){
    console.log("touch event");
    object.style.backgroundColor = "#3a2222";
    object.style.color = "red";
    //document.getElementById("bull").style.backgroundColor = "red";
  }
  function releaseColor(object){
    console.log("touch event released");
    object.style.backgroundColor = "#ecedef";
    object.style.color = "#235558";
    //document.getElementById("bull").style.backgroundColor = "red";
  }
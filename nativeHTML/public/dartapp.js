


var first = true;
//const db = new sqlite3.Database('./database/darts.sqlite');
var wurf_nr = 0;
    var punkteGesamtSpieler1 = 501;
    var punkteGesamtSpieler2 = 501;
    var würfeSpieler1 = 0;
    var würfeSpieler2 = 0;
    var spieler = true;
    //document.getElementById("debugWurfNr").value = wurf_nr;
    var double = false;
    var triple = false;
    var winner = false;
    var überworfen = false;





    function writeToDB(){
        //db.run('UPDATE dart_game
    }

    function calcWurfNr(object) {
       wurf_nr = wurf_nr + 1; 
       überworfen = false;
       document.getElementById("debugWurfNr").value = wurf_nr;

        var wert = object.value;
        if(triple){
            wert = wert * 3;
        }else{
            if(double){
                wert = wert * 2;
            }
        }
        
       if(spieler){
            var wurf_id = "wurf1" + wurf_nr;
            
            if(checkWinning(wert,double,punkteGesamtSpieler1)){
                document.getElementsByClassName("spieler1")[0].style.backgroundColor = "green";
                alert("Spieler1 gewinnt");
                winner = true;
                würfeSpieler1 += 1;
            }else{
                if(punkteGesamtSpieler1 - wert < 2){
                    überworfen = true;
                }else{
                    punkteGesamtSpieler1 -= wert;
                    würfeSpieler1 += 1;

                }
                winner = false;
            }
       }else{
        var wurf_id = "wurf2" + wurf_nr;
        
            if(checkWinning(wert,double,punkteGesamtSpieler2)){
                document.getElementsByClassName("spieler2")[0].style.backgroundColor = "green";
                alert("Spieler2 gewinnt");
                winner = true;
                würfeSpieler2 += 1;
            }else{
                if(punkteGesamtSpieler2 - wert < 2){
                    überworfen = true;
                }else{
                    punkteGesamtSpieler2 -= wert;
                    würfeSpieler2 += 1;
                }
                winner = false;
            }
       }
       
       document.getElementById("debugWurfNr").value = wurf_nr;

       document.getElementById(wurf_id).value = wert;
       if(überworfen){
        document.getElementById(wurf_id).style.color = "red";
       }else{
        writeAvg();
       }
       if(wurf_nr == 3 || überworfen){
        wurf_nr = 0;
        
        spieler = !spieler;
        oldvalues1 = [];
        oldvalues2 = [];
        for(var i = 1; i < 4; i++){
            if(spieler){
                var wurf_id = "wurf1" + i;
                oldvalues1.push(document.getElementById(wurf_id).value);
            }else{
                var wurf_id = "wurf2" + i;
                oldvalues2.push(document.getElementById(wurf_id).value);
            }
            //oldvalues.push(document.getElementById(wurf_id).value);
            document.getElementById(wurf_id).value = "";
        }
       }
       writePunktestand();
       writeAvg();
       if(winner == false){
            document.getElementById("bull").disabled = false;
                document.getElementById("bull").style.backgroundColor = "#ecedef";
            document.getElementById("debugSpieler").value = spieler;
            if(spieler){
                document.getElementsByClassName("spieler1")[0].style.backgroundColor = "#bfe0c4";
                document.getElementsByClassName("spieler2")[0].style.backgroundColor = "#ecedef";

            }else{
                document.getElementsByClassName("spieler2")[0].style.backgroundColor = "#bfe0c4";
                document.getElementsByClassName("spieler1")[0].style.backgroundColor = "#ecedef";
            }
            
            //writeBackgroundColor();
            double = false;
            triple = false;
            document.getElementById("double").style.backgroundColor = "#ecedef";
            document.getElementById("triple").style.backgroundColor = "#ecedef";
        }else{
            afterWinningDisableAllButtons();
        }
    }

    function checkWinning(wertWurf,doubleOut,restwert){
        document.getElementById("debug").value = restwert-wertWurf;
        if(restwert-wertWurf == 0 && doubleOut){
            console.log("gewonnen");
            return true;
        }else{
            console.log("nicht gewonnen");
            return false;
        }
    }

    function afterWinningDisableAllButtons(){
        var nodes = document.getElementById("calcu").getElementsByTagName('*');
        for(var i = 0; i < nodes.length; i++){
            nodes[i].disabled = true;
        }
    }
    function enableAllButtons(){
        var nodes = document.getElementById("calcu").getElementsByTagName('*');
        for(var i = 0; i < nodes.length; i++){
            nodes[i].disabled = false;
        }
    }

    function setDouble(){
        double = true;
        triple = false;
        document.getElementById("double").style.backgroundColor = "red";
        document.getElementById("triple").style.backgroundColor = "#ecedef";

    }
    function setTriple(){
        if(!triple){
            triple = true;
            double = false;
            document.getElementById("double").style.backgroundColor = "#ecedef";
            document.getElementById("triple").style.backgroundColor = "red";
            document.getElementById("bull").disabled = true;
            document.getElementById("bull").style.backgroundColor = "#3d3d3d";
        }else{
            triple = false;
            document.getElementById("double").style.backgroundColor = "#ecedef";
            document.getElementById("triple").style.backgroundColor = "#ecedef";
            document.getElementById("bull").disabled = false;
            document.getElementById("bull").style.backgroundColor = "#ecedef";
        }


    }

    function spielStarten(){
        enableAllButtons();
        wurf_nr = 0;
        punkteGesamtSpieler1 = 501;
        punkteGesamtSpieler2 = 501;
        würfeSpieler1 = 0;
        würfeSpieler2 = 0;
        wurf = [];
        spieler = true;
        document.getElementById("debugWurfNr").value = wurf_nr;
        double = false;
        triple = false;
        winner = false;
        überworfen = false;
        first = true;
        for(var i = 1; i < 4; i++){
            wurf_id = "wurf1" + i;
            wurf_id2 = "wurf2" + i;
            document.getElementById(wurf_id).value = "";
            document.getElementById(wurf_id2).value = "";
        }


        document.getElementById("punkteSpieler1").value = punkteGesamtSpieler1;
        document.getElementById("punkteSpieler2").value = punkteGesamtSpieler2;
        document.getElementsByClassName("spieler1")[0].style.backgroundColor = "#bfe0c4";
        document.getElementsByClassName("spieler2")[0].style.backgroundColor = "#ecedef";
        document.getElementById("avgSpieler1").value = "";
        document.getElementById("avgSpieler2").value = "";
        document.getElementById("double").style.backgroundColor = "#ecedef";
        document.getElementById("triple").style.backgroundColor = "#ecedef";
        document.getElementById("bull").disabled = false;
            document.getElementById("bull").style.backgroundColor = "#ecedef";
    }

    function writePunktestand(){
        document.getElementById("punkteSpieler1").value = punkteGesamtSpieler1;
        document.getElementById("punkteSpieler2").value = punkteGesamtSpieler2;

    }
    function writeBackgroundColor(){
        document.getElementsByClassName("spieler1")[0].style.backgroundColor = "#bfe0c4";
        document.getElementsByClassName("spieler2")[0].style.backgroundColor = "#ecedef";
      }

    function writeAvg(){
        if (würfeSpieler1 > 0){
            var avgSpieler1 = (501-punkteGesamtSpieler1)/würfeSpieler1;
            var num = Number(avgSpieler1) // The Number() only visualizes the type and is not needed
            var roundedString = num.toFixed(2);
            var rounded = Number(roundedString);
            document.getElementById("avgSpieler1").value = rounded;

        }else{
            document.getElementById("avgSpieler1").value = "";

        }
        if (würfeSpieler2 > 0){
            var avgSpieler2 = (501-punkteGesamtSpieler2)/würfeSpieler2;
            var num = Number(avgSpieler2) // The Number() only visualizes the type and is not needed
            var roundedString = num.toFixed(2);
            var rounded = Number(roundedString);
            document.getElementById("avgSpieler2").value = rounded;
        }else{
            document.getElementById("avgSpieler2").value = "";

        }
    }

    function writeOldValues(){
        for(var i = 1; i < 4; i++){
            if(spieler){
                wurf_id = "wurf1" + i;
                document.getElementById(wurf_id).value = Number(oldvalues[i]);
            }else{
                wurf_id = "wurf2" + i;
                document.getElementById(wurf_id).value = Number(oldvalues[i]);
            }
        }
    }

    function wurfZurück(){

        if(punkteGesamtSpieler1 == 501 && punkteGesamtSpieler2 == 501){
            spielStarten();
            return;
        }


        if(wurf_nr == 3 || wurf_nr == 0){
            //if würfeSpieler1 > 0 && würfeSpieler2 > 0
            spieler = !spieler;
        }
        if(wurf_nr == 0){
            wurf_nr = 3;
            //writeOldValues();

        }


        if(spieler){
            //spieler 1
            if(punkteGesamtSpieler1 == 501){
                
            }else{
                würfeSpieler1 -= 1;
                wurf_id = "wurf1" + wurf_nr;
                
                punkteGesamtSpieler1 += Number(document.getElementById(wurf_id).value);
            }


        }else{
            //spieler 2
            if(punkteGesamtSpieler2 == 501){
                
            }else{
                würfeSpieler2 -= 1;
                wurf_id = "wurf2" + wurf_nr;
                
                punkteGesamtSpieler2 += Number(document.getElementById(wurf_id).value);
            }
        }
        wurf_nr -= 1;
        document.getElementById("debugWurfNr").value = wurf_nr;
        document.getElementById(wurf_id).value = "";
        writePunktestand();
        writeAvg();
        if(spieler){
                document.getElementsByClassName("spieler1")[0].style.backgroundColor = "#bfe0c4";
                document.getElementsByClassName("spieler2")[0].style.backgroundColor = "#ecedef";

            }else{
                document.getElementsByClassName("spieler2")[0].style.backgroundColor = "#bfe0c4";
                document.getElementsByClassName("spieler1")[0].style.backgroundColor = "#ecedef";
            }
    }

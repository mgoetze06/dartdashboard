from flask import Flask, render_template
from flask_socketio import SocketIO, emit
#!/usr/bin/python
import sqlite3
import os,sys
import requests
import json

url = "http://192.168.0.214/update"
data = {'punkte0': '501', 'punkte1': '501', 'spieler': '0'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

spieler = "Spieler1"

file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
database_path = os.path.join(file_path,"database\\darts.db")
#connection = sqlite3.connect("C:\\projects\\DartDashboard\\nativeHTML\\clientserver\\database\\darts.db")
connection = sqlite3.connect(database_path)

cursor = connection.cursor()

cursor.execute("SELECT MAX(game_id) FROM dartgame")
game_id = cursor.fetchone()[0]
print("GameID: ",game_id)
app = Flask(__name__)
#            static_url_path='',
#            static_folder='/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def UpdateSpielstand():
    global database_path
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    alle_spieler = ["Spieler1","Spieler2"]
    punktstände = []
    for spieler in alle_spieler:
        cursor.execute("select punkte from dartgame where spieler = '"+spieler+"'")
        wert = cursor.fetchone()[0]
        punktstände.append(wert)
    if str(punktstände[0]) == '501' and str(punktstände[1]) == '501':
        initGame()
        return
    #send spielstand to all connected websockets
    emit('spielstand_update', {'punktstand1': punktstände[0],'punktstand2': punktstände[1]}, broadcast=True)
    connection.close()

    #send spielstand to esp displays
    if spieler == "Spieler1":
        spielerindex = '0'
    else: 
        if spieler == "Spieler2":
            spielerindex = '1'
    global url,headers
    data = {'punkte0': str(punktstände[0]), 'punkte1': str(punktstände[1]), 'spieler': spielerindex}
    try:
        requests.post(url, data=json.dumps(data), headers=headers,timeout=0.5)
    except requests.Timeout:
        pass

    if str(punktstände[0]) == '501' and str(punktstände[1]) == '501':
        initGame()


def WurflisteZuEinzelnenWürfen(wurfliste,ignoreSpielerwechsel):
    global spieler
    print("WurflisteZuEinzelnenWürfen: ")
    print(spieler)
    print(wurfliste)
    rest = len(wurfliste) % 3
    print("rest: ",rest)
    print("wurfliste[-1]: ",wurfliste[-1])
    if rest == 0:
        #emit('wurf_historie',{'wurfnummer': '3', 'wert': str(data["data"])}, broadcast=True)
        emit('wurf_historie',{'wurfnummer': '1', 'wert': str(wurfliste[-3])}, broadcast=True)
        emit('wurf_historie',{'wurfnummer': '2', 'wert': str(wurfliste[-2])}, broadcast=True)
        emit('wurf_historie',{'wurfnummer': '3', 'wert': str(wurfliste[-1])}, broadcast=True)
        print(wurfliste[-3:])
        if not ignoreSpielerwechsel:
            print("Spielerwechsel")

            if spieler == "Spieler1":
                emit('spieler_wechsel', {'spieler': 'Spieler2'}, broadcast=True)
            if spieler == "Spieler2":
                emit('spieler_wechsel', {'spieler': 'Spieler1'}, broadcast=True)
        return True
    if rest == 1:
        #emit('wurf_historie',{'wurfnummer': '1', 'wert': str(data["data"])}, broadcast=True)
        emit('wurf_historie',{'wurfnummer': '1', 'wert': str(wurfliste[-1])}, broadcast=True)
        return False
    if rest == 2:
        #emit('wurf_historie',{'wurfnummer': '2', 'wert': str(data["data"])}, broadcast=True)
        emit('wurf_historie',{'wurfnummer': '1', 'wert': str(wurfliste[-2])}, broadcast=True)
        emit('wurf_historie',{'wurfnummer': '2', 'wert': str(wurfliste[-1])}, broadcast=True)
        return False


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    print('received message:')
    print(data["data"])

@socketio.on('zurueck')
def handle_message():
    global database_path,spieler
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("select wurfliste from dartgame where spieler = '"+spieler+"'")
    wurfliste = cursor.fetchone()[0].split(";")
    if wurfliste[0] =="":
        wurfliste = wurfliste[1:]
    WurflisteZuEinzelnenWürfen(["","",""],True)
    rest = len(wurfliste) % 3
    if rest == 0:
        if spieler == "Spieler1":
            spieler = "Spieler2"
            emit('spieler_wechsel', {'spieler': 'Spieler2'}, broadcast=True)
        if spieler == "Spieler2":
            spieler = "Spieler1"
            emit('spieler_wechsel', {'spieler': 'Spieler1'}, broadcast=True)
        cursor.execute("select wurfliste from dartgame where spieler = '"+spieler+"'")
        wurfliste = cursor.fetchone()[0].split(";")
        if wurfliste[0] =="":
            wurfliste = wurfliste[1:]

        
        #WurflisteZuEinzelnenWürfen(wurfliste,True)
    print("zurück:")
    print(wurfliste)
    print(wurfliste[:-1])

    cursor.execute("select punkte from dartgame where spieler = '"+spieler+"'")
    if len(wurfliste) > 0:
        punktstand = cursor.fetchone()[0] + int(wurfliste[-1])
    else:
        punktstand = "501"
    query = "UPDATE dartgame SET punkte =  " + str(punktstand)  + " WHERE spieler = '"+ spieler + "' ;"
    print(query)
    cursor.execute(query)
    if len(wurfliste) > 2:
        wurfliste = wurfliste[:-1]
    else:
        if len(wurfliste) > 1:
            wurfliste = wurfliste[0:1]
        else:
            #if len(wurfliste) > 0:
            #    wurfliste = wurfliste[0]
            #else:
            wurfliste = [""]
    stringToWrite = ";".join(wurfliste)
    query = "UPDATE dartgame SET wurfliste =  '" + str(stringToWrite)  + "' WHERE spieler = '"+ spieler + "' ;"
    print(query)
    cursor.execute(query)
    connection.commit()
    if wurfliste==[""]:
        wurfliste = ["","",""]
    wechsel = WurflisteZuEinzelnenWürfen(wurfliste,False)
    if wechsel:
        cursor.execute("select wurfliste from dartgame where spieler = '"+spieler+"'")
        wurfliste = cursor.fetchone()[0].split(";")
        if wurfliste[0] =="":
            wurfliste = wurfliste[1:]
        WurflisteZuEinzelnenWürfen(wurfliste,True)
    UpdateSpielstand()

@socketio.on('wurf')
def handle_message(data):
    global database_path,spieler
    print('received message:')
    print(data["data"])
    print(data["currentSpieler"])
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    spieler = data["currentSpieler"] #"Spieler1"  # TODO MUSS VARIABEL SEIN

    cursor.execute("select punkte from dartgame where spieler = '"+spieler+"'")
    punktstand = cursor.fetchone()[0] - int(data["data"])
    query = "UPDATE dartgame SET punkte =  " + str(punktstand)  + " WHERE spieler = '"+ spieler + "' ;"
    print("neue Punktzahl: ",str(punktstand))
    cursor.execute(query)
    cursor.execute("select wurfliste from dartgame where spieler = '"+spieler+"'")
    wert = cursor.fetchone()[0] + ";" + str(data["data"])
    query = "UPDATE dartgame SET wurfliste =  '" + str(wert)  + "' WHERE spieler = '"+ spieler + "' ;"
    cursor.execute(query)
    connection.commit()

    wurfliste = wert.split(";")[1:]

    print("Wurfliste: ",wurfliste)

    avg = round((501-punktstand)/len(wurfliste),2)
    emit('avg',{'avg': str(avg)}, broadcast=True)

    WurflisteZuEinzelnenWürfen(wurfliste,False)

    UpdateSpielstand()



@socketio.on('init event')
def test_message(message):
    initGame()

def initGame():
    global database_path
    connection = sqlite3.connect(database_path)
    emit('spieler_wechsel', {'spieler': 'Spieler1'}, broadcast=True)
    cursor = connection.cursor()
    print("initialisiere Spiel")
    alle_spieler = ["Spieler1","Spieler2"]
    for spieler in alle_spieler:
        query = "UPDATE dartgame SET punkte = 501 WHERE spieler = '"+ spieler + "' ;"
        print(query)
        cursor.execute(query)
        query = "UPDATE dartgame SET wurfliste = '' WHERE spieler = '"+ spieler + "' ;"
        print(query)
        cursor.execute(query)
    connection.commit()
    emit('spielstand_update', {'punktstand1': 501,'punktstand2': 501}, broadcast=True)
    connection.close()

    global url,headers
    data = {'punkte0': '501', 'punkte1': '501', 'spieler': '0'}
    try:
        requests.post(url, data=json.dumps(data), headers=headers,timeout=0.5)
    except requests.Timeout:
        pass

if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0")
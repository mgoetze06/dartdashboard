from flask import Flask, render_template
from flask_socketio import SocketIO, emit
#!/usr/bin/python
import sqlite3
import os,sys
import requests
import json, datetime

url = "http://192.168.0.214/update"
data = {'punkte0': '501', 'punkte1': '501', 'spieler': '0'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

spieler = "Spieler1"

last_committed_punktstand1 = 501
last_committed_punktstand2 = 501

file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
database_path = os.path.join(file_path,"database")
database_path = os.path.join(database_path,"darts.db")

#connection = sqlite3.connect("C:\\projects\\DartDashboard\\nativeHTML\\clientserver\\database\\darts.db")
connection = sqlite3.connect(database_path)

cursor = connection.cursor()

cursor.execute("SELECT MAX(Game_ID) FROM dartgame_header")
game_id = cursor.fetchone()[0]
if game_id == None:
    game_id = 1
else:
    game_id = int(game_id) + 1
print("GameID: ",game_id)

time = str(datetime.datetime.now())

query = "INSERT INTO dartgame_header ('Game_ID','Typ','Typ_Punktstand','Spieler1_ID','Spieler2_ID','Spieler1_Name','Spieler2_Name','Ergebnis','Startzeit')"
query = query +  "VALUES ("+ str(game_id) + ",'DoubleOut',501,1,2,'Lini','Rici','läuft','" + time + "')"


cursor.execute(query)

connection.commit()


app = Flask(__name__)
#            static_url_path='',
#            static_folder='/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


def andereID(currentID):

    cursor.execute("select Spieler1_ID,Spieler2_ID from dartgame_header where Game_ID = " + str(game_id))
    row = cursor.fetchone()
    id1 = row[0]
    id2 = row[1]

    if id1 == currentID:
        return id2
    else:
        return id1
    


def ErmittleSpielerID():
    cursor.execute("select MAX(Wurf_Nummer_Gesamt),Spieler_ID from dartgame_details where Game_ID = " + str(game_id))
    row = cursor.fetchone()
    Max_Wurf_Nummer_Gesamt = int(row[0])
    currentID = row[1]
    
    rest  = Max_Wurf_Nummer_Gesamt % 3
    if rest > 0:
        ID = currentID
    else:
        ID = andereID(currentID)


    return ID

def ErmittleAufnahme(id):
    cursor.execute("select MAX(Wurf_Nummer)from dartgame_details where Spieler_ID = '" + id + "' and Game_ID = " + str(game_id))
    nr = cursor.fetchone()[0]
    if nr == None:
        nr = 1
    else:
        nr = int(game_id) + 1
    return nr

def ErmittleWurfNummer(id):
    cursor.execute("select MAX(Wurf_Nummer)from dartgame_details where Spieler_ID = '" + id + "' and Game_ID = " + str(game_id))
    nr = cursor.fetchone()[0]
    if nr == None:
        nr = 1
    else:
        nr = int(game_id) + 1
    return nr



def InsertWurf():
    print()
    print("### ---- Neuer Wurf! ---- ###")

    print("ermittle Spieler ID")
    spieler_id = ErmittleSpielerID()
    print("Spieler ID: ",spieler_id)
    wurf_nummer = ErmittleWurfNummer(spieler_id)
    wurf_wert = 20
    aufnahme = 0
    fehler = 0
    punktstand = 481
    punktstand_inv = 20
    wurf_gesamt = 20
    avg = 20
    wurf_typ = "S"
    spieler_id = 1
    #game_id =
    wurf_nummer_gesamt = 1

    return

def InitDetails():
    wurf_nummer = 1
    wurf_wert = 20
    aufnahme = 0
    fehler = 0
    punktstand = 481
    punktstand_inv = 20
    wurf_gesamt = 20
    avg = 20
    wurf_typ = "S"
    spieler_id = 1
    #game_id =
    wurf_nummer_gesamt = 1


    query = "INSERT INTO dartgame_details (Wurf_Nummer,Wurf_Wert,Aufnahme,Fehler,Punktstand,Punktstand_INV,Wurf_Gesamt,Avg,Wurf_Typ,Spieler_ID,Game_ID,Wurf_Nummer_Gesamt)"
    query = query + "VALUES (" + str(wurf_nummer) + "," + str(wurf_wert) + ","+ str(aufnahme) + ","+ str(fehler) + ","+ str(punktstand) + ","+ str(punktstand_inv) + ","+ str(wurf_gesamt) + ","+ str(avg) + ",'"+ wurf_typ + "',"+ str(spieler_id) + ","+ str(game_id) + "," + str(wurf_nummer_gesamt)+")"

    connection.execute(query)
    connection.commit()



def SendSpielstandToESP(data):
    global url,headers
    try:
        requests.post(url, data=json.dumps(data), headers=headers,timeout=0.5)
    except requests.Timeout:
        pass

def UpdateSpielstand():
    global database_path
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    alle_spieler = ["Spieler1","Spieler2"]
    punktstände = []
    for s in alle_spieler:
        cursor.execute("select punkte from dartgame where spieler = '"+s+"'")
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
    data = {'punkte0': str(punktstände[0]), 'punkte1': str(punktstände[1]), 'spieler': spielerindex}
    SendSpielstandToESP(data)

    if str(punktstände[0]) == '501' and str(punktstände[1]) == '501':
        initGame()



@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    print('received message:')
    print(data["data"])

@socketio.on('ueberworfen')
def handle_message(data):
    global database_path,spieler,last_committed_punktstand1,last_committed_punktstand2
    print('ueberworfen:')
    print(data["data"])
    print(data["currentSpieler"])
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    spieler = data["currentSpieler"] #"Spieler1"  # TODO MUSS VARIABEL SEIN

    cursor.execute("select wurfliste from dartgame where spieler = '"+spieler+"'")
    wurfliste = cursor.fetchone()[0].split(";")[1:]
    rest = len(wurfliste) % 3
    print("rest: ",rest)
    #errorliste = wurfliste[-rest:]
    #print("errorliste",errorliste)
    #errorliste.append(str(data["data"]))
    #while len(errorliste)<3:
    #    errorliste.append("0")
    #print("errorliste",errorliste)
    print(wurfliste[-rest:])
    outliste = wurfliste[0:-rest]

    #alten punktstand berechnen, bevor die Fehlwürfe an die Liste angehangen werden
    last_committed_punktstand = 0
    for elem in outliste:
        last_committed_punktstand += int(elem)
    last_committed_punktstand = 501 - last_committed_punktstand
    #print("outliste",outliste)
    #for e in errorliste:
    #    outliste.append("E"+e)
    stringToWrite = ";".join(outliste)
    query = "UPDATE dartgame SET wurfliste =  '" + str(stringToWrite)  + "' WHERE spieler = '"+ spieler + "' ;"
    cursor.execute(query)



    if spieler == "Spieler1":
        last_committed_punktstand1 = last_committed_punktstand
        query = "UPDATE dartgame SET punkte =  " + str(last_committed_punktstand)  + " WHERE spieler = '"+ spieler + "' ;"
    if spieler == "Spieler2":
        last_committed_punktstand2 = last_committed_punktstand
        query = "UPDATE dartgame SET punkte =  " + str(last_committed_punktstand)  + " WHERE spieler = '"+ spieler + "' ;"
    cursor.execute(query)
    connection.commit()
    WurflisteZuEinzelnenWürfen(outliste,False)
    UpdateSpielstand()


@socketio.on('zurueck')
def handle_message():
    global database_path,spieler
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("select wurfliste from dartgame where spieler = '"+spieler+"'")
    wurfliste = LeseWurfliste(spieler,cursor,schließeUeberworfenEin=False)
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
        wurfliste = LeseWurfliste(spieler,cursor,schließeUeberworfenEin=False)
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
        wurfliste = LeseWurfliste(spieler,cursor,schließeUeberworfenEin=False)
        if wurfliste[0] =="":
            wurfliste = wurfliste[1:]
        WurflisteZuEinzelnenWürfen(wurfliste,True)
    UpdateSpielstand()

# @socketio.on('spielerwechselZumESP')
# def handle_message(data):
#     global database_path
#     connection = sqlite3.connect(database_path)
#     cursor = connection.cursor()
#     alle_spieler = ["Spieler1","Spieler2"]
#     punktstände = []
#     for s in alle_spieler:
#         cursor.execute("select punkte from dartgame where spieler = '"+s+"'")
#         wert = cursor.fetchone()[0]
#         punktstände.append(wert)
#     connection.close()
#     dataESP = {'punkte0': str(punktstände[0]), 'punkte1': str(punktstände[1]), 'spieler': data["data"]}
#     SendSpielstandToESP(dataESP)


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
    InitDetails();
    InsertWurf();
    #socketio.run(app,host="0.0.0.0",allow_unsafe_werkzeug=True)

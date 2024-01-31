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

debug = False

spieler = "Spieler1"

last_committed_punktstand1 = 501
last_committed_punktstand2 = 501

file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
database_path = os.path.join(file_path,"database")
database_path = os.path.join(database_path,"darts.db")

#connection = sqlite3.connect("C:\\projects\\DartDashboard\\nativeHTML\\clientserver\\database\\darts.db")

game_id = 0



class Wurf:
    #ein Wurf beschreibt eine Zeile in dartgame_details
    def __init__(self, wurf_Nummer, wurf_Wert,aufnahme,fehler,punktstand,punktstand_INV,wurf_Gesamt,avg,wurf_typ,spieler_ID,game_ID,wurf_Nummer_Gesamt):
        self.wurf_Nummer = wurf_Nummer
        self.wurf_Wert = wurf_Wert
        self.aufnahme = aufnahme
        self.fehler = fehler
        self.punktstand = punktstand
        self.punktstand_INV = punktstand_INV
        self.wurf_Gesamt = wurf_Gesamt
        self.avg = avg
        self.wurf_typ = wurf_typ
        self.spieler_ID = spieler_ID
        self.game_ID = game_ID
        self.wurf_Nummer_Gesamt = wurf_Nummer_Gesamt

    
    def insert(self):
        global database_path
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        query = "INSERT INTO dartgame_details (Wurf_Nummer,Wurf_Wert,Aufnahme,Fehler,Punktstand,Punktstand_INV,Wurf_Gesamt,Avg,Wurf_Typ,Spieler_ID,Game_ID,Wurf_Nummer_Gesamt)"
        query = query + "VALUES (" + str(self.wurf_Nummer) + "," + str(self.wurf_Wert) + ","+ str(self.aufnahme) + ","+ str(self.fehler) + ","+ str(self.punktstand) + ","+ str(self.punktstand_INV) + ","+ str(self.wurf_Gesamt) + ","+ str(self.avg) + ",'"+ self.wurf_typ + "',"+ str(self.spieler_ID) + ","+ str(self.game_ID) + "," + str(self.wurf_Nummer_Gesamt)+")"

        cursor.execute(query)
        connection.commit()

    def __str__(self):

        outstring = "Spieler (ID = " + str(self.spieler_ID) + ") wirft: "+str(self.wurf_typ) + str(self.wurf_Wert) + " --- neuer Punktstand: " + str(self.punktstand)

        return outstring






app = Flask(__name__)
#            static_url_path='',
#            static_folder='/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


def ErmittleAndereID(currentID):
    global database_path
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute("select Spieler1_ID,Spieler2_ID from dartgame_header where Game_ID = " + str(game_id))
    row = cursor.fetchone()
    id1 = row[0]
    id2 = row[1]

    if id1 == currentID:
        return id2
    else:
        return id1
    


# def ErmittleSpielerID():
#     cursor.execute("select MAX(Wurf_Nummer_Gesamt),Spieler_ID from dartgame_details where Game_ID = " + str(game_id))
#     row = cursor.fetchone()
#     Max_Wurf_Nummer_Gesamt = int(row[0])
#     currentID = row[1]
    
#     rest  = Max_Wurf_Nummer_Gesamt % 3
#     if rest > 0:
#         ID = currentID
#     else:
#         ID = andereID(currentID)


#     return ID

# def ErmittleAufnahme(id):
#     cursor.execute("select MAX(Wurf_Nummer)from dartgame_details where Spieler_ID = '" + id + "' and Game_ID = " + str(game_id))
#     nr = cursor.fetchone()[0]
#     if nr == None:
#         nr = 1
#     else:
#         nr = int(game_id) + 1
#     return nr

# def ErmittleWurfNummer(id):
#     cursor.execute("select MAX(Wurf_Nummer)from dartgame_details where Spieler_ID = '" + id + "' and Game_ID = " + str(game_id))
#     nr = cursor.fetchone()[0]
#     if nr == None:
#         nr = 1
#     else:
#         nr = int(game_id) + 1
#     return nr


def LeseLetztenWurf(id=None):
    global database_path
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    if id==None:
        query = "select * from dartgame_details where Game_ID = " + str(game_id) + " and Wurf_Nummer_Gesamt = (select MAX(Wurf_Nummer_Gesamt) from dartgame_details where Game_ID = " + str(game_id) + ")"
    else:
        query = "select * from dartgame_details where Game_ID = " + str(game_id) + " and Spieler_ID = " + str(id) + " and Wurf_Nummer = (select MAX(Wurf_Nummer) from dartgame_details where Game_ID = " + str(game_id) + " and Spieler_ID = " + str(id) + ")"

    cursor.execute(query)
    row = cursor.fetchone()

    if row == None:
        #erster Wurf
        letzterWurf = Wurf(0,0,-1,0,501,0,0,0,None,None,game_id,0)
    
    else:
        letzterWurf = Wurf(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11])
        
    return letzterWurf





def InsertWurf(neuerWurf_Wert=0, neuerWurf_Typ='S'):
    #beides muss vom websocket kommen
    #neuerWurf_Wert z.B. 20
    #neuerWurf_Typ z.B. S

    #neuerWurf_Wert = 16
    #neuerWurf_Typ = 'T'

    print()
    print("### ---- Neuer Wurf! ---- ###")

    print("Lese letzten Wurf...")

    letzterWurf = LeseLetztenWurf()
    print(letzterWurf)
    wurf_nummer_gesamt = letzterWurf.wurf_Nummer_Gesamt + 1
    rest = letzterWurf.wurf_Nummer_Gesamt % 3
    if rest == 0:
        #Spielerwechsel
        print("Spielerwechsel")
        neuerWurf_id = ErmittleAndereID(letzterWurf.spieler_ID)
        letzterWurf = LeseLetztenWurf(neuerWurf_id)
        
        print("letzter Wurf vom anderen Spieler: ")
        print(letzterWurf)

        aufnahme = letzterWurf.aufnahme + 1

    else:
        ####
        # kein Spielerwechsel
        # letzter Wurf ist vom gleichen Spieler
        neuerWurf_id = letzterWurf.spieler_ID
        aufnahme = letzterWurf.aufnahme

    numerischerWertWurf = 0
    if neuerWurf_Typ == "S":
        numerischerWertWurf = neuerWurf_Wert
    else:
        if neuerWurf_Typ == "D":
            numerischerWertWurf = 2*neuerWurf_Wert
        else:
            if neuerWurf_Typ == "T":
                numerischerWertWurf = 3*neuerWurf_Wert
            else:
                error = 1
    
    if (letzterWurf.punktstand - numerischerWertWurf)<2:
        error = 1
    else:
        error = 0
        punktstand = letzterWurf.punktstand - numerischerWertWurf
        punktstand_inv = 501 - punktstand


    wurf_nummer = letzterWurf.wurf_Nummer + 1
    if aufnahme != letzterWurf.aufnahme:
        wurf_gesamt = numerischerWertWurf
    else:

        wurf_gesamt = letzterWurf.wurf_Gesamt + numerischerWertWurf

    avg = punktstand_inv / wurf_nummer

    w = Wurf(wurf_nummer,neuerWurf_Wert,aufnahme,error,punktstand,punktstand_inv,wurf_gesamt,avg,neuerWurf_Typ,neuerWurf_id,game_id,wurf_nummer_gesamt)
    w.insert()
    
    print("###---###---###---###")
    print("Neuer Wurf: ")
    print(w)


    return

# def InitDetails():
#     wurf_nummer = 1
#     wurf_wert = 20
#     aufnahme = 0
#     fehler = 0
#     punktstand = 481
#     punktstand_inv = 20
#     wurf_gesamt = 20
#     avg = 20
#     wurf_typ = "S"
#     spieler_id = 1
#     #game_id =
#     wurf_nummer_gesamt = 1


#     query = "INSERT INTO dartgame_details (Wurf_Nummer,Wurf_Wert,Aufnahme,Fehler,Punktstand,Punktstand_INV,Wurf_Gesamt,Avg,Wurf_Typ,Spieler_ID,Game_ID,Wurf_Nummer_Gesamt)"
#     query = query + "VALUES (" + str(wurf_nummer) + "," + str(wurf_wert) + ","+ str(aufnahme) + ","+ str(fehler) + ","+ str(punktstand) + ","+ str(punktstand_inv) + ","+ str(wurf_gesamt) + ","+ str(avg) + ",'"+ wurf_typ + "',"+ str(spieler_id) + ","+ str(game_id) + "," + str(wurf_nummer_gesamt)+")"

#     connection.execute(query)
#     connection.commit()



def SendSpielstandToESP(data):
    global url,headers
    try:
        requests.post(url, data=json.dumps(data), headers=headers,timeout=0.5)
    except requests.Timeout:
        pass

def UpdateSpielstand():

    p1 = LeseLetztenWurf(1)
    p2 = LeseLetztenWurf(2)



    #send spielstand to all connected websockets
    emit('spielstand_update', {'punktstand1': str(p1.punktstand),'punktstand2': str(p2.punktstand)}, broadcast=True)


    spieler = "Spieler1"
    #send spielstand to esp displays
    if spieler == "Spieler1":
        spielerindex = '0'
    else: 
        if spieler == "Spieler2":
            spielerindex = '1'
    data = {'punkte0': str(p1.punktstand), 'punkte1': str(p2.punktstand), 'spieler': spielerindex}
    SendSpielstandToESP(data)



@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    print('received message:')
    print(data["data"])


@socketio.on('wurf')
def handle_message(data):
    global database_path,spieler
    print('received message:')
    print(data["wert"])
    print(data["type"])

    InsertWurf(int(data["wert"]),data["type"])
    UpdateSpielstand()



@socketio.on('init event')
def test_message(message):
    initGame()

def initGame():
    global database_path, game_id
    connection = sqlite3.connect(database_path)

    cursor = connection.cursor()

    cursor.execute("SELECT MAX(Game_ID) FROM dartgame_header")
    game_id = cursor.fetchone()[0]
    if debug:
        game_id = 28
    else:
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
    emit('spielstand_update', {'punktstand1': 501,'punktstand2': 501}, broadcast=True)
    connection.close()

    global url,headers
    data = {'punkte0': '501', 'punkte1': '501', 'spieler': '0'}
    try:
        requests.post(url, data=json.dumps(data), headers=headers,timeout=0.5)
    except requests.Timeout:
        pass

if __name__ == '__main__':
    #InitDetails();
    #InsertWurf();
    socketio.run(app,host="0.0.0.0",allow_unsafe_werkzeug=True)

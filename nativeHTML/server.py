from flask import Flask, render_template
from flask_socketio import SocketIO, emit
#!/usr/bin/python
import sqlite3
import os,sys
import requests
import json, datetime
import paramiko


url = "http://192.168.0.214/update"
data = {'punkte0': '501', 'punkte1': '501', 'spieler': '0'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

debug = False

ESPAvailable = True

spieler = "Spieler1"

last_committed_punktstand1 = 501
last_committed_punktstand2 = 501

file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
database_path = os.path.join(file_path,"database")
database_path = os.path.join(database_path,"darts.db")

#connection = sqlite3.connect("C:\\projects\\DartDashboard\\nativeHTML\\clientserver\\database\\darts.db")

game_id = 0

winner = None

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

def sendeAufnahmeZuEinzelnenWürfen(aufnahme,id):
    global database_path
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    query = "select * from dartgame_details where Game_ID = " + str(game_id) + " and Spieler_ID = " + str(id) + " and Aufnahme = " + str(aufnahme) 
    cursor.execute(query)
    rows = cursor.fetchall()
    #print(rows)
    for i in range(len(rows),3):
        emit('wurf_historie',{'wurfnummer': str(i+1), 'wert': '', 'spielerid': str(id)}, broadcast=True)


    for i in range(len(rows)):
  #      if rows[i][8] == 1:
 #           emit('wurf_historie',{'wurfnummer': str(i+1), 'wert': 'E' + str(rows[i][1]), 'spielerid': str(id)}, broadcast=True)
#
        #else:
        emit('wurf_historie',{'wurfnummer': str(i+1), 'wert': str(rows[i][8]) + str(rows[i][1]), 'spielerid': str(id)}, broadcast=True)
    

    if len(rows)>0:
        emit('avg',{'avg': str(round(rows[-1][7],2)),'dartscount': str(rows[-1][0]), 'spielerid': str(id)}, broadcast=True)
        emit('visit_score',{'visit_score': str(rows[-1][6])}, broadcast=True)

def schreibeGewinner(id):
    global database_path
    if id != None:
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        time = str(datetime.datetime.now())

        p1 = LeseLetztenWurf(1,True)
        p2 = LeseLetztenWurf(2,True)
        avg1 = p1.avg
        avg2 = p2.avg
        query = "Update dartgame_header set Endzeit = '" + time +"', Ergebnis = " + str(winner) + ", Spieler1_Avg = " + str(avg1) + ", Spieler2_Avg = " + str(avg2) + " where Game_ID = "+ str(game_id) 
        cursor.execute(query)
        connection.commit()

        if winner == 1:
            avg = avg1
            darts = p1.wurf_Nummer
        else:
            avg = avg2
            darts = p2.wurf_Nummer

        queryString = "Spieler" + str(id) + "_Name"

        query = "select "+queryString + " from dartgame_header where Game_ID = " + str(game_id)
        cursor.execute(query)
        rows = cursor.fetchone()
        emit('winner',{'winner': str(id),'avg': str(avg), 'darts': str(darts), 'name': str(rows[0])}, broadcast=True)


def SchreibeGesamteAufnahmeAlsFehler(aufnahme,id):
    global database_path
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    query = "Update dartgame_details set Fehler = 1 where Game_ID = " + str(game_id) + " and Spieler_ID = " + str(id) + " and Aufnahme = "+ str(aufnahme)
    cursor.execute(query)
    connection.commit()


def LeseLetztenWurf(id=None,excludeErrors=False):
    global database_path

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    if id==None:
        #excludeErrors = False
        query = "select * from dartgame_details where Game_ID = " + str(game_id) + " and Wurf_Nummer_Gesamt = (select MAX(Wurf_Nummer_Gesamt) from dartgame_details where Game_ID = " + str(game_id) + ")"
        #query = "select * from dartgame_details where Game_ID = " + str(game_id) + " and Aufnahme = (select MAX(Aufnahme) from dartgame_details where Game_ID = " + str(game_id) + ")"
    else:
        query = "select * from dartgame_details where Game_ID = " + str(game_id) + " and Spieler_ID = " + str(id) + " and Wurf_Nummer_Gesamt = (select MAX(Wurf_Nummer_Gesamt) from dartgame_details where Game_ID = " + str(game_id) + " and Spieler_ID = " + str(id) + ")"

        #query = "select * from dartgame_details where Game_ID = " + str(game_id) + " and Spieler_ID = " + str(id) + " and Aufnahme = (select MAX(Aufnahme) from dartgame_details where Game_ID = " + str(game_id) + " and Spieler_ID = " + str(id) + ")"

    cursor.execute(query)
    row = cursor.fetchall()

    if row == None or len(row)==0:
        #erster Wurf
        letzterWurf = Wurf(0,0,-1,0,501,0,0,0,None,None,game_id,0)
    
    else:
        row_single = row[-1]
        if excludeErrors:
            aufnahme = row_single[2]
            wurf_nr = row_single[0]
            wurf_nr_gesamt = row_single[11]

            validAufnahmeFound = False
            while(validAufnahmeFound == False):
                errorCount = 0

                for i in range(len(row)):
                    errorCount = errorCount + row[i][3]

                if errorCount == 0:

                    validAufnahmeFound = True

                else:
                    validAufnahmeFound = False
                    nächsteaufnahme = row[0][2] - 1
                    #if id == None:
                    #    id = ErmittleAndereID(row[0][9])
                    query = "select * from dartgame_details where Game_ID = " + str(game_id) + " and Spieler_ID = " + str(id) + " and Aufnahme = " + str(nächsteaufnahme)

                    cursor.execute(query)
                    row = cursor.fetchall()

            #row[-1][2] = row_single[2] #aufnahme
            #row[-1][0] = row_single[0] #wurfnr
            #row[-1][11] = row_single[11] #wurfnrgesamt


            row_single = row[-1]
            letzterWurf = Wurf(wurf_nr,row_single[1],aufnahme,row_single[3],row_single[4],row_single[5],row_single[6],row_single[7],row_single[8],row_single[9],row_single[10],wurf_nr_gesamt)
        else:
            letzterWurf = Wurf(row_single[0],row_single[1],row_single[2],row_single[3],row_single[4],row_single[5],row_single[6],row_single[7],row_single[8],row_single[9],row_single[10],row_single[11])



    return letzterWurf





def InsertWurf(neuerWurf_Wert=0, neuerWurf_Typ='S'):
    global winner
    #beides muss vom websocket kommen
    #neuerWurf_Wert z.B. 20
    #neuerWurf_Typ z.B. S

    #neuerWurf_Wert = 16
    #neuerWurf_Typ = 'T'

    print()
    print("### ---- Neuer Wurf! ---- ###")

    print("Lese letzten Wurf...")

    letzterWurf = LeseLetztenWurf(excludeErrors=False)
    print(letzterWurf)
    wurf_nummer_gesamt = letzterWurf.wurf_Nummer_Gesamt + 1
    rest = letzterWurf.wurf_Nummer_Gesamt % 3
    print("rest: ", rest)
    if rest == 0:
        #Spielerwechsel
        print("Spielerwechsel")
        neuerWurf_id = ErmittleAndereID(letzterWurf.spieler_ID)
        letzterWurf = LeseLetztenWurf(neuerWurf_id,True)
        
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
    
    if (neuerWurf_Typ == "D") and ((letzterWurf.punktstand - numerischerWertWurf) == 0):
        winner = neuerWurf_id

    if ((letzterWurf.punktstand - numerischerWertWurf)<2 and (winner == None)):
        error = 1
        neuerWurf_Typ = 'E' + neuerWurf_Typ
        punktstand = letzterWurf.punktstand
        punktstand_inv = 501 - punktstand
    else:
        error = 0
        punktstand = letzterWurf.punktstand - numerischerWertWurf
        punktstand_inv = 501 - punktstand


    wurf_nummer = letzterWurf.wurf_Nummer + 1
    if aufnahme != letzterWurf.aufnahme:
        wurf_gesamt = numerischerWertWurf
    else:

        wurf_gesamt = letzterWurf.wurf_Gesamt + numerischerWertWurf

    avg = punktstand_inv / (aufnahme+1)

    w = Wurf(wurf_nummer,neuerWurf_Wert,aufnahme,error,punktstand,punktstand_inv,wurf_gesamt,avg,neuerWurf_Typ,neuerWurf_id,game_id,wurf_nummer_gesamt)
    w.insert()
    
    if(error):
        print("Fehler!")
        print(wurf_nummer)
        rest_2 = wurf_nummer % 3
        print(rest_2)
        if rest_2 > 0:
            fehlwürfe_auffüllen = 3-rest_2
            while(fehlwürfe_auffüllen>0):
                print("fülle fehlwurf in aufnahme hinzu")
                fehlwürfe_auffüllen -= 1
                wurf_nummer += 1
                neuerWurf_Wert = 0
                wurf_nummer_gesamt += 1
                neuerWurf_Typ = 'E'
                w = Wurf(wurf_nummer,neuerWurf_Wert,aufnahme,error,punktstand,punktstand_inv,wurf_gesamt,avg,neuerWurf_Typ,neuerWurf_id,game_id,wurf_nummer_gesamt)
                w.insert()


        SchreibeGesamteAufnahmeAlsFehler(aufnahme,neuerWurf_id)

    print("###---###---###---###")
    print("Neuer Wurf: ")
    print(w)

    #rest = wurf_nummer % 3
    sendeAufnahmeZuEinzelnenWürfen(aufnahme,neuerWurf_id)


    if winner == None:
        if rest == 2 or error:
            #spieler wirft den dritten dart einer aufnahme, anschließend schaltet die UI auf spielerwechsel
            #spielerwechsel (UI) erfolgt bereits vor dem Wurf des neuen Spielers
            id  = ErmittleAndereID(neuerWurf_id)
            if id == 1:
                emit('spieler_wechsel', {'spieler': 'Spieler1'}, broadcast=True)
            else:
                emit('spieler_wechsel', {'spieler': 'Spieler2'}, broadcast=True)


            #lösche die letzten drei würfe vom neuen spieler, da neue aufnahme
    else:
        schreibeGewinner(winner)



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


def clearWurfAnzeige(id):
    for i in range(3):
        emit('wurf_historie',{'wurfnummer': str(i+1), 'wert': '', 'spielerid': str(id)}, broadcast=True)



def SendSpielstandToESP(data):
    global url,headers
    global ESPAvailable
    if ESPAvailable:
        try:
            requests.post(url, data=json.dumps(data), headers=headers,timeout=0.5)
        except requests.Timeout:
            pass

def UpdateSpielstand():

    p1 = LeseLetztenWurf(1,True)
    p2 = LeseLetztenWurf(2,True)



    #send spielstand to all connected websockets
    emit('spielstand_update', {'punktstand1': str(p1.punktstand),'punktstand2': str(p2.punktstand)}, broadcast=True)



    if p1.wurf_Nummer_Gesamt > p2.wurf_Nummer_Gesamt:
        spielerindex = '0'
    else:
         spielerindex = '1'
    data = {'punkte0': str(p1.punktstand), 'punkte1': str(p2.punktstand), 'spieler': spielerindex}
    SendSpielstandToESP(data)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/streams')
def fullscreen():
    """Video streaming home page."""
    return render_template('streams.html')


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
    if winner == None:
        InsertWurf(int(data["wert"]),data["type"])
        UpdateSpielstand()

@socketio.on('zurueck')
def handle_zurueck():
    global database_path

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    #rest berechnen, bevor eine zeile gelöscht wird
    query = "select Wurf_Nummer, Spieler_ID from dartgame_details where Game_ID = " + str(game_id) + " and Wurf_Nummer_Gesamt = (select MAX(Wurf_Nummer_Gesamt) from dartgame_details where Game_ID = " + str(game_id) + ")"
    cursor.execute(query)
    rows = cursor.fetchone()
    rest = rows[0] % 3
    id  = rows[1]
    if rest == 1:
        clearWurfAnzeige(id)
    if rest == 0:
        
        #id  = ErmittleAndereID(id)
        
        if id == 1:
            emit('spieler_wechsel', {'spieler': 'Spieler1'}, broadcast=True)
        else:
            emit('spieler_wechsel', {'spieler': 'Spieler2'}, broadcast=True)
    query = "delete from dartgame_details where Game_ID = " + str(game_id) + " and Wurf_Nummer_Gesamt = (select MAX(Wurf_Nummer_Gesamt) from dartgame_details where Game_ID = " + str(game_id) + ")"
    cursor.execute(query)
    connection.commit()

    query = "select Aufnahme, Spieler_ID, Wurf_Nummer from dartgame_details where Game_ID = " + str(game_id) + " and Wurf_Nummer_Gesamt = (select MAX(Wurf_Nummer_Gesamt) from dartgame_details where Game_ID = " + str(game_id) + ")"
    cursor.execute(query)
    rows = cursor.fetchone()
    if rows == None:
        initGame()
    else:
        aufnahme = rows[0]
        id = rows[1]
        sendeAufnahmeZuEinzelnenWürfen(aufnahme,id)
        UpdateSpielstand()
    
@socketio.on('restart_server_service')
def restartService(data=None):
    if data == None:
        return
    ssh = paramiko.SSHClient()

    user = "boris"

    f = open("server.txt", "r")

    password = f.read()

    f.close()

    server = data["server"]

    #cmd_to_execute = "sudo systemctl restart boris.service"
    cmd_to_execute = data["cmd"]

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(server, username=user, password=password)

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)

    for line in ssh_stdout.readlines():
        print(line)



@socketio.on('new_player')
def new_player(message):
    global database_path
    connection = sqlite3.connect(database_path)

    cursor = connection.cursor()

    cursor.execute("Select Name from dartgame_players where Name = '"+ str(message["name"]) +"'")
    rows = cursor.fetchone()
    if rows == None:

        query = "Insert into dartgame_players (Name,Spiele_Gesamt,Letztes_Spiel,Letzter_Average,Durchschnitt_Average)"
        query = query + " VALUES ('" + str(message["name"]) + "',0,'',0,0)"
        #     query = "INSERT INTO dartgame_details (Wurf_Nummer,Wurf_Wert,Aufnahme,Fehler,Punktstand,Punktstand_INV,Wurf_Gesamt,Avg,Wurf_Typ,Spieler_ID,Game_ID,Wurf_Nummer_Gesamt)"


        cursor.execute(query)

        connection.commit()
        print("Spieler " + str(message["name"]) + " wurde hinzugefügt.")

    else:
        print("Spieler " + str(message["name"]) + " bereits vorhanden.")

    connection.close()

    initPlayers()


@socketio.on('init_connection')
def init_connection(message):
    initPlayers()
    print("players table created/updated. Connection established.")

    try:
        UpdateSpielstand()
    except:
        print("kein Spiel gestartet.")
 
@socketio.on('init event')
def test_message(message):
    name1 = message["player1"]
    name2 = message["player2"]
    initGame(name1,name2)

def initPlayers():
    global database_path
    connection = sqlite3.connect(database_path)

    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS dartgame_players (Name STRING, Spiele_Gesamt Integer, Letztes_Spiel String, Letzter_Average REAL, Durchschnitt_Average REAL);")
    connection.commit()

    cursor.execute("SELECT DISTINCT Name FROM dartgame_players")
    all_players = cursor.fetchall()
    if all_players != None:
        print(all_players)

    #emit('spieler_wechsel', {'spieler': 'Spieler2'}, broadcast=True)
    emit('init_player_selection',{'data': str(all_players)}, broadcast=True)


def initGame(name1=None,name2=None):
    global database_path, game_id, winner
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

    if name1 == None:
        name1 = "Lini"
    if name2 == None:
        name2 = "Rici"

    query = "INSERT INTO dartgame_header ('Game_ID','Typ','Typ_Punktstand','Spieler1_ID','Spieler2_ID','Spieler1_Name','Spieler2_Name','Ergebnis','Startzeit')"
    query = query +  "VALUES ("+ str(game_id) + ",'DoubleOut',501,1,2,'" + str(name1) + "','" + str(name2) + "','läuft','" + time + "')"

    winner = None
    cursor.execute(query)

    connection.commit()

    emit('init_names', {'spieler1': name1,'spieler2': name2}, broadcast=True)

    sendeAufnahmeZuEinzelnenWürfen(0,0)

    emit('spielstand_update', {'punktstand1': 501,'punktstand2': 501}, broadcast=True)
    connection.close()

    if ESPAvailable:
        global url,headers
        data = {'punkte0': '501', 'punkte1': '501', 'spieler': '0'}
        try:
            requests.post(url, data=json.dumps(data), headers=headers,timeout=0.5)
        except requests.Timeout:
            pass
    
        data = {'punkte0': '501', 'punkte1': '501', 'spieler': '1'}
        try:
            requests.post(url, data=json.dumps(data), headers=headers,timeout=0.5)
        except requests.Timeout:
            pass

if __name__ == '__main__':
    #InitDetails();
    #InsertWurf();
    socketio.run(app,host="0.0.0.0",allow_unsafe_werkzeug=True)

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

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    print('received message:')
    print(data["data"])

@socketio.on('wurf')
def handle_message(data):
    global database_path
    print('received message:')
    print(data["data"])
    print(data["currentSpieler"])
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    spieler = data["currentSpieler"] #"Spieler1"  # TODO MUSS VARIABEL SEIN
    if spieler:
        spielerindex = '0'
    else:
        spielerindex = '1'
    cursor.execute("select punkte from dartgame where spieler = '"+spieler+"'")
    wert = cursor.fetchone()[0] - int(data["data"])
    query = "UPDATE dartgame SET punkte =  " + str(wert)  + " WHERE spieler = '"+ spieler + "' ;"
    print("neue Punktzahl: ",str(wert))
    cursor.execute(query)
    cursor.execute("select wurfliste from dartgame where spieler = '"+spieler+"'")
    wert = cursor.fetchone()[0] + ";" + data["data"]
    query = "UPDATE dartgame SET wurfliste =  '" + str(wert)  + "' WHERE spieler = '"+ spieler + "' ;"
    print("Wurfliste: ",str(wert))
    print(wert.split(";")[1:])
    cursor.execute(query)



    connection.commit()
    alle_spieler = ["Spieler1","Spieler2"]
    punktstände = []
    for spieler in alle_spieler:
        cursor.execute("select punkte from dartgame where spieler = '"+spieler+"'")
        wert = cursor.fetchone()[0]
        punktstände.append(wert)

    #send spielstand to all connected websockets
    emit('spielstand_update', {'punktstand1': punktstände[0],'punktstand2': punktstände[1]}, broadcast=True)
    connection.close()

    #send spielstand to esp displays
    global url,headers
    data = {'punkte0': str(punktstände[0]), 'punkte1': str(punktstände[1]), 'spieler': spielerindex}
    try:
        requests.post(url, data=json.dumps(data), headers=headers,timeout=0.5)
    except requests.Timeout:
        pass
@socketio.on('init event')
def test_message(message):
    global database_path
    connection = sqlite3.connect(database_path)

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
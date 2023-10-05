from flask import Flask, render_template
from flask_socketio import SocketIO, emit
#!/usr/bin/python
import sqlite3
import os,sys

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
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    spieler = "Spieler1"  # TODO MUSS VARIABEL SEIN
    cursor.execute("select punkte from dartgame where spieler = '"+spieler+"'")
    wert = cursor.fetchone()[0] - int(data["data"])
    query = "UPDATE dartgame SET punkte =  " + str(wert)  + " WHERE spieler = '"+ spieler + "' ;"
    print("neue Punktzahl: ",str(wert))
    cursor.execute(query)
    connection.commit()
    alle_spieler = ["Spieler1","Spieler2"]
    punktstände = []
    for spieler in alle_spieler:
        cursor.execute("select punkte from dartgame where spieler = '"+spieler+"'")
        wert = cursor.fetchone()[0]
        punktstände.append(wert)
    emit('spielstand_update', {'punktstand1': punktstände[0],'punktstand2': punktstände[1]}, broadcast=True)
    connection.close()
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
    connection.commit()
    emit('spielstand_update', {'punktstand1': 501,'punktstand2': 501}, broadcast=True)
    connection.close()
    #emit('my response', {'data': message["data"]}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0")
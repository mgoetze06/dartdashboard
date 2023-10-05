# from flask import Flask, render_template
# from flask_sock import Sock

# app = Flask(__name__)
# sock = Sock(app)





# @sock.route('/echo')
# def echo(sock):
#     while True:
#         data = sock.receive()
#         sock.send(data)


# if __name__ == '__main__':
#     app.run(host="0.0.0.0")
#     #app.run(debug=False)



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
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    print('received message:')
    print(data["data"])

@socketio.on('my broadcast event')
def test_message(message):
    global database_path
    connection = sqlite3.connect(database_path)

    cursor = connection.cursor()
    spieler = "Spieler1"
    cursor.execute("UPDATE dartgame SET punkte =  " + str(message['data']) + " WHERE spieler = '"+ spieler + "' ;")
    connection.commit()

    alle_spieler = ["Spieler1","Spieler2"]
    for spieler in alle_spieler:
        print(spieler)
        cursor.execute("select punkte from dartgame where spieler = '"+spieler+"'")
        wert = cursor.fetchone()[0]
        #print(cursor.fetchone()[0])
    print('received broadcast message')
    #print(message["data"])
    emit('my response', {'data': wert}, broadcast=True)
    connection.close()
    #emit('my response', {'data': message["data"]}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
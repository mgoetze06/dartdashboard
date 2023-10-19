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


#cursor.execute("CREATE TABLE dart_game (spieler text, punkte integer, game_id integer, type text)")
alle_spieler = ["Spieler1","Spieler2"]
for spieler in alle_spieler:
    print(spieler)
    cursor.execute("select punkte from dartgame where spieler = '"+spieler+"'")
    print(cursor.fetchone()[0])
    #for c in cursor.fetchall():
    #    print(c)
#cursor.execute("INSERT INTO dart_game (spieler,punkte,game_id,type) VALUES ('Spieler1',501,{},'DoubleOut')".format(0))
#cursor.execute("INSERT INTO dart_game (spieler,punkte,game_id,type) VALUES ('Spieler2',501,{},'DoubleOut')".format(0))

connection.commit()
connection.close()



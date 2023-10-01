#!/usr/bin/python
import sqlite3

connection = sqlite3.connect("C:\\projects\\DartDashboard\\nativeHTML\\database\\darts.sqlite")

cursor = connection.cursor()
try:
    cursor.execute("CREATE TABLE dart_game (spieler text, punkte integer, game_id integer, type text)")
except:
    pass
cursor.execute("INSERT INTO dart_game (spieler,punkte,game_id,type) VALUES ('Spieler1',501,{},'DoubleOut')".format(0))
cursor.execute("INSERT INTO dart_game (spieler,punkte,game_id,type) VALUES ('Spieler2',501,{},'DoubleOut')".format(0))

connection.commit()
connection.close()


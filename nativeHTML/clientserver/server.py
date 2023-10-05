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
    print('received broadcast message')
    print(message["data"])
    emit('my response', {'data': message["data"]}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
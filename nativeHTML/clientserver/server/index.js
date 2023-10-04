const WebSocket = require("ws");
const express = require("express");
const app = express()
const path = require("path")

app.use("/",express.static(path.resolve(__dirname, "../client")))

const myServer = app.listen(9876)       // regular http server using node express which serves your webpage

const wsServer = new WebSocket.Server({
    noServer: true
})                                      // a websocket server

wsServer.on("connection", function(ws) {    // what should a websocket do on connection
    ws.on("message", function(msg) {        // what to do on message event
        wsServer.clients.forEach(function each(client) {
            if (client.readyState === WebSocket.OPEN) {     // check if client is ready
              client.send(msg.toString());
            }
        })
    })
})

myServer.on('upgrade', async function upgrade(request, socket, head) {      //handling upgrade(http to websocekt) event

    // accepts half requests and rejects half. Reload browser page in case of rejection
    
    if(Math.random() > 0.5){
        return socket.end("HTTP/1.1 401 Unauthorized\r\n", "ascii")     //proper connection close in case of rejection
    }
    
    //emit connection when request accepted
    wsServer.handleUpgrade(request, socket, head, function done(ws) {
      wsServer.emit('connection', ws, request);
    });
});
const WebSocket = require("ws");
const express = require("express");
const app = express()
const path = require("path");
const { Console } = require("console");
const sqlite3 = require('sqlite3').verbose();
const filepath = "C:/projects/DartDashboard/nativeHTML/clientserver/server/darts.db";

app.use("/",express.static(path.resolve(__dirname, "../client")))

const myServer = app.listen(9876)       // regular http server using node express which serves your webpage

const wsServer = new WebSocket.Server({
    noServer: true
})                                      // a websocket server

async function main() {
    db = await createDbConnection();
    await queryDB('select punkte from dartgame',db);
    await queryDB("select * from dartgame",db);
}


main();

function createDbConnection() {


    const db = new sqlite3.Database(filepath,sqlite3.OPEN_READWRITE,(error) => {
          if (error) {
            return console.error(error.message);
           }
         });
         return db;

    // const db = new sqlite3.Database(filepath, open=true, (error) => {
    //   if (error) {
    //     return console.error(error.message);
    //   }
    // });
    // console.log("Connection with SQLite has been established");
    // return db;
}
async function queryDB(query,db){
    try {
        console.log('Starting orderAlreadyProcessed function');
        //const query = 'SELECT COUNT(SoldOrderNumber) as `recsCount` from ProcessedSoldOrders where SoldOrderNumber = ?;'
        const row = await db.get(query);
        const db2 = await row.get(query);
        console.log('Row with count =', db2);
        //console.log('row.recsCount =', row.recsCount);
        const result = typeof row !== 'undefined' && row.recsCount > 0;
        console.log('Returning ' + result);
        return result;
    } catch (error) {
        console.error(error);
        throw error;
    }
}

// using
// you need to add the keyword "async" in the function that call getTestWithQuestions, then :

//const testWithQuestions = await getTestWithQuestions(); // testWithQuetions is `test_array`

// if you don't want to add async keyword, then : 
//getTestWithQuestions()
//.then(testWithQuestions => console.log(testWithQuestions))
//.catch(error => console.log(error));


wsServer.on("connection", function(ws) {    // what should a websocket do on connection
    ws.on("message", function(msg) {        // what to do on message event
        wsServer.clients.forEach(function each(client) {
            if (client.readyState === WebSocket.OPEN) {
                     // check if client is ready
                if(msg == "Init DB"){
                    db = createDbConnection();
                    client.send("501".toString());
                }
                else if(msg == "get"){
                    queryDB('select * from dart_game');
                    //temp = db.get('select * from dart_game');
                    //console.log(temp.punkte);
                    client.send("fertsch".toString());
                }
                else{
                    client.send(msg.toString());
                }
              
            }
        })
    })
})

myServer.on('upgrade', async function upgrade(request, socket, head) {      //handling upgrade(http to websocekt) event

    // accepts half requests and rejects half. Reload browser page in case of rejection
    
    // if(Math.random() > 0.5){
    //     return socket.end("HTTP/1.1 401 Unauthorized\r\n", "ascii")     //proper connection close in case of rejection
    // }
    
    //emit connection when request accepted
    wsServer.handleUpgrade(request, socket, head, function done(ws) {
      wsServer.emit('connection', ws, request);
    });
});
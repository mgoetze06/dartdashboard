// var http = require('http'),
//     fs = require('fs');


// fs.readFile('./index.html', function (err, html) {
//     if (err) {
//         throw err; 
//     }       
//     http.createServer(function(request, response) {  
//         response.writeHeader(200, {"Content-Type": "text/html"});  
//         response.write(html);  
//         response.end();  
//     }).listen(3000);
// });
const sqlite3 = require('sqlite3').verbose();
const filepath = "./database/darts.db";


function getFromDB(){
    //import * as sqlite3 from '.\\node_modules\\sqlite3\\lib\\sqlite3';
    //const sqlite3 = require(['.\\node_modules\\sqlite3\\lib\\sqlite3']);
    let db = new sqlite3.Database('./database/darts.db', (err) => {
        if (err) {
          console.error(err.message);
        }
        console.log('Connected to the chinook database.');
      });
    //const sqlite3 = require('sqlite3');
    //const db = new sqlite3.Database('database\\darts.db');
    //var temp = db.get("SELECT * FROM dart_game");
    document.getElementById("debug").value = "test";
}
function createDbConnection() {
    const db = new sqlite3.Database(filepath, (error) => {
      if (error) {
        return console.error(error.message);
      }
    });
    console.log("Connection with SQLite has been established");
    return db;
}




const express = require('express')

var fs = require('fs');
const app = express()
const port = 3000

app.get('/', (req, res) => {
  //res.send('Hello World!')
  fs.readFile('index.html', function(err, data){
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.end(data, 'utf-8');
 });
})
app.use(express.static("public"));

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})
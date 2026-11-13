// A real isolated MongoDB server for local development; data persists under .local.
const {MongoMemoryServer}=require('mongodb-memory-server');
const fs=require('node:fs');const path=require('node:path');
const {app,connect}=require('./app');
(async()=>{const dbPath=path.resolve('../../.local/mongodb');fs.mkdirSync(dbPath,{recursive:true});
const mongo=await MongoMemoryServer.create({instance:{port:27018,dbPath,storageEngine:'wiredTiger'}});
await connect(mongo.getUri());
const server=app.listen(3030,'127.0.0.1',()=>console.log('API http://127.0.0.1:3030; local MongoDB on 27018'));
process.on('SIGTERM',()=>server.close(async()=>{await require('mongoose').disconnect();await mongo.stop();process.exit(0)}));})();

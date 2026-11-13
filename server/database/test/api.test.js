const {test,before,after}=require('node:test');
const assert=require('node:assert/strict');
const {MongoMemoryServer}=require('mongodb-memory-server');
const mongoose=require('mongoose');
const {app,connect}=require('../app');
let mongo,server,base;
before(async()=>{mongo=await MongoMemoryServer.create();await connect(mongo.getUri());server=app.listen(0,'127.0.0.1');await new Promise(resolve=>server.once('listening',resolve));base='http://127.0.0.1:'+server.address().port;});
after(async()=>{await new Promise(resolve=>server.close(resolve));await mongoose.disconnect();await mongo.stop();});
async function get(path){const r=await fetch(base+path);return {status:r.status,data:await r.json()};}
test('directory returns seed records in order',async()=>{const r=await get('/fetchDealers');assert.equal(r.status,200);assert.ok(r.data.length>10);assert.equal(r.data[0].id,1);});
test('state filtering and unknown state',async()=>{const r=await get('/fetchDealers/Kansas');assert.ok(r.data.length);assert.ok(r.data.every(d=>d.state==='Kansas'));assert.deepEqual((await get('/fetchDealers/Unknown')).data,[]);});
test('single dealer and invalid ID',async()=>{assert.equal((await get('/fetchDealer/1')).data[0].id,1);assert.equal((await get('/fetchDealer/notanumber')).status,400);assert.deepEqual((await get('/fetchDealer/999999')).data,[]);});
test('review persistence and concurrent IDs',async()=>{const payload={name:'Integration Test',dealership:1,review:'Excellent service and a wonderful car.',purchase:true,purchase_date:'2026-01-02',car_make:'Toyota',car_model:'Camry',car_year:2023};const responses=await Promise.all(Array.from({length:3},()=>fetch(base+'/insert_review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})));assert.ok(responses.every(r=>r.status===201));const rows=await Promise.all(responses.map(r=>r.json()));assert.equal(new Set(rows.map(r=>r.id)).size,3);const stored=(await get('/fetchReviews/dealer/1')).data;assert.ok(stored.some(r=>r.id===rows[0].id));});
test('malformed reviews are rejected',async()=>{const r=await fetch(base+'/insert_review',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});assert.equal(r.status,400);});
test('reconnecting does not erase reviews',async()=>{await connect(mongo.getUri());const rows=(await get('/fetchReviews/dealer/1')).data;assert.ok(rows.some(r=>r.name==='Integration Test'));});

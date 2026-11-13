const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const fs = require('node:fs');
const path = require('node:path');
const Reviews = require('./review');
const Dealerships = require('./dealership');
const app = express();
app.use(cors());
app.use(express.json({limit:'32kb'}));
const wrap = fn => (req,res,next) => Promise.resolve(fn(req,res,next)).catch(next);
const numberId = x => /^\d+$/.test(x) && Number.isSafeInteger(Number(x));
app.get('/', (req,res)=>res.json({service:'Best Cars dealership API',status:'ok'}));
app.get('/fetchReviews',wrap(async(req,res)=>res.json(await Reviews.find().lean())));
app.get('/fetchReviews/dealer/:id',wrap(async(req,res)=>{
  if(!numberId(req.params.id)) return res.status(400).json({error:'Invalid dealer ID'});
  res.json(await Reviews.find({dealership:Number(req.params.id)}).sort({id:-1}).lean());
}));
app.get('/fetchDealers',wrap(async(req,res)=>res.json(await Dealerships.find().sort({id:1}).lean())));
app.get('/fetchDealers/:state',wrap(async(req,res)=>{
  res.json(await Dealerships.find(req.params.state==='All'?{}:{state:req.params.state}).sort({id:1}).lean());
}));
app.get('/fetchDealer/:id',wrap(async(req,res)=>{
  if(!numberId(req.params.id)) return res.status(400).json({error:'Invalid dealer ID'});
  res.json(await Dealerships.find({id:Number(req.params.id)}).lean());
}));
app.post('/insert_review',wrap(async(req,res)=>{
  const d=req.body;
  if(!Number.isSafeInteger(Number(d.dealership)) || typeof d.review!=='string' || !d.review.trim() || d.review.length>5000 || typeof d.name!=='string') return res.status(400).json({error:'Invalid review'});
  if(!await Dealerships.exists({id:Number(d.dealership)})) return res.status(404).json({error:'Dealer not found'});
  const counter = await mongoose.connection.collection('counters').findOneAndUpdate({_id:'review'},{$inc:{value:1}},{upsert:true,returnDocument:'after'});
  const review=await Reviews.create({id:counter.value,name:d.name,dealership:Number(d.dealership),review:d.review.trim(),purchase:d.purchase,purchase_date:d.purchase_date,car_make:d.car_make,car_model:d.car_model,car_year:d.car_year});
  res.status(201).json(review);
}));
app.use((err,req,res,next)=>{console.error(err.message);res.status(err.name==='ValidationError'||err instanceof SyntaxError?400:500).json({error:'Unable to process request'});});
async function connect(uri){
  await mongoose.connect(uri,{dbName:'dealershipsDB'});
  if(await Dealerships.countDocuments()===0){
    const data=JSON.parse(fs.readFileSync(path.join(__dirname,'data/dealerships.json')));
    await Dealerships.insertMany(data.dealerships);
  }
  if(await Reviews.countDocuments()===0){
    const data=JSON.parse(fs.readFileSync(path.join(__dirname,'data/reviews.json')));
    await Reviews.insertMany(data.reviews);
  }
  const latest=await Reviews.findOne().sort({id:-1}).lean();
  await mongoose.connection.collection('counters').updateOne({_id:'review'},{$max:{value:latest?.id||0}},{upsert:true});
}
if(require.main===module) connect(process.env.MONGODB_URI||'mongodb://127.0.0.1:27017').then(()=>app.listen(process.env.PORT||3030,'0.0.0.0',()=>console.log('Dealership API ready on port '+(process.env.PORT||3030)))).catch(err=>{console.error(err);process.exit(1)});
module.exports={app,connect};

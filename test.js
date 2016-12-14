const fs = require('fs');
const iClient = require('./insightClient');
ic = new iClient('queue');

let res = fs.readFileSync('./newTestData.json', 'utf8');
res = JSON.parse(res);

ic.send('queue', res, (o) => {
  if (o.error) console.log(o.error);
  console.log(o.payload);
  console.log('done');
  process.exit(0)
})

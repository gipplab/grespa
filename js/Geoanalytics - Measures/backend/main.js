var express = require('express');
var compress = require('compression');
var bodyParser = require('body-parser');
var async = require('async');
var config = require('./config');
var cors = require('cors');
var postgres = require('pg');
postgres.defaults.poolSize = 100;

var app = express();

app.use(compress({
    level: 9
}));
app.use(cors()); //use cors for avoiding cross-reference exceptions 
app.use(bodyParser.urlencoded({ //accepts url-encoded POST parameters
    extended: true
}));
app.use(bodyParser.json()); //accepts json-encoded POST objects

app.post('/getData', function (req, res) {
	if (!req.body.i) res.send([]);
	var agg; 
	var i = parseInt(req.body.i); 
		if (i==0){
			agg = 'COUNT(*)'; 
		} else { 
			var agg = (i%2 == 1) ? 'SUM' : 'CAST(AVG';
			agg += '(measures['+(i+(i %2))+'])'
			if (i%2 == 0) agg+='  AS DECIMAL(10,3)) '; //round avg with 3 digits 
		}
    postgres.connect(config.getDBAuth(), function(err, client, done){
		if (!err && client){
			var q = 'SELECT id,val, org.name,  org.lat,org.lng FROM';
			q+='(SELECT '+agg+' AS val, org FROM authors WHERE org IS NOT NULL GROUP BY org) a, orgfinal org WHERE a.org=org.id AND org.lng IS NOT NULL';
			console.log(q); 
			client.query(q, function(err, result){
				if (!err && result){
					res.send(result.rows); 
				} else {
					res.send([]); 
				}
				done();
			});
		}
	}); 
});
app.post('/getClosest', function(req,res) {
	if (!req.body.lat || !req.body.lng || !req.body.zoom) res.send([]); 
	 var maxDist = 156543.03392 * Math.cos(req.body.lat * Math.PI / 180) / Math.pow(2, req.body.zoom);
         maxDist /= 5000;
	var subq = 'WITH click AS (SELECT ST_MakePoint('+req.body.lng+','+req.body.lat+') AS coord) '; 
	var q = 'SELECT * FROM orgfinal org, click WHERE ST_Distance(click.coord, ST_MakePoint(org.lat,org.lng))<'+maxDist + ' AND org.lng IS NOT NULL ORDER BY ST_Distance(click.coord, ST_MakePoint(org.lng,org.lat)) ASC LIMIT 5';
	q = subq + q;  
	postgres.connect(config.getDBAuth(), function(err, client, done){
		if (!err && client){
	client.query(q, function(err, result){
				if (!err && result){
					res.send(result.rows); 
				} else {
					res.send([]); 
				}
				done();
			});
		}
	}); 
}); 	

app.listen(80);
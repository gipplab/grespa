var express = require('express');
var compress = require('compression');
var bodyParser = require('body-parser');
var async = require('async');
var config = require('./config');
var cors = require('cors');
var g = require('geographiclib'); 
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

var geod = g.Geodesic.WGS84;
var Geodesic = g.Geodesic;

//generatePaths(); 
function generatePaths(){
	postgres.connect(config.getDBAuth(), function(err, client, done){
		if (!err && client){
			var geom;
			var vals = []; 
			var i ="INSERT INTO geodesicsfinal (org1,org2,path) VALUES "
			client.query("SELECT o1.id AS id1, o1.lat AS lat1, o1.lng AS lng1, o2.id AS id2, o2.lat AS lat2, o2.lng AS lng2 FROM (SELECT DISTINCT ON (least,greatest) a1.org AS least, a2.org AS greatest FROM coauthor c  JOIN authors as a1 ON c.author1=a1.id  JOIN authors as a2 ON c.author2=a2.id WHERE a1.org!= a2.org AND a1.org IS NOT NULL AND a2.org IS NOT NULL )b JOIN orgfinal as o1 ON b.least=o1.id  JOIN orgfinal as o2 ON b.greatest=o2.id", function(error,result){
				result.rows.forEach(function(o){
					geom = genGeom(o.lat1,o.lng1, o.lat2, o.lng2) 
					
					if (geom != "-1"){
						vals.push('('+o.id1+','+o.id2+','+geom+')'); 
					}
				});
				client.query((i+vals.toString()), function(e2, r2){
					console.log("error", e2); 
					done();
				});
				
				 
			}); 
		}	
	}); 
	
}

function genGeom(lng1,lat1,lng2,lat2) {
	    var r = geod.Inverse(lat1, lng1, lat2,lng2),
    l = geod.Line(r.lat1, r.lon1, r.azi1),
    s12 = r.s12; ds = 500e3, n = Math.ceil(s12 / ds);
    var i; 
	var s; 

var tmp = []; 
for (i = 0; i <= n; ++i) {
  s = Math.min(ds * i, s12);
  r = l.Position(s, Geodesic.STANDARD | Geodesic.LONG_UNROLL);
  tmp.push(r.lat2.toFixed(5) + ' '+r.lon2.toFixed(5))	
}
console.log(tmp); 
return (tmp.length>1) ? 'ST_GeomFromText(\'LINESTRING('+tmp.toString()+')\')' : '-1'; 
}



app.post('/suggestions', function(req, res){
	postgres.connect(config.getDBAuth(), function(err, client, done){
		if (!err && client){
				client.query('SELECT name AS label, id AS value FROM orgfinal WHERE name LIKE \'%'+req.body.q+'%\' LIMIT 5', function(error, result){
					res.send(error ? [] : result.rows);
					done(); 
				}); 
		} else {
			res.send([]);
			done(); 
		}
	}); 	
}); 
app.post('/initData', function (req, res) {
    postgres.connect(config.getDBAuth(), function(err, client, done){
		if (!err && client){
			var queryContainer = []; 
			var q1 = 'SELECT o.id, o.name,  o.lat,o.lng FROM orgfinal o WHERE o.lat IS NOT NULL';
			client.query(q1, function(error, result){
				  res.send((error) ? [] : result.rows);
                  done();
			}); 	
		} else {
			res.send([]);
			done(); 
		}
	});
}); 

app.post('/simpleData', function(req,res){
	postgres.connect(config.getDBAuth(), function(err, client, done){ 
		if (!err && client){
			client.query('SELECT * FROM co_helper WHERE org=\'' + req.body.org +'\'', function(error, result){
				res.send((error) ? [] : result.rows);
				done(); 
			}); 
		} else {
			res.send([]);
				done(); 
		}
	}); 
});

app.post('/getClosest', function(req,res){
		postgres.connect(config.getDBAuth(), function(err, client, done){ 
		if (!err && client){
			var tmp = req.body.selected.split(','); 
			var selected2= []; 
			tmp.forEach(function(d){
				selected2.push('\''+d +'\''); 
			});
			
			var maxDist = 156543.03392 * Math.cos(req.body.lat * Math.PI / 180) / Math.pow(2, req.body.zoom);
            maxDist /= 5000;
var q = 'SELECT CASE WHEN org1 IN ('+selected2.toString()+') THEN org2 ELSE org1 END AS id FROM (SELECT *, ST_Distance(ST_MakePoint('+req.body.lat+','+req.body.lng+'),path) AS dist FROM geodesics WHERE (org1 IN (' + selected2.toString() +') OR org2 IN (' + selected2.toString() +'))) a  WHERE dist <'+maxDist + ' ORDER BY dist ASC LIMIT 1'; 
	console.log('q',q); 
			client.query(q, function(error, result){
				res.send((error) ? [] : result.rows);
				done(); 
			}); 
		} else {
			res.send([]);
				done(); 
		}
	}); 
});  	

	

app.listen(80);
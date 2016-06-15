var pg = require('pg')
var GoogleLocations = require('google-locations');
var config = require('./config');

var locations = new GoogleLocations('AIzaSyDa1PmtA6Nq_TPNtZHwCqNlINCAhke2ph8');
pg.connect(config.getDBAuth(), function(err, client, done){
    if (err){
        console.log(err); 
        console.log('conn issue'); 
    } else { 
        var final = []; 
        client.query('SELECT id, name FROM org2 WHERE lat IS NULL', function(error, result){
            if (!error && result.rows.length>0){
                            var i = 0;                     
            function Loop() {           
               setTimeout(function () {    
					for (var j=i; j<i+10; j++){
                    setData(result.rows[j],client)    
					}
                  i+=10;                     
                  if (i < result.rows.length) {       
                     Loop()           
                  }                        
               }, 1100)
                    }
                Loop();    
            }
        }); 
    }
    done(); 
});



function setData(obj, client){
    locations.autocomplete({input:obj.name}, function(err, response) {
		console.log("err", err); 
		console.log("resp", response); 
        var success = function(err, res) {
		console.log("res",res); 
		console.log("err", err); 
            if (res && res.hasOwnProperty('result')){
			var add =  (res.result.hasOwnProperty('formatted_address')) ?  res.result.formatted_address : null; 
    var f=  {id:obj.id,add:add,lat:res.result.geometry.location.lat, lng:res.result.geometry.location.lng} ;
                                var q = 'UPDATE org2 SET addr= $1 ,lat='+f.lng+',lng='+f.lat+' WHERE id=\''+f.id+'\''; 
                               console.log(f)
                            client.query(q,[f.add], function(err, response){
                                console.log(err)
                            }); 
							}
  };
   if (response && response.predictions && response.predictions.length >0)  locations.details({placeid: response.predictions[0].place_id}, success);   
});
}
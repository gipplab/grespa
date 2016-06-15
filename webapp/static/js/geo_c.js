$(function () {
	
	var __wrapper = null; 
	
	var edgecache = {};
	var suggcache = {}; 
	
	var marker = null; 
	var lookup = {}; 
	__init(); 
	function __init(){
		__wrapper = {map: null, style: new MapStyle() }
	 					  
		__getInitData(function(){
			__createMap($('#map').get(0), 25.458333, 8.548056);  
		})
	}
	function __getInitData(cb){
		$.get("/geo_c/getInitData").done(function (data) {
			if (data.results.length>0){
				data.results.forEach(function(obj){
					lookup[obj.id]= obj;
					delete lookup[obj.id].id; 
				}); 
				cb();
			}
		}); 
	}
	function __getSimpleData(id, cb){ 
		$.post("/geo_c/getEdgeData/"+id).done(function (data) {
			if (data.results.length>0){
				cb(data.results);
			}
		}); 
	}
	function __createMap(obj, lat, lng){	 	
		var mapOptions = {
                zoom: 3,
                zoomControlOptions: {
                    style: google.maps.ZoomControlStyle.SMALL,
                    position: google.maps.ControlPosition.LEFT_TOP
                },
                minZoom: 2,
                maxZoom: 15,
                disableDefaultUI: true,
                zoomControl: true,
                center: new google.maps.LatLng(lat, lng),
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            __wrapper.map = new google.maps.Map(obj, mapOptions);
			__wrapper.map.setOptions({
                styles: __wrapper.style.getSheet()
			});

			 var info = new google.maps.InfoWindow({
				content: ''
			});
			function getSelected(){
					var res = [];
					$('#jlist select > option ').each(function(){
						res.push($(this).attr('orgid'));
					});
					return res;
				}
			function getSelected2(){
					var res = []; 
					$('#jlist select > option ').each(function(){
						res.push('\''+$(this).attr('orgid')+'\'');
					}); 
					return res; 
				}
				
			google.maps.event.addListenerOnce(__wrapper.map, 'idle', function(){
				$('#jlist').fadeIn(); 
				$('#search').fadeIn(); 
			}); 	
			google.maps.event.addListener(__wrapper.map, "rightclick", function(event){

				$.ajax({url:"/geo_c/getClosest",
					type: "POST",
					data: JSON.stringify({lat:event.latLng.lat(), lng:event.latLng.lng(), zoom: __wrapper.map.getZoom(), selected: getSelected2().toString()}, null, '\t'),
					dataType:'json',
					contentType: "application/json; charset=utf-8"}).done(function(data){

					if (data.results.length>0){
						if (lookup.hasOwnProperty(data.results[0].id)){
							var sel = getSelected(); 
							var count=-1; 
							for (var i= 0; i<sel.length; i++){
								for (var j=0; j<edgecache[sel[i]].length; j++){
									if (edgecache[sel[i]][j].get('target')==data.results[0].id) count = edgecache[sel[i]][j].get('count');
								}
							}
							var s = lookup[data.results[0].id].name + ((count!=-1) ? ('(' + count +')') : '');
							
							info.setContent(s);
							info.setPosition(event.latLng);
							info.open(__wrapper.map); 	
						}
					}			
				}); 
			}); 
			 __wrapper.map.controls[google.maps.ControlPosition.RIGHT_TOP].push($('#controlwrapper').get(0));
			 
			$('#search').autocomplete({
														source: function( request, response ) {
																	if (suggcache.hasOwnProperty(request.term)){ 
																		response(suggcache[request.term]); 
																	} else {
																		$.post("/geo_c/getSugg/"+request.term).done(function(data){
																			
																			suggcache[request.term] = data.results;
																			response(data.results);
																		});
																	}	
																		
																		
        
      },
      minLength: 3,
	  select: function(event, ui) {
		 
        event.preventDefault();
        $("#search").val(ui.item.label);
		$('#search').attr('orgid', ui.item.value);
		
		if (edgecache.hasOwnProperty(ui.item.value)){ 
			if (edgecache[ui.item.value].length > 0){
				if (!edgecache[ui.item.value][0].getMap()){
					$('#jlist select').prepend('<option orgid="'+ui.item.value+'">'+ui.item.label+'</option>'); 
					edgecache[ui.item.value].forEach(function(p){
						p.setMap(__wrapper.map); 
					});
				}
			} 
		} else { 
			$('#jlist select').prepend('<option orgid="'+ui.item.value+'">'+ui.item.label+'</option>'); 
			__getSimpleData(ui.item.value, function(d){
				__addEdges(d[0]); 
				
			}); 
		}
    },
    focus: function(event, ui) {
        event.preventDefault();
        
    }
	  
	  }); 
	  $('#delete').button({text:false}).click(function(event){
		  event.preventDefault(); 
		  var sel = $('#jlist select > option:selected'); 
		  if (sel.size()>0){ 
			var rel = sel.first(); 
			var orgid = rel.attr('orgid');
			if (edgecache.hasOwnProperty(orgid)){
				edgecache[orgid].forEach(function(p){
					p.setMap(null); 
				});
				rel.remove(); 
			}
		  }
	  }); 
	  $('#jlist select').on('click', 'option', function(){
		  var sel = $('#jlist select > option:selected'); 
			if (sel.size()>0 && __wrapper.map){
				var orgid = sel.attr('orgid');  
				if (lookup.hasOwnProperty(orgid)){
					var tmp = lookup[orgid];
					if (marker && marker.getMap()) marker.setMap(null); 
					marker = new google.maps.Marker({icon:'http://maps.google.com/mapfiles/ms/icons/blue-dot.png', position:{lat:tmp.lng, lng:tmp.lat},map:__wrapper.map, animation: google.maps.Animation.BOUNCE});
					setTimeout(function(){
					 marker.setMap(null); 
					}, 2000);  
				}
			} 
	  });   	  
	}
	function __addEdges(obj){ 
		if (lookup.hasOwnProperty(obj.org)){
		var src = lookup[obj.org];		
			var firstCoordinates = {lat:parseFloat(src.lng), lng:parseFloat(src.lat)};
			if (!edgecache.hasOwnProperty(obj.org)) edgecache[obj.org] = [];  
			for (var prop in obj.data){
				var tgt = lookup[prop]; 
				if (tgt){			
					var sndCoordinates = {lat:parseFloat(tgt.lng), lng:parseFloat(tgt.lat)}; 
					var polyline = new google.maps.Polyline({strokeColor:'#4AB6FF', clickable:false, count: obj.data[prop], source:obj.org, target:prop, strokeOpacity:0.7, strokeWeight:0.3, geodesic:true, path:[firstCoordinates,sndCoordinates]});
					edgecache[obj.org].push(polyline);
					polyline.setMap(__wrapper.map);  
				}
			}	
		} 
	}
	
	
});
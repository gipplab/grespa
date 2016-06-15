$(function () {	
	var __maindata = [];
	var __overlay = null;
	var __wrapper = null; 
	var __scale = null; 
	var layer = null; 
	var lookup = {};

	__init(); 
	function __init(){
		__wrapper = {map: null, style: new MapStyle() }
		$('#measures').selectmenu({change: function(event,ui){
											
											__getData(function(){
												if ($('#top td').length>0){ 
													$('#top td').each(function(i,el){
															 
															var id = $(this).attr('org');
															$(this).children('span').html(lookup[id][ui.item.index]); 
													}); 
												
												
												}
												var l = $('#legend').data('obj');
												var c = __scale.copy();
												l.setScale({type:'log', scale: c});
												
												
											},ui.item.index)		 
											  
											}
								  }); 
		$('#dotSize').slider({min:1, max:20, value:3, step:1, change: function(event,ui){
			if (layer){
				 layer.selectAll('.screen').selectAll('circle').attr('r', ui.value); 
			}
			
		}}); 					  
		__getData(function(){
		__createMap($('#map').get(0), 47.458333, 8.548056);
		},0); 
	}
	function __getData(cb,i){
		$.post("/geo_m/getData/"+i, {}, 'json').done(function (data) {
			if (data.results && data.results.length>0){
				__maindata = data.results;
				var ex = d3.extent(__maindata, function(d){return parseInt(d.val)}); 
				__scale = d3.scale.log().base(2.7).domain([10, ex[1]]).range(['black','#74B3E8']);
				__maindata.forEach(function(obj){

					if (!lookup.hasOwnProperty(obj.id)) lookup[obj.id] = {}; 
						
					lookup[obj.id][i]= obj.val; 
					
					
					//possibly clean lookup before...
				}); 
				if (layer){
											var test =	layer.selectAll('.screen').data(__maindata);
											test.selectAll('circle').style("fill", function(){
						var d= d3.select(this.parentNode).data()[0]
						 
						d3.select(this).data(d); 
						
						return __scale(parseInt(d.val));
						}); 			
											}
				cb();
			}
		}); 
	}
	function __createMap(m, lat, lon){	 	
		var mapOptions = {
                zoom: 3,
                zoomControlOptions: {
                    style: google.maps.ZoomControlStyle.SMALL,
                    position: google.maps.ControlPosition.LEFT_TOP
                },
                minZoom: 3,
                maxZoom: 15,
                disableDefaultUI: true,
                zoomControl: true,
                center: new google.maps.LatLng(lat, lon),
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            __wrapper.map = new google.maps.Map(m, mapOptions);
				
			__wrapper.map.setOptions({
                styles: __wrapper.style.getSheet()
			});
			google.maps.event.addListenerOnce(__wrapper.map, 'idle', function(){
				$('#search').fadeIn();
				$('#measureWrapper').fadeIn();
			}); 
			google.maps.event.addListener(__wrapper.map, "rightclick", function(event){

				//$.ajax is needed here because it allows application/json; charset=utf-8", which is needed to get data @backend
				$.ajax({url:"/geo_m/getClosest",
					type: "POST",
					data: JSON.stringify({lat:event.latLng.lat(), lng:event.latLng.lng(), zoom: __wrapper.map.getZoom()}, null, '\t'),
					dataType:'json',
					contentType: "application/json; charset=utf-8"}).done(function(data){
					if (data.results && data.results.length>0){
					
						var i = $('#measures option:selected').index();
						var res = ''; 
						data.results.forEach(function(d){
						res+=('<tr><td org="'+d.id+'">'+d.name+ '(<span>' + lookup[d.id][i]+'</span>)</td></tr>'); 	
						});
						$('#top table').html(res); 
					}			
				}); 
					
				
				
			});
		    new spatLegend('#legend');
			__wrapper.map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push($('#legendwrapper').get(0));
			$('#legendwrapper').fadeIn();
			var l = $('#legend').data('obj');
			var c = __scale.copy();
			l.setScale({type:'log', scale: c});
			  var input = $('#search').get(0);
			  var searchBox = new google.maps.places.SearchBox(input);
			  __wrapper.map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
			  __wrapper.map.controls[google.maps.ControlPosition.TOP_RIGHT].push($('#measureWrapper').get(0));
			  searchBox.addListener('places_changed', function() {
				  var bounds = new google.maps.LatLngBounds();
				  bounds.extend(searchBox.getPlaces()[0].geometry.location);
				  __wrapper.map.fitBounds(bounds); 
			  }); 
			
			__overlay = new google.maps.OverlayView(); 
			__overlay.onAdd = function(){
				layer = d3.select(this.getPanes().overlayMouseTarget).append('div').attr('class', 'unis'); 
				__overlay.draw = function(){
					
					var proj= this.getProjection();		
					var newdata = layer.selectAll('.screen').data(__maindata);
					
					newdata.each(setPos) //UPDATE
					var enter = newdata.enter().append('svg').attr('class', 'screen').each(setPos) //ENTER
					enter.append("circle")
						 .attr("r", 3)
				         .attr("cx", 20)
				         .attr("cy", 20)
						 .attr('class', 'fu')
				         .style('fill',function(d){ 
							 return __scale(d.val)})
				         .style('opacity',0.7).style('stroke','steelblue').style('stroke-width',0.5);

		    
			function setPos(d) {			
				d = new google.maps.LatLng(d.lng, d.lat);
				d = proj.fromLatLngToDivPixel(d);
				return d3.select(this)
					   .style("left", (d.x - 18) + "px")
					   .style("top", (d.y - 18) + "px");
			}
				}
				
			}
			__overlay.setMap(__wrapper.map);  
	}
});
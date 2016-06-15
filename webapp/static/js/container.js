var Container = function (pDiv,pclass, measure,  clickFunc, hoverFunc) {
    var public = this;

    var __div;

	var __class; 
    var __nodeData;
    var __nodeIDs;
    var __nodeUndo; 
    var __linkData;
    var __linkLookup; 
    var __nodeLookup;
    var __nodeVis;
    var __linkVis;

	
    var __canvas;
    var __colorScale;
	var __legendScale; 
	var __scaleGradientStop1;
	var __scaleGradientStop2;
	var __legendAxis;
	var __legendAxisVis; 
    var __force;
	
	var __maxima={author:{}, fos:{}, uni:{}}; 
	var __measure = measure; 

    function __init() {
		var fields = {author:9, fos:4, uni:4}; 
		Object.keys(__maxima).forEach(function(key){
			for (var i= 0; i<fields[key]; i++){ 
				__maxima[key][i] = 0; 
			}
		});
		__class = pclass; 
        __div = pDiv;
        
        __nodeData = [];
        __linkData = [];
        
        __linkLookup = {}; 
        __nodeLookup = {};
        
        __nodeUndo = [];  
        __nodeRedo = []; 
        
        __initGraphics()
    }

    function __initGraphics() {
        var rect = d3.select(__div).node().getBoundingClientRect();
        var svg = d3.select(__div).append('svg')
            .attr("preserveAspectRatio", "none")
            .attr("viewBox", "0 0 " + rect.width + " " + rect.height)
            .attr("class", "svsgResponsive").on('contextmenu', function(){
            });
		__colorScale = d3.scale.linear().domain([0,50]).range(['#FFFFFF', '#FF6600']); 
         var nodeGradient = svg.append("defs")
        .append("linearGradient")
    .attr("id", "nodeGradient")
    .attr("x1", "27%")
    .attr("y1", "100%")
    .attr("x2", "73%")
    .attr("y2", "0%")
    .attr("spreadMethod", "pad");
nodeGradient.append("stop")
    .attr("offset", "0%")
    .attr("stop-color", "rgb(150,150,150)")
    .attr("stop-opacity", 1);
nodeGradient.append("stop")
    .attr("offset", "100%")
    .attr("stop-color", "rgb(20,20,20)")
    .attr("stop-opacity", 1);
	
	var scaleGradient = svg.append('defs')
						   .append("svg:linearGradient")
						   .attr("id", "scaleGradient")
						   .attr("x1", "0%")
						   .attr("y1", "100%")
						   .attr("x2", "100%")
						   .attr("y2", "100%")
						   .attr("spreadMethod", "pad");
	 __scaleGradientStop1= scaleGradient.append("stop").attr("offset", "0%").attr("stop-opacity", 1)
     __scaleGradientStop2 = scaleGradient.append("stop").attr("offset", "100%").attr("stop-opacity", 1)
    svg.append('rect').attr('width', '100%').attr('height', '100%').style('fill', 'url(#nodeGradient');
    __legendAxis = d3.svg.axis().orient("bottom").ticks(4);
    __legendAxisVis = svg.append("g").attr("class", "x axis2").attr('transform', 'translate(6,8)');				   
	svg.append('rect').attr('width', '220px').attr('height', '10px').style("fill", "url(#scaleGradient)").attr('transform', 'translate(6,0)');
	__updateLegend(); 
		
	   svg.append('svg:defs').append('svg:marker')
    .attr('id', 'arrows')
.attr("viewBox", "0 -3 6 6")
    .attr("refX", 5.0)
    .attr("refY", 0.0)
    .attr("markerWidth", 5)
    .attr("markerHeight", 5)
    .attr("orient", "auto")
  .append("svg:path")
	.attr('fill', 'white')
    .attr("d", "M0,-2.0L5,0L0,2.0");  

 
        __canvas = svg.append('g');
        svg.call(d3.behavior.zoom().on("zoom", function(){
        __canvas.attr('transform', "translate("+d3.event.translate+"), scale(" + d3.event.scale + ")");    
        })).on("dblclick.zoom", null);
        
        
       
        __force = d3.layout.force()
            .linkStrength(2)
            .distance(120)
            .charge(-2500)
            .size([rect.width, rect.height])
            .on('tick', __tick);
        __nodeData  = __force.nodes();
        __linkData =  __force.links(); 
        __force.drag()
            .on("dragstart", function (d) {
           d3.event.sourceEvent.stopPropagation(); 
                __nodeData.forEach(function (di) {
                    di.fixed = false;
                });
                d.fixed = true;
            });
    }

    function __tick() {
        __nodeVis.attr("transform", function (d) {
            return 'translate(' + d.x + ',' + d.y + ')';
        });
        __linkVis.attr('d',  function(d) {
       var dx = d.target.x - d.source.x,
        dy = d.target.y - d.source.y,
        dr = Math.sqrt(dx * dx + dy * dy)/4,
        mLx = d.source.x + dx/2,
        mLy = d.source.y + dy/2,
        mAx = d.source.x + dx,
        mAy = d.source.y + dy;
	if (d.directed){
       return [ //edge with arrow
          "M",d.source.x,d.source.y,
           "L",mLx,mLy,
           "L",d.target.x,d.target.y,
           "Z"
          ].join(" ");
		} else {
		return [ //edge without arrow
		   "M",d.source.x,d.source.y,
           "L",d.target.x,d.target.y,
           "Z"
          ].join(" ");
		}
  });
       
    }
    function getNode(id){
        for (var i= 0; i<__nodeData.length; i++){
            if (__nodeData[i]['id'] == id) return i;
        }
        return -1;      
    }
    
    function __removeNodes(objs){
        if (objs.length<1) return;  
        var index; 
        objs.forEach(function(obj){
            index = getNode(obj.id); 
            if (index !== -1){
                __nodeData.splice(index,1); 
                delete __nodeLookup[obj.id]; 
                for (var i= __linkData.length-1; i>=0; i--){
                    if (__linkData[i].source.id == obj.id || __linkData[i].target.id == obj.id){
                        delete __linkLookup[__linkData[i].source.id+'-'+__linkData[i].target.id];
                         __linkData.splice(i,1);
                    }
                }
            }
        }); 
        __updateGraphics();
		
		__maxima[__class][__measure] = 0; 
		__updateMaximum(); 
        __force.start();   
    }
    
    function __updateGraphics(){
        __linkVis = __canvas.selectAll('path').data(__linkData)
        __linkVis.enter().append('path').attr('class', 'link').attr('marker-mid', 'url(#arrows)'); 
        __linkVis.exit().remove();
         
        __nodeVis = __canvas.selectAll('.nodeContainer').data(__nodeData, function(d){return d.id}); 
        var nodeEnter = __nodeVis
            .enter().append('g').attr('class', 'nodeContainer').call(__force.drag);
        nodeEnter.append('circle').attr('r', 35).attr('stroke', 'white').attr('fill', function(d){return __colorScale(d.measures[measure])});
        
        nodeEnter.append('rect').attr('width', 68).attr('height', 20).attr('transform', 'translate(-34,-10)').attr('fill', 'white').attr('opacity', 0.9).attr('stroke', 'none');
        nodeEnter.append('text').attr('transform', 'translate(0,4)').text(function (d) {
           /* if (d.addLabel){
                return d.addLabel;
            }*/
            return d.name;
        });
       
        __nodeVis.on('click', function (d) {
             if (d3.event.defaultPrevented) return;
                var that = this; 
               clickFunc({clicked:d.id, all:__nodeIDs.toString()});
            
                d3.select(that).select(' circle').attr('stroke', function(){
                    if (d3.select(this).attr('stroke') === 'white'){
                         d3.selectAll('.nodeContainer').select(' circle').attr('stroke', 'white'); 
                         return 'steelblue';
                        
                    } else { 
                        return 'white'; 
                    }
                    
                })     
        }).on('mouseenter', function(d){
            hoverFunc.enter(d);  
        }).on('mouseleave', function(d){
            hoverFunc.leave(d); 
        }); 
        __nodeVis.exit().remove();
        
       __canvas.selectAll('.nodeContainer').each(function(){
           this.parentNode.appendChild(this); 
       }); 
        __nodeIDs=[];
        __nodeData.forEach(function(node){
            __nodeIDs.push(node.id); 
        });
    }
    function __addNodes(newNodes,clicked, addLabel) {
        if (newNodes.length<1) return; 
        //index nodes by ID
        var expansions = [];  
        newNodes.forEach(function(n){ 
            if (!__nodeLookup.hasOwnProperty(n.id)){
                n.addLabel = addLabel;
                __nodeData.push(n);
                expansions.push(n); 
                __nodeLookup[n.id]=42; //dont care
            }
        }); 
        if (expansions.length>0) __nodeUndo.push({clicked:clicked, arr:expansions}); 
        newNodes.forEach(function(n){
             if (n.hasOwnProperty('links')){
                n.links.forEach(function(l){
                    var src = Math.min(l,n.id); 
                    var tar = Math.max(l,n.id);
                    if (!__linkLookup.hasOwnProperty(src+'-'+tar)){
                        var srctmp = getNode(src);
                        var tartmp = getNode(tar);
						
                        if (srctmp !== -1 && tartmp !== -1){
                            __linkLookup[src+'-'+tar] = 42; //dont-care-value  
							var finallink = {source: getNode(src), target: getNode(tar), directed: false};
							if (clicked) { 
							if (clicked == src) finallink = {source: getNode(src), target: getNode(tar), directed: true};
							if (clicked == tar) finallink = {source: getNode(tar), target: getNode(src), directed: true};
							}
                            __linkData.push(finallink);
                        }
                    }
                }); 
                //delete n.links;
             } 
         }); 
        __updateGraphics();  
		__updateMaximum(); 
        __force.start(); 
        
    } 
	function __updateMaximum() {
		__nodeData.forEach(function(node){
				if (node.measures[__measure]>__maxima[__class][__measure]) __maxima[__class][__measure] =  node.measures[__measure];  
		}); 
		public.setColor(__colorScale.range()[1]); 
	}
	function __updateLegend(){ 
		var copy = __colorScale.copy(); 
		__scaleGradientStop1.attr("stop-color", copy.range()[0]);
        __scaleGradientStop2.attr("stop-color", copy.range()[1]);
	    var legendScale = copy.range([0, 220]); //further parameters get set in updateGraphics()
        __legendAxis.scale(legendScale);
        __legendAxisVis.call(__legendAxis);
	}

    public.addNodes = function (arr,clicked, addLabel) {
        __addNodes(arr,clicked, addLabel);
    }

    public.clear = function () {
        __linkVis.remove();
        __nodeVis.remove();

        __linkData = [];
        __nodeData = [];
        __force.nodes([]).links([]);
    };
    public.undo = function(){ 
        var rel = __nodeUndo.pop(); 
        if (rel && rel.arr.length>0){
            __nodeRedo.push(rel); 
            __removeNodes(rel.arr);
        }
    } 
    public.redo = function(){
        var rel = __nodeRedo.pop(); 
        if (rel && rel.arr.length>0){
        __addNodes(rel.arr,rel.clicked);
        }
    }
    public.setColor = function(hex){ 
        __colorScale.domain([0, __maxima[__class][__measure]]).range(['#FFFFFF',hex]); 
        __canvas.selectAll('.nodeContainer circle').attr('fill', function(d){return __colorScale(d.measures[__measure])})
        __updateLegend(); 
    } 
	public.setMeasure = function(index){ 
		__measure = index; 
		__maxima[__class][__measure] = 0; 
		__updateMaximum(); 
	}
	
    __init()


}
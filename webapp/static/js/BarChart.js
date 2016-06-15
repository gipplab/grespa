var BarChart = function(pCanvas, pDataIndex){
	var public = this;
	
    //private variables
    //assignment, if independent from constructor
    var dims;
    var width;
    var focusHeight;
    var contextHeight = 40;
    var upperMargin = 50;
    var middleMargin = 23;
    var lowerMargin = 30;
    var paddingsHor = 55;
	
	var focus; 
	var context; 
	var brush; 
	var tooltip; 

	var xScale; 
	var x2Scale; 
	var xAxis; 
	var x2Axis; 
	var yScale; 
	var y2Scale; 
	var yAxis; 
	
	var mainData;
    var dataIndex;
	function __constructor(){
		dims = d3.select(pCanvas).node().getBoundingClientRect();
        width = dims.width - 2 * 60;
        focusHeight = dims.height - upperMargin - middleMargin - contextHeight - lowerMargin;


        __requestData(function(data){
            if (data.length > 0){
                mainData = data;
                dataIndex = pDataIndex;
                //preprocess dates
                for (var i=0; i<mainData.length; i++){
                    for (var j=0; j<mainData[i].length; j++){
                        mainData[i][j].year = new Date(mainData[i][j].year,0,1);
                    }
                }
                __initGraphics();
				$(pCanvas).data('obj', public);
            }
        }); 

        function __requestData(callback){
        $.post("/getTimeSeries", {}, 'json').done(function (data) {
            callback((data.errors.length>0) ? data.errors : data.results);
        });
        }

	}
	
	function __initGraphics(){ 
		var svg = d3.select(pCanvas).append('svg')
                .attr('height', dims.height).attr('width', '100%'); 
			svg.append('rect').attr('width', '100%').attr('height', '100%')
                .attr('fill', '#000318');
			tooltip = d3.tip()
                .attr('class', 'tooltip')
                .offset([-10, 0])
                .html(function (d) {
                    return 'Count: ' + d.count + '<br>Year: ' + d.year.getFullYear();
                });
            svg.call(tooltip);
			            svg.append('defs').append('svg:clipPath').attr('id', 'clip').append('rect').attr('width', width).attr('height', focusHeight);

            //prepare svg for the timescales
            focus = svg.append('g')
                .attr('transform', 'translate(' + paddingsHor + ',' + upperMargin + ')').attr('class', 'focus');
            focus.append('g')
                .attr('class', 'x axis')
                .attr('transform', 'translate(0,' + focusHeight + ')');
            focus.append('g')
                .attr('class', 'y axis')
                .append('text')
                .attr('class', 'y tlabel')
                .text('#');

            focus.append('g').attr('clip-path', 'url(#clip)').attr('class', 'focusCanvas'); //clipPath from above
            context = svg.append('g')
                .attr('transform', 'translate(' + paddingsHor + ',' + (focusHeight + upperMargin + middleMargin) + ')').attr('class', 'context');
            context.append('rect')
                .attr('width', width)
                .attr('height', contextHeight)
                .attr('id', 'contextBg')
                .attr('stroke', 'white')
                .attr('fill', 'none');
            context.append('g')
                .attr('class', 'x axis')
                .attr('transform', 'translate(0,' + contextHeight + ')')

            //initialise time scales, axis and call the axis on the visual components, created before

             var extent = d3.extent(mainData[dataIndex], function(d){
                return d.year;
            });
			
            xScale = d3.time.scale().range([0, width]);
            x2Scale = d3.time.scale().domain(extent).range(xScale.range());
            xAxis = d3.svg.axis().scale(xScale).orient('bottom')
            x2Axis = d3.svg.axis().scale(x2Scale).orient('bottom'); 
            focus.selectAll(".x.axis").transition().duration(750).call(xAxis);
            context.selectAll(".x.axis").transition().duration(750).call(x2Axis);

            //d3 brushing
            brush = d3.svg.brush()
                .x(x2Scale)
                .on('brush', function () {
                    var domain = brush.empty() ? x2Scale.domain() : brush.extent();
                    __setExtent(domain);
                });



            __setExtent([new Date(1960,0,1), extent[1]]);


			 context.append('g')
                .attr('class', 'x brush')
                .attr('id', 'brushDrag')
                .call(brush)
                .selectAll("rect")
                .attr('height', contextHeight);
        __updateGraphics();
	}
    function __setExtent(pDomain){
                    brush.extent(pDomain);
                    xScale = xScale.domain(pDomain);
					xAxis.scale(xScale);
					focus.selectAll('rect').attr('transform', function (d) {
																return 'translate(' + xScale(d.year) + ',0)';
																});
					focus.selectAll('.x.axis').call(xAxis);
					focus.selectAll('.bar').attr("width", function (d) {
																		return  (xScale(new Date(1971, 0, 1)) - xScale(new Date(1970, 0, 1)))+0.4;
					});
					d3.select('#brushDrag').call(brush);
    }
	function __updateGraphics(){
        //do we need to update the focus' x axis?
        var tmpExtent = d3.extent(mainData[dataIndex], function(d){
                return d.year;
            });
        if (xScale.domain() && (tmpExtent[0].getTime() == xScale.domain()[0].getTime() || tmpExtent[1].getTime() == xScale.domain()[1].getTime() )){
        } else {
           __setExtent(tmpExtent);
        }

		var domain = [d3.min(mainData[dataIndex], function (d) { return d.count;}), d3.max(mainData[dataIndex], function (d) { return d.count;})];
		yScale = d3.scale.linear().domain(domain).range([focusHeight, 0]);
        y2Scale = d3.scale.linear().domain(yScale.domain()).range([contextHeight, 0]);
        yAxis = d3.svg.axis().scale(yScale).orient('left').innerTickSize(-width).outerTickSize(0);

        focus.selectAll(".y.axis").transition().duration(750).call(yAxis);

        var focusRects = focus.select('.focusCanvas').selectAll('.bar').data(mainData[dataIndex]);
        focusRects.enter().append('rect').attr('class','bar')
		.on('mouseenter', function(d){tooltip.show(d)})
		.on('mousemove', function(d){tooltip.show(d)})
		.on('mouseleave', function(d){tooltip.hide(d)});
        focusRects.exit().remove();

        focusRects.attr('transform', function (d) {
            return 'translate(' + xScale(d.year) + ',0)';
        }).attr('width', function (d) {
            return  (xScale(new Date(2015, 0, 1)) - xScale(new Date(2014, 0, 1)));
        });

        focusRects.transition().duration(700)
            .attr('height', function (d) {
                return focusHeight - yScale(d.count);
            })
            .attr('y', function (d) {
                return yScale(d.count);
            })
            .attr('fill', function (d) {
                return 'steelblue';
            });

			
        var contextRects = context.selectAll('.bar')
            .data(mainData[dataIndex]);

        contextRects.enter().append('rect').attr('class', 'bar')
        contextRects.exit().transition().duration(700).remove();
		
        contextRects.attr('transform', function (d) {
            return 'translate(' + x2Scale(d.year) + ',0)'
        });
		
        contextRects.transition().duration(700).attr('width', function (d) {
                return 0.9999 * (x2Scale(new Date(1971, 1, 1)) - x2Scale(new Date(1970, 1, 1)))
            })
            .attr('height', function (d) {
                return  contextHeight - y2Scale(d.count);
            })
            .attr('y', function (d) {

                return y2Scale(d.count);
            })
            .attr('fill', function (d) {
                return 'steelblue'
            });

        context.node().appendChild(d3.select('#brushDrag').node()); //bring brush to front
	}
    public.setDataIndex = function(i){
        dataIndex = i;
        __updateGraphics();
    }

	__constructor(); 


}
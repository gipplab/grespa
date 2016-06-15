var Diff = function(pCanvas, pData, categories){

var __svg; 
var __data; 
var __height =300;
var __width = 500;
function __constructor(){
	__data = pData;
	console.log(__data);
	__canvas = pCanvas; 
	__initGraphics(); 
}

function __initGraphics(){
__svg = d3.select(__canvas).append('svg').attr('height', '320px').attr('width', '500px');
__svg.append('rect').attr('width', '500px').attr('height', '320px').attr('fill', 'white').attr('stroke','black');
var tooltip = d3.tip()
                .attr('class', 'tooltip')
                .offset([-10, 0])
                .html(function (d) {
                    return  d;
                });
	__svg.call(tooltip); 
var inner = __svg.append('g').attr('transform', 'translate(100,20)');
	inner.append('g')
                .attr('class', 'x axis3')
                .attr('transform', 'translate(0,' + (__height-40) + ')');
    inner.append('g')
                .attr('class', 'y axis3')
				.attr('transform', 'translate(0,0)')
                .append('text')
                .attr('class', 'y blabel')
                .text('#');
	var xScale = d3.time.scale().domain([0,__data.first.length+1]).range([0, __width-200]);
	var xAxis = d3.svg.axis().scale(xScale).orient('bottom')
	__svg.selectAll(".x.axis3").transition().duration(750).call(xAxis);

	__svg.selectAll('.x.axis3').selectAll('text').remove();
	
	var max1 = d3.max(__data.first, function(d){ return d; });
	var max2 = d3.max(__data.second, function(d){ return d; });
	var yScale = d3.scale.linear().domain([0, Math.max(max1,max2)+1]).range([__height-40, 0]);
	var yAxis = d3.svg.axis().scale(yScale).orient('left').outerTickSize(0);
	__svg.selectAll(".y.axis3").transition().duration(750).call(yAxis);

	var firsts = inner.selectAll('.firstRects').data(__data.first)
	var g = firsts.enter().append('g').attr('class', 'firstRects');
	var fRect = g.append('rect');
	fRect.on('mouseenter', function(d){tooltip.show(d)})
		.on('mousemove', function(d){tooltip.show(d)})
		.on('mouseleave', function(d){tooltip.hide(d)});
	g.append('text').text(function(d,i){
			console.log('i:'+i)
			return categories[i].label
	});
	firsts.exit().remove();
	g.attr('transform', function (d,i) {
            return 'translate(' + (xScale(i+0.75)) + ',0)';
        });
			fRect.attr('width', function (d) {
            return  (xScale(1) - xScale(0))/2;
        });

        fRect.transition().duration(700)
            .attr('height', function (d) {
                return __height-40 - yScale(d);
            })
            .attr('y', function (d) {
                return yScale(d);
            })
            .attr('fill', function (d) {
                return 'steelblue';
            });

		var seconds = inner.selectAll('.sndRects').data(__data.second)
	var g2 = seconds.enter().append('g').attr('class', 'sndRects')
	var sRect = g2.append('rect');
	sRect.on('mouseenter', function(d){tooltip.show(d)})
		.on('mousemove', function(d){tooltip.show(d)})
		.on('mouseleave', function(d){tooltip.hide(d)});
	seconds.exit().remove();
	g2.attr('transform', function (d,i) {
            return 'translate(' + (xScale(i+0.75) + (xScale(1) - xScale(0))/8) + ',0)';
        });
			sRect.attr('width', function (d) {
            return  (xScale(1) - xScale(0))/4;
        });

	sRect.transition().duration(700)
            .attr('height', function (d) {
                return __height-40 - yScale(d);
            })
            .attr('y', function (d) {
                return yScale(d);
            })
            .attr('fill', function (d,i) {
                return 'lightblue'
            });

}

__constructor();

}
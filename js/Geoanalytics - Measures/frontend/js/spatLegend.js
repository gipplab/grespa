/*
    COPYRIGHT Philipp Meschenmoser, University of Konstanz. 2015.
    
    

    This file is part of Aquila.

    Aquila is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Aquila is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

*/

var spatLegend = function (pContainer) {
    var public = this;
    var scale = null;
    var scaletype = '';
    var init = false;
    var container;
    var svg;
    var gradient;
    var stop1;
    var stop2;
    var legendScale;
    var legendAxis;


    function constructor(pContainer) {
        container = pContainer;
        initGraphics();
        $(container).data('obj', public);
    }

    function initGraphics() {
        svg = d3.select(container).append('svg').attr("width", '100%').attr("height", '100%');
        gradient = svg.append('defs').append("svg:linearGradient").attr("id", "spatGradient").attr("x1", "0%").attr("y1", "100%").attr("x2", "100%").attr("y2", "100%").attr("spreadMethod", "pad");
        stop1 = gradient.append("stop").attr("offset", "0%").attr("stop-opacity", 1);
        stop2 = gradient.append("stop").attr("offset", "100%").attr("stop-opacity", 1);
        svg.append('rect').attr('width', '220px').attr('height', '10px').style("fill", "url(#spatGradient)").attr("transform", "translate(3,0)");
        legendAxis = d3.svg.axis().orient("bottom").ticks(4);
        legendAxisVis = svg.append("g").attr("class", "x axis2").attr("transform", "translate(3,10)");
    }

    function labelCollision() {
        var bbs = []
        var sel = legendAxisVis.selectAll('text').each(function (d, i) {
            d3.select(this).attr('transform', 'translate(0,0)'); //reset labels positions
            if (d3.select(this).text().length > 0) bbs.push({
                index: i,
                dom: this
            });
        });
        var doShift = false;
        var shiftArr = [];

        for (var i = 1; i < bbs.length; i++) {
            if (doShift) {
                //doShift is set, when the last label collided with the label before. So, when the last 
                // label has to be shifted downwards, you dont need to look at the current label wrt 
                //collision detection. Thus, skip.
                doShift = false;

            } else {
                var lastBB = bbs[i - 1].dom.getBoundingClientRect();
                var thisBB = bbs[i].dom.getBoundingClientRect();
                if (lastBB.right +5 >= thisBB.left) {
                    d3.select(bbs[i].dom).attr('transform', 'translate(0,4)');
                    shiftArr.push(i);
                    doShift = true;

                }
            }
        }
        if (shiftArr.length > 0) {
            for (var i = 0; i < bbs.length; i++) { //shift every label, which was not shifted downwards, upwards.
                if (shiftArr.indexOf(i) === -1) d3.select(bbs[i].dom).attr('transform', 'translate(0,-4)');
            }
        }
		d3.select('.domain').remove(); //from where do we have that element...
    }

    public.setScale = function (pScaleObj) {
        //pScale = {type:'pow', scale:function...}
        scale = pScaleObj.scale;
        scaletype = pScaleObj.type;
		
        stop1.attr("stop-color", scale.range()[0]).attr("stop-opacity", 1);
        stop2.attr("stop-color", scale.range()[1]).attr("stop-opacity", 1);
        legendScale = scale.range([0, 220]); //further parameters get set in updateGraphics()
        legendAxis.scale(legendScale);

        //both formats show numbers such as 10k. 
        //however, another format for log scales was needed, 's' was not enough.
		if (scaletype === 'log') {

            legendAxis.tickFormat(function (d) {
                return legendScale.tickFormat(4, d3.format(".1f"))(d); //else: it would show up in 4E10 e.g.
            });
			
        } else {
            legendAxis.tickFormat(d3.format('s'));
        }

        legendAxisVis.call(legendAxis);
//        if (scaletype === 'log') svg.select('.tick').remove();
        labelCollision();
    }
    constructor(pContainer);
}
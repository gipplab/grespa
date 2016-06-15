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

var MapStyle = function () {
    var public = this;
    var sheet; //current sheet

    function constructor() {
        sheet = public.getDefault();
    }

    public.getDefault = function () {
        return [
            {
                //basic map styles
                stylers: [
                    {
                        "saturation": -100 //-40
                },
				/*
					standard lightness: 30%
					-> lightness values specified by the slider in 
					domain of [-90,10]
				*/
                    {
                        "lightness": -25
                },
                    {
                        "hue": "#00000" //"#0066ff"
                },
                    {
                        "gamma": 0.2 //0.85
                }
                           ]
                },
                //basic feature styles   
            {
                featureType: "road",
                stylers: [{
                    visibility: "off"
            }]
                },
            {
                featureType: "administrative",
                stylers: [{
                    visibility: "off"

            }]
                },

                //display labels 
            {
                featureType: "administrative.country",
                stylers: [{
                            weight: 1.5
                }, {
                            visibility: "on"
                        },
					//{ invert_lightness: true } white borders when whole globe is darkened? could get discussed.
                ] //additional: extra weight for country borders
                },
            {
                featureType: "administrative.locality",
                elementType: "labels",
                stylers: [{
                        visibility: "off"
            },
                    {
                        invert_lightness: true
                    }
			]
                },
            {
                featureType: "administrative.country",
                elementType: "labels",
                stylers: [{
                        visibility: "off"
            },
                    {
                        invert_lightness: true
                    }]
                },
            {
                featureType: "water",
                elementType: "labels",
                stylers: [{
                        visibility: "off"
            },
                    {
                        invert_lightness: true
                    }
			]
                },

            {
                featureType: "poi", //points of interest
                elementType: "labels",
                stylers: [{
                    visibility: "off"
            }, {
                    invert_lightness: true
                }]

                },
            {
                featureType: "landscape", //hide labels & icons for mountains and man-mades...
                elementType: "labels", //hiding the features completely looks very weird 
                stylers: [{
                        visibility: "off",
            },
                    {
                        invert_lightness: true
                    }]
                }
            ]
    }

    public.setLightness = function (val) {
        sheet[0].stylers[1]["lightness"] = val;
    }

    public.setLabelsVisible = function (bool) {
        for (var i = 4; i < sheet.length; i++) sheet[i].stylers[0]["visibility"] = (bool) ? "on" : "off";
    }
    public.getSheet = function () {
        return sheet;
    }
    constructor();
}
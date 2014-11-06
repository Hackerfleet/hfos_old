'use strict';


/**
 * @ngdoc function
 * @name frontendApp.controller:MapCtrl
 * @description
 * # MapCtrl
 * Controller of the frontendApp
 */
angular.module('frontendApp')
  .controller('MapCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];

    console.log('Hallo angularscope!');

    $scope.init = function() {
        console.log('Hello Mapviewer!');

        L.RotatedMarker = L.Marker.extend({
          options: { angle: 0 },
          _setPos: function(pos) {
            L.Marker.prototype._setPos.call(this, pos);
            if (L.DomUtil.TRANSFORM) {
              // use the CSS transform rule if available
              this._icon.style[L.DomUtil.TRANSFORM] += ' rotate(' + this.options.angle + 'deg)';
            } else if (L.Browser.ie) {
              // fallback for IE6, IE7, IE8
              var rad = this.options.angle * L.LatLng.DEG_TO_RAD,
              costheta = Math.cos(rad),
              sintheta = Math.sin(rad);
              this._icon.style.filter += ' progid:DXImageTransform.Microsoft.Matrix(sizingMethod=\'auto expand\', M11=' +
                costheta + ', M12=' + (-sintheta) + ', M21=' + sintheta + ', M22=' + costheta + ')';
            }
          }
        });
        L.rotatedMarker = function(pos, options) {
            return new L.RotatedMarker(pos, options);
        };

        var Coords = [0,0];
        var Course = 0;
        var Radiorange = 700;
        var RangeDisplay = false;

        var editingRoute = false;
        var routeLayers = {};
        var cm;

        L.Polyline.include(L.Mixin.ContextMenu);

        var VesselIcon = L.icon({
            iconUrl: '/assets/icons/vessel.png',
            //shadowUrl: 'leaf-shadow.png',

            iconSize:     [25, 25], // size of the icon
            //shadowSize:   [50, 64], // size of the shadow
            iconAnchor:   [12, 12], // point of the icon which will correspond to marker's location
            //shadowAnchor: [4, 62],  // the same for the shadow
            popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
        });

        var VesselMovingIcon = L.icon({
            iconUrl: '/assets/icons/vessel-moving.png',
            //shadowUrl: 'leaf-shadow.png',

            iconSize:     [25, 25], // size of the icon
            //shadowSize:   [50, 64], // size of the shadow
            iconAnchor:   [12, 12], // point of the icon which will correspond to marker's location
            //shadowAnchor: [4, 62],  // the same for the shadow
            popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
        });

        var VesselStoppedIcon = L.icon({
            iconUrl: '/assets/icons/vessel-stopped.png',
            //shadowUrl: 'leaf-shadow.png',

            iconSize:     [25, 25], // size of the icon
            //shadowSize:   [50, 64], // size of the shadow
            iconAnchor:   [12, 12], // point of the icon which will correspond to marker's location
            //shadowAnchor: [4, 62],  // the same for the shadow
            popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
        });

        // TODO: This is madness and needs to be simplified, standardized, along with the geojson map feature rendering.

        var LighthouseIcon = L.icon({
            iconUrl: '/assets/icons/lighthouse.png',
            //shadowUrl: 'leaf-shadow.png',

            iconSize:     [25, 25], // size of the icon
            //shadowSize:   [50, 64], // size of the shadow
            iconAnchor:   [12, 12], // point of the icon which will correspond to marker's location
            //shadowAnchor: [4, 62],  // the same for the shadow
            popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
        });


        // VesselMarker = L.rotatedMarker(Coords, {icon: VesselIcon}).addTo(map);
        var OSDMVessels = {'Vessel 1': {'Type': 'vessel', 'Coords': [54.1849, 7.9037], 'Course': 320, 'Speed': 0, 'Range':400, 'Marker': false, 'Plot': false,'RangeDisplay': false},
                           'Vessel 2': {'Type': 'vessel', 'Coords': [54.17683, 7.8931], 'Course': 290, 'Speed': 0, 'Range':300, 'Marker': false, 'Plot': false, 'RangeDisplay': false},
                           'Vessel 3': {'Type': 'vessel', 'Coords': [54.16889, 7.90593], 'Course': 30, 'Speed': 5, 'Range':700, 'Marker': false, 'Plot': false, 'RangeDisplay': false},
                           'Vessel 4': {'Type': 'vessel', 'Coords': [54.1661, 7.90434], 'Course': 210, 'Speed': 8, 'Range':800, 'Marker': false, 'Plot': false, 'RangeDisplay': false},
                           'Lighthouse Helgoland': {'Type': 'lighthouse', 'Coords': [54.18182, 7.88227], 'Course': 0, 'Speed': 0, 'Range': 1500, 'Marker': false, 'Plot': false, 'RangeDisplay': false}
                           };

        var Routes = {};
        var route;
        var waypoints;

        function centerMap (e) {
            console.log(e.latlng);
            map.panTo(e.latlng);
        }

        function zoomIn (e) {
            map.zoomIn();
        }

        function zoomOut (e) {
            map.zoomOut();
        }

        function zoomHere (e) {
            map.panTo(e.latlng);
            map.zoomIn();
        }

        function centerVessel (e) {
            map.panTo(Coords);
        }

        function closeRoute (e) {
            console.log('Closing route editor');

            var points = route.getPoints();
            console.log(points);
            waypoints = [];
            points.forEach(function(point) {
                console.log(point);
                waypoints.push(point.getLatLng());
            });
            $.ajax({
                type: 'POST',
                url: '/route/store/', // missing: route id or "new"
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify(waypoints),
                success: function(data)
                {
                    alert(data);
                }
            });
            map.removeLayer(route);

            editingRoute = false;
            waypointline = L.polyline(waypoints, {color: 'black'}).addTo(map);
        }

        function startRoute (e) {
            if (editingRoute) {
                alert('Cannot edit two routes at one time! Close the current route first.');
            } else {
                console.log(Coords);
                var startcoords = e.latlng;
                console.log(startcoords);

                route = L.Polyline.PolylineEditor([
                    Coords,
                    [startcoords.lat, startcoords.lng]
                ],{
                    weight: 5
                }).addTo(map);
                editingRoute = true;
            }
        }

        var map = L.map('map', {
            zoom: 16,
            maxZoom: 17,
            minZoom: 3,
            zoomControl: false,
            zoomsliderControl: true,
            contextmenu: true,
            contextmenuWidth: 200,
            contextmenuItems: [{
                text: 'Start new route',
                callback: startRoute
            }, {
                text: 'Close route',
                callback: closeRoute
            }, '-', {
                text: 'Center map on Vessel',
                callback: centerVessel
            }, {
                text: 'Center map here',
                callback: centerMap
            }, '-', {
                text: 'Zoom in',
                icon: '/assets/images/zoom-in.png',
                callback: zoomIn
            }, {
                text: 'Zoom out',
                icon: '/assets/images/zoom-out.png',
                callback: zoomOut
            }, {
                text: 'Zoom here',
                icon: '/assets/images/zoom-here.png',
                callback: zoomHere
            }]
        });

        /*if (!map.restoreView()) {
            map.setView([52.513, 13.41998], 16);
        }
        */

        var Terminator = terminator(); //.addTo(map);

        var GraticuleOne = L.graticule({ style: { color: '#55A', weight: 1, dashArray: '.'}, interval: 1 }).addTo(map);

        //var MousePosition = L.control.mousePosition().addTo(map);

        //var PanControl = L.control.pan().addTo(map);

        var openStreetMapUrl = 'http://{s}.tile.osm.org/{z}/{x}/{y}.png';
        var cached_openStreetMapUrl = 'http://localhost:8055/tiles/tile.osm.org/{z}/{x}/{y}.png';
        var seamarksUrl = 'http://tiles.openseamap.org/seamark/{z}/{x}/{y}.png';
        var cached_seamarksUrl = 'http://localhost:8055/tiles/tiles.openseamap.org/seamark/{z}/{x}/{y}.png';
        var cached_esriworldimageryUrl = 'http://localhost:8055/tiles/server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
        var esriworldimageryAttribution = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community';
        var sportsUrl = 'http://tiles.openseamap.org/sport/{z}/{x}/{y}.png';

        var openStreetMapAttribution = '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors';
        var OpenSeaMapAttribution = 'Map data &copy; 2012 OpenSeaMap contributors';

        var osmlayer       = L.tileLayer(openStreetMapUrl, {attribution: openStreetMapAttribution}); // .addTo(map);
        var seamarkslayer  = L.tileLayer(seamarksUrl, {maxZoom: 16, attribution: OpenSeaMapAttribution}); //.addTo(map);
        var cached_osmlayer       = L.tileLayer(cached_openStreetMapUrl, {attribution: openStreetMapAttribution}).addTo(map);
        var cached_seamarkslayer  = L.tileLayer(cached_seamarksUrl, {maxZoom: 16, attribution: OpenSeaMapAttribution}); // .addTo(map);
        var cached_esriworldimagerylayer    = L.tileLayer(cached_esriworldimageryUrl, {maxZoom: 16, attribution: esriworldimageryAttribution}).setOpacity(0.5);
        var sportslayer    = L.tileLayer(sportsUrl, {minZoom: 8, maxZoom: 18, attribution: OpenSeaMapAttribution});
        //    cloudmadelayer = L.tileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/997/256/{z}/{x}/{y}.png', {
        //        maxZoom: 18,
        //        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>'
        //    });


        var baseLayers = {
            'Default': osmlayer,
            'Cached':  cached_osmlayer,
            //'Cloudmade': cloudmadelayer,
        };

        var overlayLayers = {
            'Seamarks': seamarkslayer,
            'Seamarks Cached': cached_seamarkslayer,
            'Sports': sportslayer,
            'Terminator': Terminator,
            //'Grid 1°': GraticuleOne,
            'Satellite by ESRI World Imagery': cached_esriworldimagerylayer,
            'OpenWeatherMap Clouds': L.tileLayer.provider('OpenWeatherMap.Clouds'),
            'OpenWeatherMap CloudsClassic': L.tileLayer.provider('OpenWeatherMap.CloudsClassic'),
            'OpenWeatherMap Precipitation': L.tileLayer.provider('OpenWeatherMap.Precipitation'),
            'OpenWeatherMap PrecipitationClassic': L.tileLayer.provider('OpenWeatherMap.PrecipitationClassic'),
            'OpenWeatherMap Rain': L.tileLayer.provider('OpenWeatherMap.Rain'),
            'OpenWeatherMap RainClassic': L.tileLayer.provider('OpenWeatherMap.RainClassic'),
            'OpenWeatherMap Pressure': L.tileLayer.provider('OpenWeatherMap.Pressure'),
            'OpenWeatherMap PressureContour': L.tileLayer.provider('OpenWeatherMap.PressureContour'),
            'OpenWeatherMap Wind': L.tileLayer.provider('OpenWeatherMap.Wind'),
            'OpenWeatherMap Temperature': L.tileLayer.provider('OpenWeatherMap.Temperature'),
            'OpenWeatherMap Snow': L.tileLayer.provider('OpenWeatherMap.Snow')
        };

        jQuery.extend(overlayLayers, routeLayers);

        //var layerControl = L.control.layers(baseLayers, overlayLayers).addTo(map);

        var style = {color:'red', opacity: 1.0, fillOpacity: 1.0, weight: 2, clickable: false};

        /*L.Control.FileLayerLoad.LABEL = '<i class="fa fa-folder-open filelayer-icon"></i>';
        L.Control.fileLayerLoad({
            fitBounds: true,
            layerOptions: {style: style,
                           pointToLayer: function (data, latlng) {
                              return L.circleMarker(latlng, {style: style});
                           }},
        }).addTo(map);
        */
        var courseplot = L.polyline([], {color: 'red'}).addTo(map);

        function onMapClick(e) {
            if($('#cb_identify').is(':checked')){

                var popup = L.popup()
                    .setLatLng(e.latlng)
                    .setContent('Here is: ' + e.latlng.toString())
                    .openOn(map);
                }
        }

        map.on('click', onMapClick);

        var VesselMarker = L.rotatedMarker(Coords, {icon: VesselIcon}).addTo(map);

        function update_show_vessels() {
            console.log('Toggling Show Vessels');

            if(!$('#cb_show_vessels').is(':checked')){
                for (property in OSDMVessels) {

                    var name = property;
                    var marker = OSDMVessels[name].Marker;
                    var plot = OSDMVessels[name].Plot;
                    if(marker != false) { map.removeLayer(marker); }
                    if(plot != false) map.removeLayer(plot);

                    OSDMVessels[name].Marker = OSDMVessels[name].Plot = false;
                }
            } else {
                UpdateVessels();
            }
        }

        function update_show_radiorange() {
            console.log('Toggling Show Radiorange');

            if(!$('#cb_show_radiorange').is(':checked')){
                for (property in OSDMVessels) {

                    var name = property;
                    var rangecircle = OSDMVessels[name].RangeDisplay;

                    if (rangecircle != false) {
                        map.removeLayer(rangecircle);
                        OSDMVessels[name].RangeDisplay = false;
                    }
                }
                map.removeLayer(RangeDisplay);
                RangeDisplay = false;
            } else {
                UpdateVessels();
            }
        }

        function UpdateVessels(){
            if($('#cb_show_vessels').is(':checked')){
                for (property in OSDMVessels) {

                    name = property;
                    coords = OSDMVessels[name].Coords;
                    course = OSDMVessels[name].Course;
                    speed = OSDMVessels[name].Speed;
                    type = OSDMVessels[name].Type;
                    radiorange = OSDMVessels[name].Range;

                    var icon;

                    //console.log('OSDMVESSELDISPLAY: ', type, name, ':',speed, '@', coords);

                    if ($('#cb_show_radiorange').is(':checked')) {
                        if(OSDMVessels[name].RangeDisplay == false) {
                            var circle = L.circle(coords, radiorange, {
                                color: '#6494BF',
                                fillColor: '#4385BF',
                                fillOpacity: 0.4
                            }).addTo(map);
                            OSDMVessels[name].RangeDisplay = circle;
                        }
                    }

                    if (type == 'vessel') {
                        if (speed > 0) {
                            var dist = speed * (5/60);

                            /* var target = [0,0];
                            target[0] = Math.asin( Math.sin(coords[0])*Math.cos(d/R) + Math.cos(coords[0])*Math.sin(d/R)*Math.cos(course) );
                            target[1] = coords[1] + Math.atan2(Math.sin(course)*Math.sin(d/R)*Math.cos(coords[0]), Math.cos(d/R)-Math.sin(coords[0])*Math.sin(target[0])); */


                            var lat1 = Geo.parseDMS(coords[0]);
                            var lon1 = Geo.parseDMS(coords[1]);
                            var brng = Geo.parseDMS(course);


                            // calculate destination point, final bearing
                            var p1 = LatLon(lat1, lon1);
                            var p2 = p1.destinationPoint(brng, dist);
                            var brngFinal = p1.finalBearingTo(p2);

                            //console.log('OSDMVESSELDISPLAY-ARROW: Distance travelled in 5 min:', dist, 'Coords: ', p1, ' Coords in 5 min:', p2, ' Final Bearing:', brngFinal);
                            if (OSDMVessels[name].Plot == false) {
                                OSDMVessels[name].Plot = L.polyline([p1, p2], {color: 'red'}).addTo(map);
                            } else {
                                OSDMVessels[name].Plot.setLatLngs([p1, p2]);
                            }

                            icon = VesselMovingIcon;

                        } else {
                            if (OSDMVessels[name].Plot != false) {
                                map.removeLayer(OSDMVessels[name].Plot);
                                OSDMVessels[name].Plot = false;
                            }
                            icon = VesselStoppedIcon;
                        }
                    } else if (type=='lighthouse') {
                        icon = LighthouseIcon;
                    }

                    if(OSDMVessels[name].Marker != false) {
                        OSDMVessels[name].Marker.setLatLng(coords);
                        OSDMVessels[name].Marker.options.angle = course;
                        OSDMVessels[name].Marker.update();
                    } else {
                        OSDMVessels[name].Marker = marker = L.rotatedMarker(coords, {icon: icon}).addTo(map);
                        OSDMVessels[name].Marker.options.angle = course;
                        OSDMVessels[name].Marker.update();
                    }
                }
            }
        }

        function UpdateMapMarker(){
            console.log('Getting current Vessel position');

            $.ajax({
                type: 'POST',
                url: 'logbook/latest',
                contentType: 'application/json',
                dataType: 'json',
                success: function (response) {
                    Coords = response.coords;
                    Course = response.course;
                    console.log('Coords: ' + Coords + ' Course:' + Course);

                    courseplot.addLatLng(Coords);
                    plotted = courseplot.getLatLngs();

                    if (plotted.length > 50) {
                        courseplot.spliceLatLngs(0, 1);
                    }

                    VesselMarker.setLatLng(Coords);
                    VesselMarker.options.angle = Course;
                    VesselMarker.update();

                    if ($('#cb_show_radiorange').is(':checked')) {
                        if(RangeDisplay == false) {
                            var circle = L.circle(Coords, Radiorange, {
                                color: '#67BF64',
                                fillColor: '#67BF64',
                                fillOpacity: 0.4
                            }).addTo(map);
                            RangeDisplay = circle;
                        }
                    }


                }
            });

            if($('#cb_follow').is(':checked')){
                centerVessel();
            }
        }


        function Update() {
            if($('#cb_update').is(':checked')){
                UpdateMapMarker();
                UpdateVessels();
            }

            console.log(OSDMVessels);

            setTimeout(function(){
            Update();}, 3000);
        }

        $(document).ready(function(){
            Update();
        });
    };

    $scope.$on('$viewContentLoaded', function() {
        console.log('Fertig!');
        $scope.init();
    });

});

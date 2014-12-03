'use strict';


/**
 * @ngdoc function
 * @name frontendApp.controller:MapCtrl
 * @description
 * # MapCtrl
 * Controller of the frontendApp
 */
angular.module('frontendApp')
  .controller('MapCtrl', ["$scope", "leafletData", function ($scope, leafletData) {
    angular.extend($scope, {
      helgoland: {
        lat: 52.513,
        lon: 13.41998,
        zoom: 12
      },
      Vessel: {
        lat: 52.67,
        lon: 13.43,
        course: 0,
        speed: 0,
        radiorange: 700
      },
      settings: {
        OSDMRangeDisplay: false,
        OSDMDisplay: false,
        VesselFollow: true
      },
      OSDMVessels: {
        'Vessel 1': {
          'Type': 'vessel',
          'Coords': [54.1849, 7.9037],
          'Course': 320,
          'Speed': 0,
          'Range': 400,
          'Marker': false,
          'Plot': false,
          'RangeDisplay': false
        },
        'Vessel 2': {
          'Type': 'vessel',
          'Coords': [54.17683, 7.8931],
          'Course': 290,
          'Speed': 0,
          'Range': 300,
          'Marker': false,
          'Plot': false,
          'RangeDisplay': false
        },
        'Vessel 3': {
          'Type': 'vessel',
          'Coords': [54.16889, 7.90593],
          'Course': 30,
          'Speed': 5,
          'Range': 700,
          'Marker': false,
          'Plot': false,
          'RangeDisplay': false
        },
        'Vessel 4': {
          'Type': 'vessel',
          'Coords': [54.1661, 7.90434],
          'Course': 210,
          'Speed': 8,
          'Range': 800,
          'Marker': false,
          'Plot': false,
          'RangeDisplay': false
        },
        'Lighthouse Helgoland': {
          'Type': 'lighthouse',
          'Coords': [54.18182, 7.88227],
          'Course': 0,
          'Speed': 0,
          'Range': 1500,
          'Marker': false,
          'Plot': false,
          'RangeDisplay': false
        }
      },
      controls: {
        draw: {}
      },
      layers: {
        baselayers: {
          osm: {
            name: 'OpenStreetMap',
            type: 'xyz',
            url: 'http://localhost:8055/tiles/a.tile.osm.org/{z}/{x}/{y}.png',
            layerOptions: {
              //subdomains: ['a', 'b', 'c'],
              attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
              continuousWorld: false
            }
          },
          cycle: {
            name: 'OpenCycleMap',
            type: 'xyz',
            url: 'http://localhost:8055/tiles/a.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png',
            layerOptions: {
              //subdomains: ['a', 'b', 'c'],
              attribution: '&copy; <a href="http://www.opencyclemap.org/copyright">OpenCycleMap</a> contributors - &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
              continuousWorld: true
            }
          }
        },
        overlays: {
          openseamap: {
            name: 'OpenSeaMap',
            type: 'xyz',
            url: 'http://localhost:8055/tiles/t1.openseamap.org/seamark/{z}/{x}/{y}.png',
            layerOptions: {
              attribution: '&copy; OpenSeaMap contributors',
              continuousWorld: true,
              tms: true
            }
          },
          hillshade: {
            name: 'Hillshade Europa',
            type: 'wms',
            url: 'http://localhost:8055/tiles/129.206.228.72/cached/hillshade',
            visible: false,
            layerOptions: {
              layers: 'europe_wms:hs_srtm_europa',
              format: 'image/png',
              opacity: 0.25,
              attribution: 'Hillshade layer by GIScience http://www.osm-wms.de',
              crs: L.CRS.EPSG900913
            }
          },
          fire: {
            name: 'OpenFireMap',
            type: 'xyz',
            url: 'http://localhost:8055/tiles/openfiremap.org/hytiles/{z}/{x}/{y}.png',
            visible: false,
            layerOptions: {
              attribution: '&copy; <a href="http://www.openfiremap.org">OpenFireMap</a> contributors - &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
              continuousWorld: true
            }
          },
          esriimagery: {
            name: 'Satellite ESRI World Imagery',
            type: 'xyz',
            url: 'http://localhost:8055/tiles/server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            visible: false,
            layerOptions: {
              attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
              continuousWorld: true,
              opacity: 0.25
            }
          }
        }
      }
    });
    leafletData.getMap().then(function (map) {
      var drawnItems = $scope.controls.draw.edit.featureGroup;

      map.on('draw:created', function (e) {
        var layer = e.layer;
        console.log(e);

        drawnItems.addLayer(layer);
        console.log(JSON.stringify(layer.toGeoJSON()));

      });
    });
    /*

     $scope.init = function (scope) {
     console.log('Hello Mapviewer!');

     L.RotatedMarker = L.Marker.extend({
     options: {angle: 0},
     _setPos: function (pos) {
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
     L.rotatedMarker = function (pos, options) {
     return new L.RotatedMarker(pos, options);
     };


     var cm;

     var VesselIcon = L.icon({
     iconUrl: '/assets/icons/vessel.png',
     //shadowUrl: 'leaf-shadow.png',

     iconSize: [25, 25], // size of the icon
     //shadowSize:   [50, 64], // size of the shadow
     iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
     //shadowAnchor: [4, 62],  // the same for the shadow
     popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
     });

     var VesselMovingIcon = L.icon({
     iconUrl: '/assets/icons/vessel-moving.png',
     //shadowUrl: 'leaf-shadow.png',

     iconSize: [25, 25], // size of the icon
     //shadowSize:   [50, 64], // size of the shadow
     iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
     //shadowAnchor: [4, 62],  // the same for the shadow
     popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
     });

     var VesselStoppedIcon = L.icon({
     iconUrl: '/assets/icons/vessel-stopped.png',
     //shadowUrl: 'leaf-shadow.png',

     iconSize: [25, 25], // size of the icon
     //shadowSize:   [50, 64], // size of the shadow
     iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
     //shadowAnchor: [4, 62],  // the same for the shadow
     popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
     });

     // TODO: This is madness and needs to be simplified, standardized, along with the geojson map feature rendering.

     var LighthouseIcon = L.icon({
     iconUrl: '/assets/icons/lighthouse.png',
     //shadowUrl: 'leaf-shadow.png',

     iconSize: [25, 25], // size of the icon
     //shadowSize:   [50, 64], // size of the shadow
     iconAnchor: [12, 12], // point of the icon which will correspond to marker's location
     //shadowAnchor: [4, 62],  // the same for the shadow
     popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
     });


     // VesselMarker = L.rotatedMarker(Coords, {icon: VesselIcon}).addTo(map);


     function centerMap(e) {
     console.log(e.latlng);
     map.panTo(e.latlng);
     }

     function zoomIn(e) {
     map.zoomIn();
     }

     function zoomOut(e) {
     map.zoomOut();
     }

     function zoomHere(e) {
     map.panTo(e.latlng);
     map.zoomIn();
     }

     function centerVessel(e) {
     map.panTo(Coords);
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

     var Terminator = terminator(); //.addTo(map);

     var GraticuleOne = L.graticule({style: {color: '#55A', weight: 1, dashArray: '.'}, interval: 1}).addTo(map);

     //var MousePosition = L.control.mousePosition().addTo(map);

     //var PanControl = L.control.pan().addTo(map);


     var style = {color: 'red', opacity: 1.0, fillOpacity: 1.0, weight: 2, clickable: false};

     /*L.Control.FileLayerLoad.LABEL = '<i class="fa fa-folder-open filelayer-icon"></i>';
     L.Control.fileLayerLoad({
     fitBounds: true,
     layerOptions: {style: style,
     pointToLayer: function (data, latlng) {
     return L.circleMarker(latlng, {style: style});
     }},
     }).addTo(map);
     /**/
    /*
     var courseplot = L.polyline([], {color: 'red'}).addTo(map);

     function onMapClick(e) {
     if ($('#cb_identify').is(':checked')) {

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

     if (!$('#cb_show_vessels').is(':checked')) {
     for (property in OSDMVessels) {

     var name = property;
     var marker = OSDMVessels[name].Marker;
     var plot = OSDMVessels[name].Plot;
     if (marker != false) {
     map.removeLayer(marker);
     }
     if (plot != false) map.removeLayer(plot);

     OSDMVessels[name].Marker = OSDMVessels[name].Plot = false;
     }
     } else {
     UpdateVessels();
     }
     }

     function update_show_radiorange() {
     console.log('Toggling Show Radiorange');

     if (!$('#cb_show_radiorange').is(':checked')) {
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

     function UpdateVessels() {
     if ($('#cb_show_vessels').is(':checked')) {
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
     if (OSDMVessels[name].RangeDisplay == false) {
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
     var dist = speed * (5 / 60);

     /* var target = [0,0];
     target[0] = Math.asin( Math.sin(coords[0])*Math.cos(d/R) + Math.cos(coords[0])*Math.sin(d/R)*Math.cos(course) );
     target[1] = coords[1] + Math.atan2(Math.sin(course)*Math.sin(d/R)*Math.cos(coords[0]), Math.cos(d/R)-Math.sin(coords[0])*Math.sin(target[0]));
     */
    /*

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
     } else if (type == 'lighthouse') {
     icon = LighthouseIcon;
     }

     if (OSDMVessels[name].Marker != false) {
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

     function UpdateMapMarker() {
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
     if (RangeDisplay == false) {
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

     if ($('#cb_follow').is(':checked')) {
     centerVessel();
     }
     }


     function Update() {
     if ($('#cb_update').is(':checked')) {
     UpdateMapMarker();
     UpdateVessels();
     }

     console.log(OSDMVessels);

     setTimeout(function () {
     Update();
     }, 3000);
     }

     $(document).ready(function () {
     Update();
     });
     };

     $scope.$on('$viewContentLoaded', function () {
     console.log('Fertig!');
     /* $scope.init($scope);
     $("#map").height($(window).height()-100).width($(window).width());
     $scope.map.invalidateSize(); */
  }]);

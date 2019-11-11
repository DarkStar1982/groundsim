/**
 * Map width/360 or Map heoight/180 
 * 298/360 , 150/360
 */
var mapConversionConstX = 0.8277;
var mapConversionConstY = 0.8333;
/**
 * Map size
 */
var mapWidth = 298;
var mapHeight = 150;
/**
 * Pause between AJAX calls
 */
var loopBreak = 3000;
var baseUrl = "http://127.0.0.1:8000"

var norad_url = "";

var app = new Vue({
    el: '#dash_app',
    data: {
	norad_id: 0,
	sat_name: 0,
	path: [],
	interval: null,
	datalocation: {
	    lat: 0,
	    lng: 0,
	    alt: 0,
	    time: "N/A",
	    i: 0,
	    ra: 0,
	    e: 0,
	    a: 0,
	    w: 0,
	    tp: 0
	},
	api: {
	    list: baseUrl + "/list/",
	    location: baseUrl + "/location/"+norad_url,
	    telemetry: baseUrl + "/telemetry",
	    log: baseUrl + "/log/",
	    instruments: baseUrl + "/instruments/"
	}
    },
    mounted: function () {
	this.getNoradId();
	this.interval = setInterval(function () {
	    this.showLocation();
	}.bind(this), loopBreak);
    },
    created: function () {

    },
    methods: {
	getNoradId(){
	    var theApp = this;
    
	    this.loadApi(this.api.list, function (data) {
		theApp.norad_id = data.satelites[0].norad_id;
		theApp.sat_name = data.satelites[0].sat_name;
		norad_url = "?norad_id=" + data.satelites[0].norad_id;
	    });
	},
	showLocation() {
	    var theApp = this;
	    console.log(norad_url);
	    this.loadApi(this.api.location+norad_url, function (data) {
		var ctx = document.getElementById("earth_map_img").getContext("2d");

		var lng = (data.lng < 0) ? data.lng : data.lng * 2;
		var lat = (data.lat > 0) ? data.lat : data.lat * 2;

		var x = Math.abs(Math.round(lng * mapConversionConstX));
		var y = Math.abs(Math.round(lat * mapConversionConstY));

		theApp.path.push({x, y});

		theApp.drawSatellite(ctx, x, y);
	    });
	},
	drawSatellite(ctx, x, y) {
	    var img = document.getElementById("satelite_icon");
	    ctx.clearRect(0, 0, mapWidth, mapHeight);
	    ctx.drawImage(img, x - 5, y - 5, 20, 20);
	},
	drawTrajectory(ctx) {
	    this.path.forEach(function (coord) {
		ctx.beginPath();
		ctx.moveTo(coord.x, coord.y);
		ctx.lineTo(coord.x + 1, coord.y + 1);
		ctx.stroke();
	    });
	},
	loadApi(endpoint, callback) {
	    var theApp = this;
	    axios.get(endpoint).then((response) => {
		if (response.data.status === 'ok') {
		    callback(response.data);
		    //	refresh location data
		    theApp.datalocation = response.data;
		}
	    }).catch(error => {
		console.log(error);
	    });
	}
    },
    beforeDestroy: function () {
	clearInterval(this.interval);
    }
});

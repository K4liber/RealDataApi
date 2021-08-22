function load_map(lat, lon) {
    var mymap = L.map('mapid').setView([lat, lon], 13);

    var tileLayer = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiazRsaWJlciIsImEiOiJja3NtczE4MmUwMW9jMnBucDZkdWYyZ2JzIn0.bRAZ1jLsbV1tY1-zNr9UzA', {
        attribution: 'Map data',
        maxZoom: 18,
        id: 'mapbox/streets-v11',
        tileSize: 512,
        zoomOffset: -1,
        accessToken: 'pk.eyJ1IjoiazRsaWJlciIsImEiOiJja3NtczE4MmUwMW9jMnBucDZkdWYyZ2JzIn0.bRAZ1jLsbV1tY1-zNr9UzA'
    });
    tileLayer.addTo(mymap);

    var marker = L.marker([lat, lon]).addTo(mymap);
    marker.bindPopup("" +
        "<div style='margin: 0 auto;'>" +
        "<img style='width: 80px;' src='static/jbielecki.jpeg'/>" +
        "<br>Jan Bielecki" +
        "</div>");
}

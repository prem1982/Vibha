<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAqwsGFsC84NYRZq4fGZig_hRu2Gqn4HTYJgQveiu145_qnQ4NxBQD2p2SdrGQ82lxQV9U_mjHTmh1SA"
      type="text/javascript"></script>
<script type="text/javascript">

//<![CDATA[

function load() {
  if (GBrowserIsCompatible()) {
    var map = new GMap2(document.getElementById("map"));
    map.addControl(new GSmallMapControl());
    map.setCenter(new GLatLng(22.5, 83), 5);

    /* Define Cutom Icons */
    var redIcon = new GIcon(G_DEFAULT_ICON);
    redIcon.image = "http://www.google.com/intl/en_us/mapfiles/ms/micons/red-dot.png";
    redIcon.iconSize = new GSize(32,32);
    redIcon.iconAnchor = new GPoint(16,32);
    redIcon.shadow = "";
    var greenIcon = new GIcon(G_DEFAULT_ICON);
    greenIcon.image = "http://www.google.com/intl/en_us/mapfiles/ms/micons/green-dot.png";
    greenIcon.iconSize = new GSize(32,32);
    greenIcon.iconAnchor = new GPoint(16,32);
    greenIcon.shadow = "";

    var locationS = [ 
    {% for location in locationS %}
      {{ location|safe }}{% if not forloop.last %},{% endif %}
    {% endfor %}
    ];

    function addLocation(location) {
      var point = new GLatLng(location.lat, location.lng);
      if(location.current_project)
        location.markeroption = {icon: greenIcon};
      else
        location.markeroption = {icon: redIcon};

      location.marker = new GMarker(point,location.markeroption);
      map.addOverlay(location.marker);
      GEvent.addListener(location.marker, "click", function() { showInfo(location.id); });
    }

    function showInfo(id) {
      var location = locationS[id];
      map.closeInfoWindow();
      location.marker.openInfoWindowHtml(location.code);
    }

    for (var i = 0; i < locationS.length; i++) {
      locationS[i].id = i;
    }

    for (var i = 0; i < locationS.length; i++) {
      addLocation(locationS[i]);
    }

  }
}

//]]>
</script>

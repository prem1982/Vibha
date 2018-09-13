<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAqwsGFsC84NYRZq4fGZig_hRu2Gqn4HTYJgQveiu145_qnQ4NxBQD2p2SdrGQ82lxQV9U_mjHTmh1SA"
      type="text/javascript"></script>
<script type="text/javascript">

//<![CDATA[

function load() {
  if (GBrowserIsCompatible()) {
    var map = new GMap2(document.getElementById("map"));
    /* map.addControl(new GSmallMapControl()); */
    map.setCenter(new GLatLng(23.5, 83), 3);

    GEvent.addListener(map, "click", function() {
      window.open('http://projects.vibha.org/projects/map/', 'Vibha projects');
    });

    // Creates a marker at the given point with the given number label
    function createMarker(lat, lng, name) {
      var point = new GLatLng(lat, lng);
      var marker = new GMarker(point);
      return marker;
    }

    map.addOverlay(createMarker({{ project.location.latitude }}, {{ project.location.longitude }}, '{{ project.name|escape }}'));
  }
}

//]]>
</script>

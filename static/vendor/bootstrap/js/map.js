// Initialize and add the map
function initMap() {
    // The location of Birmingham
    const uluru = { lat: 52.4862, lng: -1.8905 };
    // The map, centered at Birmingham
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 4,
        center: uluru,
    });
    // The marker, positioned at Birmingham
    const marker = new google.maps.Marker({
        position: uluru,
        map: map,
    });
    }
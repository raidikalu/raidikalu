(function analytics() {

  gtag('config', GOOGLE_ANALYTICS_ID, {
    'custom_map': {
      'dimension1': 'monster',
      'dimension2': 'tier',
      'dimension3': 'gym',
      'dimension4': 'starttimechoice',
      'metric1': 'starttimeint',
    }
  });

  document.body.addEventListener('change', handleEvent);
  document.body.addEventListener('click', handleEvent);

  function handleEvent(event) {

    var eventName;
    var data = {};
    var raidId;
    var raidElement;

    if (event.type === 'change' && event.target.checked && event.target.id.indexOf('raid-toggle-') === 0) {
      eventName = 'details';
      raidId = event.target.id.split('-')[2];
    }
    else if (event.type === 'change' && event.target.checked && event.target.id.indexOf('rac-') === 0) {
      eventName = 'participation';
      raidId = event.target.id.split('-')[1];
      data['starttimechoice'] = event.target.value;
      data['starttimeint'] = event.target.value;
    }
    else if (event.target.classList.contains('raid-map-link')) {
      eventName = 'location';
      raidId = event.target.parentNode.parentNode.getAttribute('data-id');
    }
    else if (event.target.classList.contains('raid-directions-link')) {
      eventName = 'directions';
      raidId = event.target.parentNode.parentNode.getAttribute('data-id');
    }
    else {
      return;
    }

    raidElement = document.querySelector('.raid[data-id="' + raidId + '"]');
    data['monster'] = raidElement.getAttribute('data-monster');
    data['tier'] = raidElement.getAttribute('data-tier');
    data['gym'] = raidElement.getAttribute('data-gym');
    data['event_action'] = eventName;

    gtag('event', eventName, data);

  }

})();

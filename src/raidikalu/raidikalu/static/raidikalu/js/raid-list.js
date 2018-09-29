
initTimers();
initNicknameListeners();
initAttendanceListeners(document);
initRaidLinking();


var timerElements = document.querySelectorAll('[data-time]');

function initTimers() {

  setInterval(updateTimers, 1000);

  function updateTimers() {

    var len = timerElements.length;
    var i;

    for (i = 0; i < len; i++) {
      updateTimer(timerElements[i]);
    }

  }

  function updateTimer(element) {

    var targetTime = parseInt(element.getAttribute('data-time'));
    var currentTime = Math.round(new Date().getTime() / 1000.0);
    var timeLeft = Math.max(targetTime - currentTime, 0);

    if (timeLeft) {
      var seconds = timeLeft % 60;
      var minutes = Math.floor(timeLeft / 60 % 60);
      var hours = Math.floor(timeLeft / 60 / 60 % 60);
      element.innerHTML = pad(hours) + ':' + pad(minutes) + ':' + pad(seconds);
    }

  }

  function pad(val) {
    return ('0' + val.toString()).slice(-2);
  }

}


function initNicknameListeners() {

  var nicknameField = document.querySelector('.trainer-nickname-input');

  nicknameField.addEventListener('change', handleNicknameChange);

  function handleNicknameChange() {

    var formData = new FormData();
    var request = new XMLHttpRequest();

    formData.append('action', 'set-nickname');
    formData.append('nickname', nicknameField.value);
    request.open('POST', '', true);
    request.setRequestHeader('X-CSRFToken', CSRFTOKEN);
    request.send(formData);

  }

}


function initAttendanceListeners(containerElement) {

  var attendanceChoiceContainers = containerElement.querySelectorAll('.raider-attendance-choices');
  var len = attendanceChoiceContainers.length;
  var i;

  for (i = 0; i < len; i++) {
    attendanceChoiceContainers[i].addEventListener('change', handleAttendanceChange);
  }

  function handleAttendanceChange(event) {

    var raidId = this.getAttribute('data-raid-id');
    var attendanceChoice = event.target.value;

    var formData = new FormData();
    var request = new XMLHttpRequest();

    formData.append('action', 'set-attendance');
    formData.append('raid', raidId);
    formData.append('choice', attendanceChoice);
    request.open('POST', '', true);
    request.setRequestHeader('X-CSRFToken', CSRFTOKEN);
    request.send(formData);

  }

}


function initMessageListeners() {

  var wsScheme = window.location.protocol == 'https:' ? 'wss' : 'ws';
  var websocket = new ReconnectingWebSocket(wsScheme + '://' + window.location.host + '/ws/');

  websocket.addEventListener('message', handleMessage);


  function handleMessage(event) {

    var payload = JSON.parse(event.data);
    var raidName = 'unknown';

    if (payload.event == 'attendance') {
      attendanceUpdated(payload.data);
    }

    if (payload.data.raid) {
      try {
        raidName = document.querySelector('.raid[data-id="' + payload.data.raid + '"] .raid-name').textContent;
      } catch(e) {}
    }

    console.log('[' + new Date().toLocaleTimeString('en-US', {hour12: false}) + ']', raidName + ':', payload.message);

  }

  function attendanceUpdated(attendance) {

    var raidSnippet = attendance.snippet;
    var tempWrapper = document.createElement('div');
    var oldRaidElement = document.querySelector('.raid[data-id="' + attendance.raid + '"]');
    var oldRaidCheckbox = oldRaidElement.querySelector('.raid-toggle');
    var newRaidElement;
    var oldChoiceElement;
    var choiceElements;
    var choiceIndex;

    tempWrapper.innerHTML = raidSnippet;
    newRaidElement = tempWrapper.firstChild;
    newRaidElement.querySelector('.raid-toggle').checked = oldRaidCheckbox.checked;

    choiceElements = newRaidElement.querySelectorAll('.raid-attendance-choice');
    if (attendance.submitter == NICKNAME) {
      choiceIndex = attendance.choice !== null ? parseInt(attendance.choice) : attendance.choice;
    }
    else {
      oldChoiceElement = oldRaidElement.querySelector('.raid-attendance-choice:checked');
      choiceIndex = oldChoiceElement ? parseInt(oldChoiceElement.value) : null;
    }
    if (choiceIndex !== null && choiceElements[choiceIndex]) {
      choiceElements[choiceIndex].checked = true;
      newRaidElement.querySelector('.raid-attandance-cancel').checked = false;
    }

    oldRaidElement.parentNode.replaceChild(newRaidElement, oldRaidElement);

    timerElements = document.querySelectorAll('[data-time]');
    initAttendanceListeners(newRaidElement);

  }

}


function initRaidLinking() {

  var raidWarning = document.querySelector('.unknown-raid');

  openLinkedRaid();
  window.addEventListener('hashchange', openLinkedRaid);

  function openLinkedRaid() {

    var raidId;
    var raidToggle;

    if (window.location.hash) {
      raidId = window.location.hash.split('-')[1];
      raidToggle = document.getElementById('raid-toggle-' + raidId);
      if (raidToggle) {
        raidToggle.checked = true;
        raidWarning.style.display = 'none';
      } else {
        raidWarning.style.display = '';
      }
    }

  }

}

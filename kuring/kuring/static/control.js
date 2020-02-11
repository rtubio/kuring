var task_id = getTaskId();
var url = "ws://" + window.location.host + "/ws/tasker/" + task_id + '/';
var __wsock;

cleanLog();
log('ws::OPEN to: ' + url);
__wsock = new WebSocket(url);

__wsock.onopen = function() {
  log('ws::CONNECTED to: ' + url)
};

__wsock.onmessage = function (evt)
{
  var data = JSON.parse(evt.data);
  log('ws::Data RECEIVED: ' + data)
};

__wsock.onclose = function()
{
  log('ws::DISCONNECTED from: ' + url);
};

__wsock.onerror = function(evt)
{
  log('ws::ERROR: ' + evt.data);
};

function requestData() {
  ws.send("get-data");
}

function cleanLog () {
  document.querySelector('#console').value = '';
}

function log (message) {
  document.querySelector('#console').value += (message  + '\n');
}

function getTaskId () {
  return document.getElementById('taskId').innerHTML;
}

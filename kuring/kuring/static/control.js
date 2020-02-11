var task_id = getTaskId();
var url = "ws://" + window.location.host + "/ws/tasker/" + task_id + '/';
var __wsock;
var __wsStatus = false;
var __pingAlarm;
var __pingReset = 0;
var KEEPALIVE = 20000;    // 20s keepalive

__init__();

__wsock.onopen = function() { log('ws::CONNECTED to: ' + url); updateWsStatus(true); };
__wsock.onerror = function(evt) { log('ws::ERROR: ' + evt.data); };
__wsock.onmessage = function (evt) { var data = JSON.parse(evt.data); decodeMessage(data); };
__wsock.onclose = function() { updateWsStatus(false); log('ws::[WARN] Reconecting...'); __wsock = new WebSocket(url); };


async function sendMessage(ws, message, count) {
  if (count) { __pingReset += 1; }
  return ws.send(JSON.stringify({'message': message}));
}


function decodeMessage(data) {
  __pingReset += 1;
  if (data['type'] == 'pong') { log('ws::INFO: pong!'); return; }
  if (data['type'] == 'info') { log('ws::INFO:' + str(data['message'])); return; }
  if (data['type'] == 'plot') { m = data['m']; x = data['x']; y = data['y'];
    // plot()
    return;
  }
  log('ws::ERROR: received data could not be decoded, data = ' + JSON.stringify(data));
}


function pingServer() {
  if (__wsStatus == false) { return; }
  if (__pingReset > 0) { __pingReset = 0; return; }
  sendMessage(__wsock, {'type': 'ping'}, false).then(function (e) { log('ws::INFO: ping!'); });
}


function __init__ () {
  updateWsStatus(false);
  cleanLog(); log('ws::OPEN to: ' + url);
  __wsock = new WebSocket(url);
  __pingAlarm = window.setInterval(pingServer, KEEPALIVE);   // every 5 seconds, ping...
}

function log (message) {
  document.getElementById('console').value = (message  + '\n') + document.getElementById('console').value;
}

function updateWsStatus (status) {
  var text = 'OFF';
  __wsStatus = status;
  if (__wsStatus) { text = 'ON'; }
  document.getElementById('wsStatus').innerHTML = text;
}

function cleanLog () { document.getElementById('console').value = ''; }
function getTaskId () { return document.getElementById('taskId').innerHTML; }
function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

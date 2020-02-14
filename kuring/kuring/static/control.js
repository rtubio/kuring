// general configuration
var task_id = document.getElementById('taskId').innerHTML;
var url = "ws://" + window.location.host + "/ws/tasker/" + task_id + '/';
var datefmt = { hour: "2-digit", minute: "2-digit", second: "2-digit" };
// plot.ly diagram configuraiton
var __plot;
var __plotId = 'graph1';
var __plotData = {
  'T1': {x: [], y: [], mode: 'lines', line: { width: 3}, name: 'temp_1'},
  'T2': {x: [], y: [], mode: 'lines', line: { width: 3}, name: 'temp_2'},
};
var layout = {
  title: 'Curing Oven - Temperature Measurements',
  showlegend: true,
  plot_bgcolor: "rgba(248, 249, 250, 0)",
  paper_bgcolor: "rgba(248, 249, 250, 0)",
  xaxis: { title: { text: 'time (s)' }, range: [0, 600] },
  yaxis: { title: { text: 'Temperature (degC)' }, range: [-10, 150] }
};
// websocket configuration
var __wsock;
var __wsStatus = false;
var __pingAlarm;
var __pingReset = 0;
var __navigating = false;   // flag that blocks the connection lost window from being launched during navigation

var KEEPALIVE = 50000;    // 50s keepalive


__init__();


$("#delOk").click(function(e) { __navigating = true; console.log('X'); });
$("#runOk").click(function(e) { __navigating = true; console.log('X'); });
$("#stopOk").click(function(e) { __navigating = true; console.log('X'); });
$("#endOk").click(function(e) { __navigating = true; console.log('X'); });

__wsock.onopen = function() { log('INF', 'CONNECTED to: ' + window.location.host); updateWsStatus(true); };
__wsock.onerror = function(evt) { log('ERR', evt.data); };
__wsock.onmessage = function (evt) { var data = JSON.parse(evt.data); decodeMessage(data); };
__wsock.onclose = function() {
  if (__navigating == true) {return;}
  updateWsStatus(false); log('ERR', 'Connection lost'); $('#informConnLost').modal();
};


async function sendMessage(ws, message, count) {
  if (count) { __pingReset += 1; } return ws.send(JSON.stringify({'message': message}));
}


function decodeMessage(message) {
  __pingReset += 1;
  data = message['message'];
  if (data['type'] == 'pong') { log('INF', 'Pong!'); return; }
  if (data['type'] == 'info') { log('INF', str(data['message'])); return; }
  if (data['type'] == 'task.finished') { log('INF', 'Task finished!'); $('#taskFinished').modal(); return; }
  if (data['type'] == 'plot.data') {
    __plotData[data['m']]['x'].push(data['x']);
    __plotData[data['m']]['y'].push(data['y']);
    Plotly.redraw(__plotId);
    return;
  }
  log('ERR', 'Non-decodable data = ' + JSON.stringify(data));
}


function pingServer() {
  if (__wsStatus == false) { return; }
  if (__pingReset > 0) { __pingReset = 0; return; }
  sendMessage(__wsock, {'type': 'ping'}, false).then(function (e) { log('INF', 'Ping!'); });
}


function __init__ () {
  updateWsStatus(false);
  cleanLog();
  __wsock = new WebSocket(url);
  __pingAlarm = window.setInterval(pingServer, KEEPALIVE);   // every 5 seconds, ping...
  __plot = Plotly.newPlot(__plotId, [__plotData['T1'], __plotData['T2']], layout);
}


function cleanLog () { document.getElementById('console').value = ''; }


function log (level, message) {
  var date = new Date();
  var timestr = date.toLocaleTimeString("es-ES", datefmt);
  text = '[' + timestr + ',' + level + ']: ' + message + '\n';
  document.getElementById('console').value = (text) + document.getElementById('console').value;
}


function updateWsStatus (status) {
  var text = 'OFF'; __wsStatus = status; if (__wsStatus) { text = 'ON'; }
  document.getElementById('wsStatus').innerHTML = text;
}

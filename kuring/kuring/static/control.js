// ui configuration
var task_status = $("#taskStatus").html();
var datefmt = { hour: "2-digit", minute: "2-digit", second: "2-digit" };
var __plotId = 'graph1';
var __plotData = {
  'T1': {x: [], y: [], mode: 'lines', line: { width: 3}, name: 'temp_1'},
  'T2': {x: [], y: [], mode: 'lines', line: { width: 3}, name: 'temp_2'},
};
var __navigating = false;   // flag that blocks the connection lost window from being launched during navigation
var layout = {
  title: 'Curing Oven - Temperature Measurements',
  showlegend: true,
  plot_bgcolor: "rgba(248, 249, 250, 0)",
  paper_bgcolor: "rgba(248, 249, 250, 0)",
  xaxis: { title: { text: 'time (s)' }, range: [0, 600], autorange: true },
  yaxis: { title: { text: 'Temperature (degC)' }, range: [-10, 150], autorange: false }
};
var __plot = Plotly.newPlot(__plotId, [__plotData['T1'], __plotData['T2']], layout);
var __latestPlot = 0.0;     // point in time for the latest plotted data.

// websocket configuration
var task_id = $("#taskId").html();
var url = "ws://" + window.location.host + "/ws/tasker/" + task_id + '/';

var KEEPALIVE = 50000;    // 50s keepalive
var __wsock = new WebSocket(url);
var __wsStatus = false;
var __wsDelayN = 0;
var __wsDelay = 0.0;
var __wsDelayPrev = 0.0;
var __wsDelayT = 0.0;
var __wsJitter = 0.0;
var __t0 = -1;
var __pingAlarm = window.setInterval(pingServer, KEEPALIVE);   // every 5 seconds, ping...;
var __pingReset = 0;


__wsock.onopen = function() {
  log('INF', 'CONNECTED to: ' + window.location.host); updateWsStatus(true);
  loadPlot();
};

__wsock.onerror = function(evt) { log('ERR', evt.data); };
__wsock.onmessage = function (evt) { var data = JSON.parse(evt.data); decodeMessage(data); };

__wsock.onclose = function() {
  if (__navigating == true) { return; }
  updateWsStatus(false);
  log('ERR', 'Connection lost'); $('#informConnLost').modal();
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
    __latestPlot = data['x'];
    __plotData[data['m']]['x'].push(data['x']);
    __plotData[data['m']]['y'].push(data['y']);
    Plotly.redraw(__plotId);
    reportDelay(data);
    return;
  }
  if (data['type'] == 'replay.data') {
    console.log('*, data = ' + JSON.stringify(data));
    plotChunks(data['m'], data['ts'], data['vs']);
    return;
  }
  log('ERR', 'Non-decodable data = ' + JSON.stringify(data));
}


function plotChunks(sensorId, times, values) {
  __plotData[sensorId]['x'].push(times);
  __plotData[sensorId]['y'].push(values);
  __latestPlot = times[times.length - 1];
  Plotly.redraw(__plotId);
}


function pingServer() {
  if (__wsStatus == false) { return; }
  if (__pingReset > 0) { __pingReset = 0; return; }
  sendMessage(__wsock, {'type': 'ping'}, false).then(function (e) { log('INF', 'Ping!'); });
}


function runOk__click(e) {
  $("#confirmRun").modal('toggle');
  sendMessage(__wsock, {'type': 'runTask', 'taskId': task_id});
  setControlsRunning(); log('INF', 'Task launched');
}


function stopOk__click(e) {
  $("#confirmStop").modal('toggle');
  sendMessage(__wsock, {'type': 'stopTask', 'taskId': task_id});
  setControlsFinished(); log('Task stopped');
}
function endOk__click(e) { $("#taskFinished").modal('toggle'); setControlsFinished(); log('INF', 'Task finished!'); }


$(document).ready(function(){

  log('INF', "Loading task #" + task_id + ", state = " + task_status);

  $("#runOk").click(runOk__click);
  $("#stopOk").click(stopOk__click);
  $("#endOk").click(endOk__click);

  updateWsStatus(false);
  cleanLog();
  setControls();

});


function loadPlot () {
  // This function loads the data from the previous execution run if necessary.
  if ((task_status == "N") || (task_status == "R" )) { return; }
  sendPlotRequest();
}


function sendPlotRequest () {
  var msg = {'type': 'requestPlot', 'taskpk': task_id, 'sensorId': 'T1'};
  sendMessage(__wsock, msg, true).then(log('INF', 'T1 Plot requested, task #' + task_id));
  var msg = {'type': 'requestPlot', 'taskpk': task_id, 'sensorId': 'T2'};
  sendMessage(__wsock, msg, true).then(log('INF', 'T2 Plot requested, task #' + task_id));
}


function setControls () {
  if (task_status == "N") { setControlsNew(); return; }
  if (task_status == "R") { setControlsRunning(); return; }
  setControlsFinished();
}

function setControlsNew () {
  $("#db-run").removeClass('na'); $("#db-stop").addClass('na'); $("#db-pause").addClass('na');
  $("#taskStatusLabel").html("New");
}
function setControlsRunning () {
  $("#db-run").addClass('na'); $("#db-stop").removeClass('na'); // TODO :: $("#db-pause").removeClass('na');
  $("#taskStatusLabel").html("Running");
}
function setControlsFinished () {
  $("#db-run").addClass('na'); $("#db-stop").addClass('na'); $("#db-pause").addClass('na');
  $("#taskStatusLabel").html("Finished");
}


function cleanLog () { $('#console').val(''); }


function log (level, message) {
  var date = new Date();
  var timestr = date.toLocaleTimeString("es-ES", datefmt);
  text = '[' + timestr + ',' + level + ']: ' + message + '\n';
  $('#console').val((text) + $('#console').val());
}


function updateWsStatus (status) {
  var text = 'OFF'; __wsStatus = status; if (__wsStatus) { text = 'ON'; } $('#wsStatus').html(text);
}


function timestamp () {return new Date().getTime();}


function reportDelay (data) {
  updateWsDelayStats(data);
  var report = {
    'type': 'reportDelay', 'taskId': task_id,
    't': __wsDelayT,
    'd': __wsDelayPrev,
    'j': __wsJitterPrev
  };
  sendMessage(__wsock, report, true).then(function (e) { });
}


function updateWsDelayStats(data) {

  __wsDelayT = timestamp()
  var delay = __wsDelayT - parseInt(data['t']*1000, 10);
  var jitter = Math.abs(__wsDelayPrev - delay);

  __wsDelayN += 1;
  __wsDelay = __wsDelay + (delay - __wsDelay) / __wsDelayN;
  __wsJitter = __wsJitter + (jitter - __wsJitter) / __wsDelayN;
  __wsDelayPrev = delay;
  __wsJitterPrev = jitter;

  $("#wsDelay").html(parseInt(__wsDelay, 10));
  $("#wsJitter").html(parseInt(__wsJitter, 10));

}

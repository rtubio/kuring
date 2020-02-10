var url = "ws://localhost:8000/control";
var __wsock = new WebSocket(url);

__wsock.onopen = function() {
  log('ws::CONNECTED to : ' + url + '\n')
};

__wsock.onmessage = function (evt)
{
  var data = JSON.parse(evt.data);
  log('ws::Data RECEIVED: ' + data)
};

__wsock.onclose = function()
{
  log('ws::DISCONNECTED from : ' + url);
};

function requestData() {
  ws.send("get-data");
}

function log (message) {
  document.querySelector('#console').value += (message  + '\n');
}



var xpState = document.createElement("xpState");
xpState = "EMPTY";

document.querySelector('#db-play').onclick = function(e) {
  console.log('<play> clicked');
};

document.querySelector('#db-stop').onclick = function(e) {
  console.log('<stop> clicked');
};

document.querySelector('#db-pause').onclick = function(e) {
  console.log('<pause> clicked');
};

const socket = io();
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let drawing = false;
let current = { x: 0, y: 0 };

canvas.addEventListener("mousedown", (event) => {
  drawing = true;
  current.x = event.clientX;
  current.y = event.clientY;
});
canvas.addEventListener("mouseup", () => {
  drawing = false;
});
canvas.addEventListener("mousemove", (event) => {
  if (!drawing) return;

  drawLine(current.x, current.y, event.clientX, event.clientY);
  socket.emit("drawing", {
    x0: current.x,
    y0: current.y,
    x1: event.clientX,
    y1: event.clientY,
  });
  current.x = event.clientX;
  current.y = event.clientY;
});

function drawLine(x0, y0, x1, y1) {
  context.beginPath();
  context.moveTo(x0, y0);
  context.lineTo(x1, y1);
  context.strokeStyle = "black";
  context.lineWidth = 5;
  context.stroke();
  context.closePath();
}

socket.on("drawing", (data) => {
  drawLine(data.x0, data.y0, data.x1, data.y1);
});


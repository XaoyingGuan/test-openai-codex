const socket = io('http://localhost:3000');
let score = 0;
let highScore = 0;
let interval;
const size = 20;
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let snake = [{x: 9, y: 9}];
let food = {x: 5, y: 5};
let dir = {x: 0, y: 0};

function draw() {
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'lime';
  snake.forEach(s => ctx.fillRect(s.x*size, s.y*size, size-2, size-2));
  ctx.fillStyle = 'red';
  ctx.fillRect(food.x*size, food.y*size, size-2, size-2);
}

function update() {
  const head = {...snake[0]};
  head.x += dir.x; head.y += dir.y;
  if (head.x < 0 || head.x >= 20 || head.y < 0 || head.y >= 20 || snake.some(s => s.x===head.x && s.y===head.y)) {
    gameOver();
    return;
  }
  snake.unshift(head);
  if (head.x === food.x && head.y === food.y) {
    score++; document.getElementById('score').innerText = score;
    placeFood();
  } else {
    snake.pop();
  }
  draw();
}

function placeFood() {
  food = {x: Math.floor(Math.random()*20), y: Math.floor(Math.random()*20)};
}

function gameOver() {
  clearInterval(interval);
  fetch('/api/score', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({score})})
    .then(r=>r.json()).then(()=>loadLeaderboard());
  if (score > highScore) { highScore = score; document.getElementById('highScore').innerText = highScore; }
  score = 0; document.getElementById('score').innerText = score;
  snake = [{x:9,y:9}]; dir={x:0,y:0};
}

document.addEventListener('keydown', e => {
  if (e.key === 'ArrowUp' && dir.y===0) dir={x:0,y:-1};
  if (e.key === 'ArrowDown' && dir.y===0) dir={x:0,y:1};
  if (e.key === 'ArrowLeft' && dir.x===0) dir={x:-1,y:0};
  if (e.key === 'ArrowRight' && dir.x===0) dir={x:1,y:0};
});

function start() {
  placeFood();
  draw();
  interval = setInterval(update, 200);
}

function loadLeaderboard() {
  fetch('/api/leaderboard').then(r=>r.json()).then(data => {
    const ul = document.getElementById('leaderboard');
    ul.innerHTML = '';
    data.forEach(row => {
      const li = document.createElement('li');
      li.textContent = `${row.email}: ${row.highScore}`;
      ul.appendChild(li);
    });
  });
}

// Auth
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');
registerBtn.onclick = () => {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})}).then(r=>r.json()).then(a=>alert(a.message));
};
loginBtn.onclick = () => {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})}).then(r=>r.json()).then(a=>{
    alert(a.message);
    highScore = a.highScore || 0; document.getElementById('highScore').innerText = highScore; start();
    loadLeaderboard();
  });
};

socket.on('scoreUpdate', loadLeaderboard);

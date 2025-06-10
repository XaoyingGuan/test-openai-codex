const express = require('express');
const session = require('express-session');
const bcrypt = require('bcrypt');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const db = require('./database');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*'
  }
});

app.use(cors({ origin: '*' }));
app.use(express.json());
app.use(session({
  secret: 'snake-secret',
  resave: false,
  saveUninitialized: false
}));

// Register user
app.post('/api/register', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ message: 'Missing fields' });
  const hashed = await bcrypt.hash(password, 10);
  const stmt = db.prepare('INSERT INTO users(email, password) VALUES(?, ?)');
  stmt.run(email, hashed, err => {
    if (err) return res.status(400).json({ message: 'User exists' });
    res.json({ message: 'Registered' });
  });
});

// Login user
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  db.get('SELECT * FROM users WHERE email = ?', [email], async (err, row) => {
    if (err || !row) return res.status(400).json({ message: 'Invalid credentials' });
    const match = await bcrypt.compare(password, row.password);
    if (!match) return res.status(400).json({ message: 'Invalid credentials' });
    req.session.userId = row.id;
    res.json({ message: 'Logged in', highScore: row.highScore });
  });
});

// Update high score
app.post('/api/score', (req, res) => {
  const { score } = req.body;
  const userId = req.session.userId;
  if (!userId) return res.status(401).json({ message: 'Not logged in' });
  db.get('SELECT highScore FROM users WHERE id = ?', [userId], (err, row) => {
    if (err || !row) return res.status(500).json({ message: 'User not found' });
    if (score > row.highScore) {
      db.run('UPDATE users SET highScore = ? WHERE id = ?', [score, userId]);
    }
    io.emit('scoreUpdate');
    res.json({ message: 'Score recorded' });
  });
});

// Fetch leaderboard
app.get('/api/leaderboard', (req, res) => {
  db.all('SELECT email, highScore FROM users ORDER BY highScore DESC LIMIT 10', (err, rows) => {
    res.json(rows || []);
  });
});

io.on('connection', socket => {
  socket.on('disconnect', () => { });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));

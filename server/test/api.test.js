const assert = require('assert');
const request = require('supertest');

process.env.DB_PATH = ':memory:';
const { app } = require('../app');

const agent = request.agent(app);
const user = { email: 'tester@example.com', password: 'secret' };

describe('Snake API', function() {
  it('registers a new user', async function() {
    const res = await agent
      .post('/api/register')
      .send(user)
      .expect(200);
    assert.strictEqual(res.body.message, 'Registered');
  });

  it('logs in the user', async function() {
    const res = await agent
      .post('/api/login')
      .send(user)
      .expect(200);
    assert.strictEqual(res.body.message, 'Logged in');
  });

  it('records a score and returns it in the leaderboard', async function() {
    await agent.post('/api/score').send({ score: 10 }).expect(200);
    const lb = await agent.get('/api/leaderboard').expect(200);
    assert(Array.isArray(lb.body));
    assert.strictEqual(lb.body[0].email, user.email);
    assert.strictEqual(lb.body[0].highScore, 10);
  });
});

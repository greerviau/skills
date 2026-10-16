const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

function fixture(t) {
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'skill links ')));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const repo = path.join(root, 'checkout');
  const home = path.join(root, 'home');
  fs.mkdirSync(path.join(repo, 'scripts'), { recursive: true });
  fs.mkdirSync(home);
  fs.copyFileSync(path.join(__dirname, '../link-skills.sh'), path.join(repo, 'scripts/link-skills.sh'));
  const source = path.join(repo, 'skills/engineering/example');
  fs.mkdirSync(source, { recursive: true });
  fs.writeFileSync(path.join(source, 'SKILL.md'), 'first');
  const destinations = ['.agents/skills', '.claude/skills'].map(p => path.join(home, p));
  const run = () => spawnSync('bash', [path.join(repo, 'scripts/link-skills.sh')], {
    env: { ...process.env, HOME: home }, encoding: 'utf8',
  });
  return { repo, home, source, destinations, run };
}

test('links shared harness locations and exposes edits immediately on repeated runs', t => {
  const f = fixture(t);
  for (let i = 0; i < 2; i++) assert.equal(f.run().status, 0);
  fs.writeFileSync(path.join(f.source, 'SKILL.md'), 'edited');
  for (const dest of f.destinations) {
    assert.equal(fs.realpathSync(path.join(dest, 'example')), f.source);
    assert.equal(fs.readFileSync(path.join(dest, 'example/SKILL.md'), 'utf8'), 'edited');
  }
});

test('removes retired checkout links and preserves unrelated links', t => {
  const f = fixture(t);
  assert.equal(f.run().status, 0);
  for (const dest of f.destinations) {
    fs.symlinkSync(path.join(f.repo, 'skills/engineering/retired'), path.join(dest, 'retired'));
    fs.symlinkSync('/missing/unrelated', path.join(dest, 'unrelated'));
  }
  assert.equal(f.run().status, 0);
  for (const dest of f.destinations) {
    assert.equal(fs.readdirSync(dest).includes('retired'), false, 'retired link remains');
    assert.equal(fs.readlinkSync(path.join(dest, 'unrelated')), '/missing/unrelated');
  }
});

test('refuses installed copies before changing any destination', t => {
  const f = fixture(t);
  const installed = path.join(f.destinations[1], 'example');
  fs.mkdirSync(installed, { recursive: true });
  fs.writeFileSync(path.join(installed, 'SKILL.md'), 'installed copy');
  assert.notEqual(f.run().status, 0, 'installed copy was overwritten');
  assert.equal(fs.readFileSync(path.join(installed, 'SKILL.md'), 'utf8'), 'installed copy');
  assert.equal(fs.existsSync(f.destinations[0]), false);
});

test('rejects a destination symlink into the checkout before changing files', t => {
  const f = fixture(t);
  fs.mkdirSync(path.dirname(f.destinations[1]), { recursive: true });
  fs.symlinkSync(path.join(f.repo, 'skills'), f.destinations[1]);
  assert.notEqual(f.run().status, 0);
  assert.equal(fs.existsSync(path.join(f.repo, 'skills/example')), false);
});

// Kör med: node --test scripts/worktree/worktree.test.mjs
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { assertLocal, assertOwnedDatabase, assertSafeName, databaseName, parseConnection, withDatabase, worktreeSlug } from './worktree.mjs';

const local = (host) => parseConnection(`Host=${host};Database=HealthAppDb;Username=postgres;Password=x`);

for (const host of ['localhost', 'LOCALHOST', '127.0.0.1', '::1']) {
  test(`godkänner ${host}`, () => assert.doesNotThrow(() => assertLocal(local(host))));
}
for (const host of ['localhost.example.com', 'example.com', '127.0.0.2', 'localhost,prod.example.com']) {
  test(`vägrar ${host}`, () => assert.throws(() => assertLocal(local(host))));
}

test('slug och databasnamn saneras även med udda mappnamn', () => {
  const slug = worktreeSlug('C:/repos/feat"; DROP DATABASE x;--');
  assert.match(slug, /^[a-z0-9_]+$/);
  const name = databaseName('HealthAppDb', slug);
  assert.doesNotThrow(() => assertSafeName(name));
  assert.ok(name.length <= 63);
});

test('vägrar källdatabas med otillåtna tecken', () => {
  for (const name of ['a"b', "a'b", 'a;b', 'a b']) assert.throws(() => assertSafeName(name));
});

test('raderar bara databaser som tillhör den här worktreen', () => {
  const slug = worktreeSlug('C:/repos/wt-a');
  assert.doesNotThrow(() => assertOwnedDatabase(`HealthAppDb_wt_${slug}`, slug));
  assert.throws(() => assertOwnedDatabase('prod_wt_data', slug));
  assert.throws(() => assertOwnedDatabase(`HealthAppDb_wt_${worktreeSlug('C:/repos/wt-b')}`, slug));
  assert.throws(() => assertOwnedDatabase(`HealthAppDb_wt_${slug}_extra`, slug));
});

test('byter bara databas i anslutningssträngen', () => {
  const value = 'Host=localhost;Database=A;Username=u;Password=Database=x';
  assert.equal(withDatabase(value, 'B'), 'Host=localhost;Database=B;Username=u;Password=Database=x');
});

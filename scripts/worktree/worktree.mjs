#!/usr/bin/env node
// Ger varje worktree egna lokala databaser och en egen port.
//   node scripts/worktree/worktree.mjs ensure        skapar kopior av databaserna och .worktree/env.json
//   node scripts/worktree/worktree.mjs drop          tar bort worktreens kopior
//   node scripts/worktree/worktree.mjs exec <cmd>    kör ett kommando med worktreens inställningar
//
// Säkerhet: skriptet vägrar köra mot andra värdar än localhost, kräver ofarliga databasnamn och
// raderar bara databaser vars namn slutar med _wt_ plus den här worktreens exakta id.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { basename, join, resolve } from 'node:path';

export const connectionKeys = ['DefaultConnection', 'DataConnection'];

export function parseConnection(value) {
  const parts = {};
  for (const part of value.split(';')) {
    const index = part.indexOf('=');
    if (index > 0) parts[part.slice(0, index).trim().toLowerCase()] = part.slice(index + 1).trim();
  }
  return {
    host: parts.host ?? parts.server ?? 'localhost',
    port: parts.port ?? '5432',
    database: parts.database ?? parts.db,
    username: parts.username ?? parts['user id'] ?? parts.userid ?? parts.user,
    password: parts.password ?? parts.pwd ?? '',
  };
}

export function assertLocal(connection) {
  if (!['localhost', '127.0.0.1', '::1'].includes(connection.host.toLowerCase())) {
    throw new Error('Vägrar köra: databasen ligger inte på localhost.');
  }
  if (!connection.database || !connection.username) {
    throw new Error('Anslutningssträngen saknar databas eller användare.');
  }
}

export function assertSafeName(name) {
  if (!/^[A-Za-z0-9_]+$/.test(name)) throw new Error('Vägrar köra: databasnamnet innehåller otillåtna tecken.');
}

export function assertOwnedDatabase(name, slug) {
  assertSafeName(name);
  if (!name.endsWith(`_wt_${slug}`)) throw new Error(`Vägrar radera ${name}: den tillhör inte den här worktreen.`);
}

export function withDatabase(value, database) {
  return value.replace(/((?:^|;)\s*(?:database|db)\s*=)[^;]*/i, `$1${database}`);
}

export function worktreeSlug(path) {
  const hash = createHash('sha1').update(resolve(path).toLowerCase()).digest('hex').slice(0, 8);
  const name = basename(path).toLowerCase().replace(/[^a-z0-9]+/g, '_').slice(0, 20);
  return `${name}_${hash}`;
}

export function databaseName(source, slug) {
  return `${source.slice(0, 25)}_wt_${slug}`;
}

export function apiPort(slug) {
  return 5200 + (parseInt(slug.slice(-8), 16) % 600);
}

function findTool(tool) {
  const probe = spawnSync(tool, ['--version'], { stdio: 'ignore' });
  if (!probe.error) return tool;
  const base = 'C:\\Program Files\\PostgreSQL';
  if (existsSync(base)) {
    for (const version of readdirSync(base).sort().reverse()) {
      const candidate = join(base, version, 'bin', `${tool}.exe`);
      if (existsSync(candidate)) return candidate;
    }
  }
  throw new Error(`Hittar inte ${tool}. Installera PostgreSQL-klienten eller lägg den i PATH.`);
}

function run(command, args, env = {}, options = {}) {
  const result = spawnSync(command, args, { encoding: 'utf8', env: { ...process.env, ...env }, ...options });
  if (result.error) throw result.error;
  return result;
}

function psql(connection, database, sql) {
  return run(findTool('psql'), ['-h', connection.host, '-p', connection.port, '-U', connection.username, '-d', database, '-v', 'ON_ERROR_STOP=1', '-Atc', sql], { PGPASSWORD: connection.password });
}

function checked(result, what) {
  if (result.status !== 0) throw new Error(`${what} misslyckades: ${(result.stderr ?? '').replace(/PGPASSWORD=\S+/g, '')}`);
  return result;
}

function databaseExists(connection, name) {
  return checked(psql(connection, 'postgres', `SELECT 1 FROM pg_database WHERE datname = '${name}'`), 'Kontrollen').stdout.trim() === '1';
}

function cloneDatabase(connection, target, workDir) {
  checked(psql(connection, 'postgres', `CREATE DATABASE "${target}"`), 'Skapandet av databasen');
  const dump = join(workDir, `${target}.sql`);
  const tool = { PGPASSWORD: connection.password };
  const base = ['-h', connection.host, '-p', connection.port, '-U', connection.username];
  try {
    checked(run(findTool('pg_dump'), [...base, '--no-owner', '--no-privileges', '-f', dump, connection.database], tool), 'Kopieringen');
    checked(run(findTool('psql'), [...base, '-d', target, '-v', 'ON_ERROR_STOP=1', '-q', '-f', dump], tool), 'Inläsningen');
  } catch (error) {
    psql(connection, 'postgres', `DROP DATABASE IF EXISTS "${target}"`);
    throw error;
  } finally {
    rmSync(dump, { force: true });
  }
}

function readSecrets(rootPath) {
  const result = run('dotnet', ['user-secrets', 'list', '--project', join(rootPath, 'Mintakt.API.csproj')]);
  const secrets = {};
  if (result.status !== 0) throw new Error('Kunde inte läsa User Secrets i huvudmappen.');
  for (const key of connectionKeys) {
    const line = result.stdout.split(/\r?\n/).find((row) => row.startsWith(`ConnectionStrings:${key} = `));
    if (!line) throw new Error(`ConnectionStrings:${key} saknas i User Secrets.`);
    secrets[key] = line.slice(line.indexOf(' = ') + 3).trim();
  }
  return secrets;
}

function ensure(paths) {
  const stateDir = join(paths.worktree, '.worktree');
  mkdirSync(stateDir, { recursive: true });
  const slug = worktreeSlug(paths.worktree);
  const secrets = readSecrets(paths.root);
  const env = { ASPNETCORE_ENVIRONMENT: 'Development', ASPNETCORE_URLS: `http://localhost:${apiPort(slug)}` };
  const databases = [];

  for (const key of connectionKeys) {
    const source = parseConnection(secrets[key]);
    assertLocal(source);
    assertSafeName(source.database);
    const target = databaseName(source.database, slug);
    if (!databaseExists(source, target)) {
      console.log(`Skapar ${target} från ${source.database} ...`);
      cloneDatabase(source, target, stateDir);
    }
    env[`ConnectionStrings__${key}`] = withDatabase(secrets[key], target);
    databases.push({ key, name: target });
  }

  writeFileSync(join(stateDir, 'env.json'), JSON.stringify({ env, databases }, null, 2));

  const rootEnv = join(paths.root, 'data', '.env');
  const localEnv = join(paths.worktree, 'data', '.env');
  if (resolve(rootEnv) !== resolve(localEnv) && existsSync(rootEnv)) {
    copyFileSync(rootEnv, localEnv);
    const data = databases.find((item) => item.key === 'DataConnection').name;
    const text = readFileSync(localEnv, 'utf8').replace(/^(DATABASE_URL=.*\/)[^/?\r\n]+/m, `$1${data}`);
    writeFileSync(localEnv, text);
  }
  console.log(`Klart. API-adress: ${env.ASPNETCORE_URLS}`);
}

function drop(paths) {
  const file = join(paths.worktree, '.worktree', 'env.json');
  if (!existsSync(file)) return;
  const state = JSON.parse(readFileSync(file, 'utf8'));
  const slug = worktreeSlug(paths.worktree);
  for (const { key, name } of state.databases) {
    assertOwnedDatabase(name, slug);
    const connection = parseConnection(state.env[`ConnectionStrings__${key}`]);
    assertLocal(connection);
    checked(psql(connection, 'postgres', `DROP DATABASE IF EXISTS "${name}" WITH (FORCE)`), 'Borttagningen');
    console.log(`Tog bort ${name}`);
  }
}

function execute(paths, args) {
  const state = JSON.parse(readFileSync(join(paths.worktree, '.worktree', 'env.json'), 'utf8'));
  const result = spawnSync(args[0], args.slice(1), { stdio: 'inherit', env: { ...process.env, ...state.env } });
  process.exit(result.status ?? 1);
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(import.meta.filename)) {
  const worktree = process.env.ORCA_WORKTREE_PATH || process.cwd();
  const paths = { worktree, root: process.env.ORCA_ROOT_PATH || worktree };
  const [command, ...args] = process.argv.slice(2);
  try {
    if (command === 'ensure') ensure(paths);
    else if (command === 'drop') drop(paths);
    else if (command === 'exec' && args.length) execute(paths, args);
    else throw new Error('Använd: ensure, drop eller exec <kommando>');
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

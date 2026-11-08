// Kör med: node --test .claude/hooks/block-dangerous.test.mjs
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const hook = fileURLToPath(new URL('./block-dangerous.mjs', import.meta.url));
const status = (command) => spawnSync(process.execPath, [hook], { input: JSON.stringify({ tool_input: { command } }) }).status;

const blocked = [
  'git push --force origin x', 'GIT PUSH -F', 'git push --force-with-lease', 'git push origin master', 'git push origin HEAD:main', 'git push origin +master',
  'git reset --hard HEAD~1', 'git clean -fd', 'rm -rf bin', 'rm -r -f bin', 'rm -f -r bin', 'rm --recursive bin', 'find . -name x -delete',
  'rmdir /s obj', 'Remove-Item obj -Recurse', 'psql -c "drop table users"', 'psql -c "DROP DATABASE x"', 'truncate table users', 'dropdb x', 'dotnet ef database drop',
  'dotnet user-secrets list', 'cat %APPDATA%/Microsoft/UserSecrets/abc/secrets.json', 'cat data/.env', 'cat .worktree/env.json', 'env', 'printenv', 'env | grep Jwt', 'Get-ChildItem Env:', 'cat ~/.ssh/id_rsa',
];
const allowed = [
  'dotnet test', 'git status', 'git push origin feat/x', 'git push -u origin feat/force-login', 'git push origin feat/main', 'rm file.txt', 'git log --format=%f', 'grep -r master src',
  'git checkout -b fix/reset-hard-doc', 'dotnet ef migrations add X', 'find . -name "*.cs"', 'node scripts/worktree/worktree.mjs exec dotnet run --no-launch-profile', 'cat appsettings.environment.md', 'env FOO=1 dotnet test',
];

for (const command of blocked) test(`blockerar: ${command}`, () => assert.equal(status(command), 2));
for (const command of allowed) test(`tillåter: ${command}`, () => assert.equal(status(command), 0));

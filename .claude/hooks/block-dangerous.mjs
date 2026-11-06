#!/usr/bin/env node
// PreToolUse-hook: stoppar vanliga kommandon som inte går att ångra. Exit 2 blockerar kommandot.
// Det här är ett skyddsnät och ingen säkerhetsgräns. Omskrivna kommandon, skript och andra
// program kan ta sig förbi blocklistan. Se "Hookens begränsningar" i CLAUDE.md.
let input = '';
for await (const chunk of process.stdin) input += chunk;

let command = '';
try {
  command = JSON.parse(input)?.tool_input?.command ?? '';
} catch {
  process.exit(0);
}

const rules = [
  [/\bgit\s+push\b[^|;&]*(--force\b|--force-with-lease\b|\s-f\b)/i, 'force push'],
  [/\bgit\s+reset\s+--hard\b/i, 'git reset --hard'],
  [/\bgit\s+clean\b[^|;&]*\s-[a-z]*f/i, 'git clean -f'],
  [/\bgit\s+push\b[^|;&]*[\s:+](origin\s+)?(master|main)\b/i, 'direkt push till huvudbranchen'],
  [/\b(rm|del|rmdir|rd)\b[^|;&]*\s(-[a-z]*r[a-z]*f?|-[a-z]*f[a-z]*r|\/s)\b/i, 'rekursiv radering'],
  [/\brm\b[^|;&]*--(recursive|force)\b/i, 'rekursiv radering'],
  [/\bfind\b[^|;&]*\s-delete\b/i, 'radering med find'],
  [/\bRemove-Item\b[^|;&]*-Recurse/i, 'rekursiv radering'],
  [/\b(drop\s+(database|schema|table)|truncate\s+table)\b/i, 'radering i databasen'],
  [/\b(dropdb|dotnet\s+ef\s+database\s+drop)\b/i, 'radering av databas'],
  [/\bdotnet\s+user-secrets\s+(list|set|remove|clear)\b/i, 'åtkomst till hemligheter'],
  [/usersecrets|secrets\.json|(^|[\s"'/\\])\.env\b|\.worktree[/\\]env\.json/i, 'åtkomst till hemligheter'],
  [/(^|[\s;|&])(env|printenv)(\s*($|[;|&]))/i, 'utskrift av miljövariabler'],
  [/\bGet-ChildItem\s+Env:|\bgci\s+Env:|\bdir\s+Env:/i, 'utskrift av miljövariabler'],
  [/(^|[\s"'/\\])\.ssh([\s"'/\\]|$)/i, 'åtkomst till SSH-nycklar'],
];

for (const [pattern, reason] of rules) {
  if (pattern.test(command)) {
    console.error(`Blockerat av hook: ${reason}. Be Hamze köra kommandot själv om det verkligen behövs.`);
    process.exit(2);
  }
}
process.exit(0);

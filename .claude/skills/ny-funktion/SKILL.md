---
name: ny-funktion
description: Tar en funktion från idé till pull request med Spec Kit och separata granskare. Använd när en ny funktion eller större fix ska byggas.
---
Följ stegen i ordning. Stanna vid varje **STOPP** och vänta på Hamzes svar.

1. Kolla vad som pågår med `git worktree list` och `gh pr list`. Rör en annan uppgift samma filer? Säg det och **STOPP**.
2. Kör `/speckit-specify` och sedan `/speckit-clarify` med beskrivningen: $ARGUMENTS. **STOPP**: Hamze läser specen.
3. Kör `/speckit-plan`, `/speckit-tasks` och `/speckit-analyze`. **STOPP**: Hamze godkänner planen.
4. Kör `/speckit-implement`. Skriv testet först och se det bli rött innan koden skrivs.
5. Kör `dotnet build` och `dotnet test`. Fortsätt inte förrän allt är grönt.
6. Skapa mappen `.worktree` om den saknas och kör `git diff origin/master...HEAD > .worktree/review.diff`.
7. Starta agenterna `kodgranskare` och `sakerhetsgranskare` parallellt. Åtgärda blockerande fynd och granska igen.
8. Är ändringen större än 400 rader, utan genererade filer? Föreslå en uppdelning och **STOPP**.
9. **STOPP**: visa sammanfattning och granskningsresultat. Skapa pull requesten med `gh pr create` först när Hamze säger ja. Merga aldrig själv.

Ändras ett krav under arbetet? Uppdatera specen först, inte bara koden.

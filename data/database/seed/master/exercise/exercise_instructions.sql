-- ============================================================
-- seed_exercise_instructions.sql
-- Instructions och common_mistakes för de viktigaste övningarna
-- Coach priority >= 8, compound övningar
-- ============================================================

-- ── BÄNKPRESS (id=1) ─────────────────────────────────────────
UPDATE exercises SET
  instructions = 'Ligg på bänken med fötterna plant i golvet. Grip stången lite bredare än axelbredden. Sänk stången kontrollerat till bröstet. Pressa upp till utsträckta armar. Håll skulderbladen indragna under hela rörelsen.',
  common_mistakes = 'Lyfter fötterna från golvet. Stången studsar mot bröstet. För smalt eller brett grepp. Armbågarna utåt vid 90 grader (ska vara ca 45-75 grader).',
  cues = ARRAY['Dra stången isär', 'Skulderbladen ner och in', 'Fötterna i golvet', 'Pressa bröstkorgen upp mot stången']
WHERE id = 1;

-- ── KNÄBÖJ (id=5) ────────────────────────────────────────────
UPDATE exercises SET
  instructions = 'Ställ stången på övre ryggen (low bar) eller trapeziusmuskeln (high bar). Fötterna axelbredd isär, tårna lätt utåt. Böj knäna och höfterna simultant, håll ryggen rak. Sänk tills låren är parallella eller djupare. Driv upp genom hälarna.',
  common_mistakes = 'Knäna kollapsar inåt (valgus). Hälen lyfts från golvet. Överkroppen lutar för mycket framåt. Ryggen rundar i botten av rörelsen.',
  cues = ARRAY['Knäna utåt', 'Bröstet upp', 'Hälarna i golvet', 'Andas in nedåt, ut uppåt']
WHERE id = 5;

-- ── MARKLYFT (id=3) ──────────────────────────────────────────
UPDATE exercises SET
  instructions = 'Stå med fötterna höftbredd isär, stången över mitten av foten. Grip stången axelbredd. Sänk höfterna, håll ryggen rak och neutral. Lyft stången tätt längs benen. Lås ut höfterna och knäna i topp. Kontrollerat ned i omvänd ordning.',
  common_mistakes = 'Stången för långt från kroppen. Ryggen rundar i botten. Höfterna skjuts upp för tidigt (stiff-leg). Låser inte ut höfterna i topp.',
  cues = ARRAY['Stången tätt mot benen', 'Ryggen rak som en planka', 'Tryck golvet nedåt', 'Lås ut höfterna i topp']
WHERE id = 3;

-- ── MILITÄRPRESS (id=7) ──────────────────────────────────────
UPDATE exercises SET
  instructions = 'Stå med fötterna axelbredd isär. Grip stången lite bredare än axelbredden. Pressa stången rakt upp ovanför huvudet. Håll core spänt under hela rörelsen. Sänk kontrollerat tillbaka till axelhöjd.',
  common_mistakes = 'Lutar bakåt för att hjälpa rörelsen (börjar likna standing incline). Låser inte armbågarna i topp. Pressa inte stången rakt upp (ska röra sig lätt bakåt för att undvika ansiktet).',
  cues = ARRAY['Core spänt', 'Pressa upp och lätt bakåt', 'Lås ut armbågarna i topp', 'Kontrollerat ned']
WHERE id = 7;

-- ── LATSDRAG (id=4) ──────────────────────────────────────────
UPDATE exercises SET
  instructions = 'Sitt med låren under vadderna. Grip stången bredare än axelbredden med overhands grepp. Luta överkroppen lätt bakåt. Dra stången mot övre bröstet medan du drar armbågarna ned och bakåt. Kontrollerat upp.',
  common_mistakes = 'Drar bakom nacken (belastar nacken onödigt). Använder för mycket biceps istället för ryggen. Lutar för mycket bakåt och gör det till en rodd.',
  cues = ARRAY['Armbågarna ner mot fickan', 'Skulderbladen ihop och ner', 'Tänk: kläm en apelsin i armhålan', 'Bröstkorgen möter stången']
WHERE id = 4;

-- ── ROMANIAN DEADLIFT (id=74) ────────────────────────────────
UPDATE exercises SET
  instructions = 'Stå med stången i händerna, höftbredd isär. Håll ryggen rak och neutral. Böj framåt i höfterna (hinge) medan du sänker stången längs benen. Sträck höfterna framåt för att återgå till startposition. Knäna lätt böjda under hela rörelsen.',
  common_mistakes = 'Böjer i ryggen istället för höfterna. Går för djupt och rundar ländrygg. Stången för långt från kroppen. Låser knäna helt.',
  cues = ARRAY['Skjut höfterna bakåt', 'Stången tätt mot benen', 'Känn sträcken i hamstrings', 'Ryggen rak hela vägen']
WHERE id = 74;

-- ── DUMBBELL BENCH PRESS (id=107) ────────────────────────────
UPDATE exercises SET
  instructions = 'Ligg på bänken med en hantel i varje hand. Håll hantelarna vid brösthöjd med handflatorna framåt. Pressa upp till utsträckta armar. Sänk kontrollerat tillbaka. Mer rörelseomfång än skivstångsvarianten.',
  common_mistakes = 'Hantelarna rör sig i olika hastighet. Armbågarna för långt ut (>90 grader). Tappar kontrollen i nedre position.',
  cues = ARRAY['Hantelarna parallella', 'Kontrollerat ned', 'Pressa in mot varandra i toppen', 'Skulderbladen ner och in']
WHERE id = 107;

-- ── DUMBBELL ROW (id=117) ────────────────────────────────────
UPDATE exercises SET
  instructions = 'Stöd ena knät och handen på bänken. Håll ryggen horisontell. Dra hanteln upp mot höften med armbågen nära kroppen. Kontrollerat ned. Håll skulderbladen stabila under rörelsen.',
  common_mistakes = 'Roterar kroppen för att hjälpa rörelsen. Drar mot axeln istället för höften. Sänker för snabbt ned.',
  cues = ARRAY['Armbågen tätt mot kroppen', 'Dra mot höften', 'Skulderbladen stabila', 'Full rörelseomfång']
WHERE id = 117;

-- ── BULGARIAN SPLIT SQUAT (id=79) ────────────────────────────
UPDATE exercises SET
  instructions = 'Placera bakre foten på en bänk. Frambenet axelbredd från bänken. Sänk kroppen vertikalt tills bakre knät nästan nuddar golvet. Frambenet gör jobbet — driv upp genom framhälen.',
  common_mistakes = 'Framfoten för nära bänken (knät går för långt framför tån). Lutar för mycket framåt. Bakre knät dunkar i golvet.',
  cues = ARRAY['Vertikalt ned', 'Bröst upp', 'Framhälen i golvet', 'Bakre benet passivt']
WHERE id = 79;

-- ── UTFALL (id=6) ────────────────────────────────────────────
UPDATE exercises SET
  instructions = 'Stå upprätt med fötterna höftbredd isär. Ta ett stort steg framåt. Sänk bakre knät mot golvet. Frambenet ska ha knät ungefär ovanför hälen. Driv upp och återgå till startposition eller ta nästa steg.',
  common_mistakes = 'Knät går långt framför tån. Överkroppen lutar framåt. Steget för kort (instabilt).',
  cues = ARRAY['Vertikalt ned, inte framåt', 'Bröst upp', 'Bakre knät mot golvet', 'Driv upp genom framhälen']
WHERE id = 6;

-- ── ROMANIAN DEADLIFT WITH DUMBBELLS (id=192) ────────────────
UPDATE exercises SET
  instructions = 'Stå med hantlar framför låren. Samma teknik som barbell RDL men med hantlar som kan röra sig längs benen mer naturligt. Bra för nybörjare som lär sig hip hinge-mönstret.',
  common_mistakes = 'Böjer i ryggen. Hantelarna för långt från kroppen. Går för djupt och tappar neutral rygg.',
  cues = ARRAY['Höfterna bakåt', 'Hantlar tätt mot benen', 'Neutral rygg', 'Känn hamstrings sträcka']
WHERE id = 192;

-- Verifiera
SELECT
  COUNT(*) FILTER (WHERE instructions IS NOT NULL) AS har_instructions,
  COUNT(*) FILTER (WHERE common_mistakes IS NOT NULL) AS har_common_mistakes,
  COUNT(*) FILTER (WHERE cues IS NOT NULL) AS har_cues
FROM exercises;
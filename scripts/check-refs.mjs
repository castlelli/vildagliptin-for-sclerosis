// Checks the built pages: every in-text citation resolves to a reference,
// every reference is cited at least once, and EN and PT number them identically.
import { readFileSync } from 'node:fs';

const pages = { en: 'dist/index.html', pt: 'dist/pt/index.html' };
let failed = false;
const seen = {};
for (const [lang, file] of Object.entries(pages)) {
  const html = readFileSync(file, 'utf8');
  const listed = [...html.matchAll(/<li id="ref-(\d+)"/g)].map((m) => +m[1]);
  const cited = new Set();
  for (const m of html.matchAll(/<sup class="cite">(.*?)<\/sup>/g)) {
    for (const part of m[1].replace(/<[^>]+>/g, '').split(',')) {
      const [a, b] = part.split('–').map(Number);
      for (let n = a; n <= (b || a); n++) cited.add(n);
    }
  }
  const missing = [...cited].filter((n) => !listed.includes(n));
  const uncited = listed.filter((n) => !cited.has(n));
  const order = [...html.matchAll(/data-refs="([^"]+)"/g)].flatMap((m) => m[1].split(' '));
  seen[lang] = [...new Set(order)];
  console.log(`${lang}: ${listed.length} references, ${cited.size} cited, unresolved [${missing}], uncited [${uncited}]`);
  if (missing.length || uncited.length || listed.length !== cited.size) failed = true;
}
const same = JSON.stringify(seen.en) === JSON.stringify(seen.pt);
console.log(`EN/PT citation order identical: ${same}`);
if (!same) failed = true;
process.exit(failed ? 1 : 0);

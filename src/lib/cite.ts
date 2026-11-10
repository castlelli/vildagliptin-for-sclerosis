import refsRaw from '../data/references.json';

export interface Ref {
  key: string;
  authors: string[];
  etAl?: boolean;
  title: string;
  journal?: string;
  volume?: string;
  pages?: string;
  year: number | string;
  doi?: string;
  pmid?: string;
  url?: string;
  kind?: 'literature' | 'data' | 'method';
  verified?: boolean;
  note?: string;
}

export const refs: Ref[] = refsRaw as Ref[];
const byKey = new Map(refs.map((r) => [r.key, r]));

const CITE = /\[@([a-z0-9_;\s-]+)\]/gi;

/** Walk every string in a dictionary in document order (object key order). */
function* strings(node: unknown): Generator<string> {
  if (typeof node === 'string') yield node;
  else if (Array.isArray(node)) for (const n of node) yield* strings(n);
  else if (node && typeof node === 'object') for (const v of Object.values(node)) yield* strings(v);
}

/**
 * Number references by first appearance, Nature style.
 * `extra` lists keys cited outside the dictionary (charts, captions) in the
 * position they appear; they are appended where they are first seen.
 */
export function numbering(dict: unknown): Map<string, number> {
  const order = new Map<string, number>();
  for (const s of strings(dict)) {
    for (const m of s.matchAll(CITE)) {
      for (const k of m[1].split(';').map((x) => x.trim()).filter(Boolean)) {
        if (!byKey.has(k)) throw new Error(`Unknown reference key "${k}" in: ${s.slice(0, 80)}`);
        if (!order.has(k)) order.set(k, order.size + 1);
      }
    }
  }
  return order;
}

/** Compress [1,2,3,5] → "1–3,5". */
export function ranges(nums: number[]): string {
  const n = [...new Set(nums)].sort((a, b) => a - b);
  const out: string[] = [];
  for (let i = 0; i < n.length; i++) {
    let j = i;
    while (j + 1 < n.length && n[j + 1] === n[j] + 1) j++;
    out.push(j - i >= 2 ? `${n[i]}–${n[j]}` : j > i ? `${n[i]},${n[j]}` : `${n[i]}`);
    i = j;
  }
  return out.join(',');
}

function esc(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export function supFor(keys: string[], order: Map<string, number>): string {
  const nums = keys.map((k) => order.get(k)!).sort((a, b) => a - b);
  // link each run to its first reference
  const parts = ranges(nums).split(',').map((part) => {
    const first = part.split('–')[0];
    const ks = keys.filter((k) => {
      const n = order.get(k)!;
      const [a, b] = part.split('–').map(Number);
      return n >= a && n <= (b ?? a);
    });
    return `<a href="#ref-${first}" data-refs="${ks.join(' ')}">${part}</a>`;
  });
  return `<sup class="cite">${parts.join(',')}</sup>`;
}

/** Light markup: *em*, **strong**, `mono`, ~GENE~, [@key;key] citations. */
export function rich(text: string, order: Map<string, number>): string {
  let s = esc(text);
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/\*(.+?)\*/g, '<em>$1</em>');
  s = s.replace(/`(.+?)`/g, '<span class="mono">$1</span>');
  s = s.replace(/~(.+?)~/g, '<span class="gene">$1</span>');
  s = s.replace(CITE, (_, body: string) => supFor(body.split(';').map((x) => x.trim()).filter(Boolean), order));
  return s;
}

/** Keys cited in a string, for the margin column. */
export function keysIn(text: string): string[] {
  const out: string[] = [];
  for (const m of text.matchAll(CITE)) for (const k of m[1].split(';').map((x) => x.trim())) if (k && !out.includes(k)) out.push(k);
  return out;
}

export function getRef(key: string) {
  const r = byKey.get(key);
  if (!r) throw new Error(`Unknown reference ${key}`);
  return r;
}

/** Short margin form: "Soare, A. et al. Arthritis Rheumatol. (2020)" */
export function shortRef(r: Ref): string {
  if (r.kind === 'data') {
    const head = r.title.split(':')[0];
    return r.key.startsWith('geo') ? `NCBI GEO ${head}` : head.replace(/ \(.*$/, '');
  }
  const first = r.authors[0] ?? '';
  const more = r.authors.length > 1 || r.etAl ? ' et al.' : '';
  return `${first}${more} ${r.journal ?? ''} (${r.year})`.replace(/\s+/g, ' ').trim();
}

/** Full Nature style: Authors. Title. Journal Vol, pages (Year). */
export function fullRef(r: Ref): string {
  const a = r.authors.length > 5 || r.etAl ? `${r.authors.slice(0, 1).join(', ')} et al.` : joinAuthors(r.authors);
  const vol = r.volume ? ` <b>${esc(r.volume)}</b>` : '';
  const pg = r.pages ? `, ${esc(r.pages)}` : '';
  const j = r.journal ? ` <i>${esc(r.journal)}</i>${vol}${pg}` : '';
  return `${esc(a)} ${esc(r.title.replace(/\.$/, ''))}.${j} (${r.year}).`;
}

function joinAuthors(a: string[]) {
  if (a.length <= 1) return a.join('');
  return `${a.slice(0, -1).join(', ')} &amp; ${a[a.length - 1]}`.replace('&amp;', '&');
}

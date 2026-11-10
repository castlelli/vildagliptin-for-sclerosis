// Interactive re-plots of the study's results. Each chart reads its data from
// src/data/figures/*.json; exact vs approximate provenance is printed under it.
import * as d3 from 'd3';
import deg from '../data/figures/deg.json';
import cells from '../data/figures/dpp4-celltypes.json';
import states from '../data/figures/fibro-states.json';
import paga from '../data/figures/paga.json';
import progeny from '../data/figures/progeny.json';
import network from '../data/figures/network.json';
import mrss from '../data/figures/mrss.json';
import pk from '../data/figures/pk.json';
import landscape from '../data/figures/landscape.json';

type Sel = d3.Selection<SVGSVGElement, unknown, null, undefined>;
type L = Record<string, any>;

const v = (n: string) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const C = () => ({
  ink: v('--ink'), ink2: v('--ink-2'), ink3: v('--ink-3'), rule: v('--rule'), grid: v('--grid-strong'),
  tracer: v('--tracer'), tracerInk: v('--tracer-ink'), hema: v('--hema'), paper: v('--paper'), wash: v('--tracer-wash'),
  ok: v('--ok'),
});
const fmt = (x: number, d = 2) => (x < 0 ? '−' : '') + Math.abs(x).toFixed(d);
const pt = (l: L) => l.lang === 'pt';
const PT: Record<string, string> = {
  Fibroblast: 'Fibroblasto', Endothelial: 'Endotelial', Myeloid: 'Mieloide', Mast: 'Mastócito', Keratinocyte: 'Queratinócito',
  'T cell': 'Linfócito T', Pericyte: 'Pericito', Control: 'Controle', SSc: 'ES',
  'Activated fibroblast state': 'Estado de fibroblasto ativado', 'ECM program': 'Programa de MEC', 'DPP4-positive fraction': 'Fração DPP4-positiva',
  'Mean DPP4 expression': 'Expressão média de DPP4', 'Progenitor state': 'Estado progenitor', 'Myofibroblast state': 'Estado de miofibroblasto',
  'Integrin cell surface interactions': 'Interações de integrinas na superfície celular', Keratinization: 'Queratinização',
  'Extracellular matrix organization': 'Organização da matriz extracelular', 'Assembly of collagen fibrils and other multimeric structures': 'Montagem de fibrilas de colágeno e outras estruturas multiméricas',
  'ECM proteoglycans': 'Proteoglicanos da MEC', 'Collagen chain trimerization': 'Trimerização das cadeias de colágeno', 'Collagen formation': 'Formação de colágeno',
  'Collagen biosynthesis and modifying enzymes': 'Biossíntese de colágeno e enzimas modificadoras', 'Degradation of the extracellular matrix': 'Degradação da matriz extracelular',
  'Collagen degradation': 'Degradação de colágeno',
};
const tr = (s: string, l: L) => (pt(l) && PT[s]) || s;
const num = (x: number, d: number, l: L) => (pt(l) ? fmt(x, d).replace('.', ',') : fmt(x, d));

function frame(el: HTMLElement, height: number, minW = 300) {
  el.innerHTML = '';
  const w = Math.max(minW, el.clientWidth);
  const svg = d3.select(el).append('svg')
    .attr('viewBox', `0 0 ${w} ${height}`).attr('width', w).attr('height', height)
    .attr('role', 'img') as unknown as Sel;
  return { svg, w };
}

function tooltip(el: HTMLElement) {
  let tip = el.querySelector<HTMLElement>('.tip');
  if (!tip) { tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; el.appendChild(tip); }
  const t = tip;
  return {
    show(html: string, x: number, y: number) {
      t.innerHTML = html; t.hidden = false;
      const w = t.offsetWidth;
      t.style.left = `${Math.max(0, Math.min(x - w / 2, el.clientWidth - w))}px`;
      t.style.top = `${y - t.offsetHeight - 10}px`;
    },
    hide() { t.hidden = true; },
  };
}

function provenance(el: HTMLElement, l: L, kind: 'exact' | 'approx' | 'model' | 'mixed', extra = '') {
  const p = document.createElement('p');
  p.className = `prov prov-${kind}`;
  const text = kind === 'exact' ? l.ui.exact : kind === 'approx' ? l.ui.approx : kind === 'model' ? l.ui.model : `${l.ui.exact} ${l.ui.approx}`;
  p.textContent = `${text}${extra ? ' ' + extra : ''}`;
  el.appendChild(p);
}

function axisStyle(g: d3.Selection<SVGGElement, unknown, null, undefined>) {
  g.attr('class', 'axis');
  g.select('.domain').remove();
  return g;
}

function panelTitle(svg: Sel, x: number, y: number, text: string, letter: string) {
  const t = svg.append('text').attr('class', 'panel-title').attr('x', x).attr('y', y);
  t.append('tspan').attr('class', 'panel-letter').text(letter + ' ');
  t.append('tspan').text(text);
}

/* ---------- selectivity ruler ---------- */
function ruler(el: HTMLElement, l: L) {
  const c = C();
  const enz = Object.entries(pk.offTargets_nM).map(([name, ic]) => ({ name, ic: ic as number }));
  let conc = pk.params.free_plasma_peak_nM;
  const wrap = document.createElement('div');
  el.innerHTML = '';
  const plot = document.createElement('div');
  el.append(plot, wrap);
  const control = document.createElement('label');
  control.className = 'range-row';
  control.innerHTML = `<span>${l.exposure}</span><input type="range" min="0" max="400" step="1" aria-label="${l.exposure}"><output></output>`;
  wrap.appendChild(control);
  const input = control.querySelector('input')!;
  const output = control.querySelector('output')!;
  const toPos = (x: number) => Math.round((Math.log10(x) / 4) * 400);
  const fromPos = (p: number) => 10 ** ((p / 400) * 4);
  input.value = String(toPos(conc));

  const draw = () => {
    const { svg, w } = frame(plot, 190);
    svg.attr('aria-label', `IC50 ruler. ${enz.map((e) => `${e.name} ${e.ic} nM`).join(', ')}.`);
    const x = d3.scaleLog().domain([1, 10000]).range([24, w - 24]);
    svg.append('g').attr('transform', 'translate(0,120)').call(
      (g) => axisStyle(g.call(d3.axisBottom(x).tickValues([1, 10, 100, 1000, 10000]).tickFormat((d) => `${d3.format(',')(+d)} nM`))),
    );
    // minor ticks
    svg.append('g').selectAll('line').data(d3.range(0, 4).flatMap((p) => d3.range(2, 10).map((m) => m * 10 ** p)))
      .join('line').attr('x1', (d) => x(d)).attr('x2', (d) => x(d)).attr('y1', 116).attr('y2', 120).attr('stroke', c.grid);
    svg.append('line').attr('x1', x(1)).attr('x2', x(10000)).attr('y1', 120).attr('y2', 120).attr('stroke', c.ink);
    // shaded blocked region
    svg.append('rect').attr('x', x(1)).attr('y', 34).attr('width', Math.max(0, x(conc) - x(1))).attr('height', 86)
      .attr('fill', c.wash).attr('opacity', 0.7);
    const g = svg.append('g').selectAll('g').data(enz).join('g').attr('transform', (d) => `translate(${x(d.ic)},0)`);
    g.append('line').attr('y1', 52).attr('y2', 120).attr('stroke', (d) => (d.name === 'DPP-4' ? c.tracer : c.ink)).attr('stroke-width', (d) => (d.name === 'DPP-4' ? 2 : 1));
    g.append('circle').attr('cy', 52).attr('r', 5).attr('fill', (d) => (conc >= d.ic ? (d.name === 'DPP-4' ? c.tracer : c.ink) : c.paper)).attr('stroke', (d) => (d.name === 'DPP-4' ? c.tracer : c.ink)).attr('stroke-width', 1.5);
    g.append('text').attr('y', 38).attr('text-anchor', (d) => (d.name === 'FAP' ? 'start' : d.name === 'DPP-8' ? 'end' : 'middle')).attr('dx', (d) => (d.name === 'FAP' ? 4 : d.name === 'DPP-8' ? -4 : 0)).attr('class', 'lbl-strong').text((d) => d.name);
    g.append('text').attr('y', (d) => (d.name === 'FAP' ? 156 : 142)).attr('text-anchor', (d) => (d.name === 'FAP' ? 'start' : d.name === 'DPP-8' ? 'end' : 'middle')).attr('class', 'lbl-num').attr('dy', 14)
      .text((d) => `${d3.format(',')(d.ic)} nM · ${Math.round((100 * conc) / (conc + d.ic))}%`);
    // exposure marker
    svg.append('line').attr('x1', x(conc)).attr('x2', x(conc)).attr('y1', 18).attr('y2', 120).attr('stroke', c.ink).attr('stroke-dasharray', '3 3');
    svg.append('text').attr('x', x(conc)).attr('y', 12).attr('text-anchor', x(conc) > w - 120 ? 'end' : 'start').attr('dx', x(conc) > w - 120 ? -4 : 4)
      .attr('class', 'lbl-num').text(`${d3.format(',.0f')(conc)} nM`);
    output.textContent = enz.map((e) => `${e.name}: ${conc >= e.ic ? l.blocked : l.spared}`).join(' · ');
  };
  input.addEventListener('input', () => { conc = fromPos(+input.value); draw(); });
  draw();
  return draw;
}

/* ---------- bulk DEG + Reactome ---------- */
function degChart(el: HTMLElement, l: L) {
  const c = C();
  const narrow = el.clientWidth < 760;
  const rowH = 24;
  const hA = deg.genes.length * rowH + 70;
  const hB = deg.pathways.length * rowH + 70;
  const { svg, w } = frame(el, narrow ? hA + hB + 20 : Math.max(hA, hB));
  svg.attr('aria-label', `${l.a}. ${deg.genes.map((g) => `${g.gene} ${fmt(g.diff)}`).join(', ')}`);
  const tip = tooltip(el);
  const colW = narrow ? w : (w - 40) / 2;
  // A
  const gA = svg.append('g');
  panelTitle(gA as any, 0, 16, l.a, 'a');
  const xA = d3.scaleLinear().domain([-0.3, 1.45]).range([70, colW - 10]);
  const yA = d3.scaleBand().domain(deg.genes.map((g) => g.gene)).range([40, hA - 30]).padding(0.3);
  gA.append('g').attr('transform', `translate(0,${hA - 30})`).call((g) => axisStyle(g.call(d3.axisBottom(xA).ticks(4))));
  gA.append('line').attr('x1', xA(0)).attr('x2', xA(0)).attr('y1', 36).attr('y2', hA - 30).attr('stroke', c.ink3).attr('stroke-dasharray', '2 3');
  const rows = gA.append('g').selectAll('g').data(deg.genes).join('g').attr('transform', (d) => `translate(0,${yA(d.gene)! + yA.bandwidth() / 2})`);
  rows.append('text').attr('x', 62).attr('text-anchor', 'end').attr('dy', '0.35em').attr('class', (d) => (d.gene === 'DPP4' ? 'lbl-gene hot' : 'lbl-gene')).text((d) => d.gene);
  rows.append('line').attr('x1', xA(0)).attr('x2', (d) => xA(d.diff)).attr('stroke', (d) => (d.sig ? c.ink : c.grid)).attr('stroke-width', 1.2);
  rows.append('circle').attr('cx', (d) => xA(d.diff)).attr('r', 5)
    .attr('fill', (d) => (d.gene === 'DPP4' ? c.paper : c.ink)).attr('stroke', (d) => (d.gene === 'DPP4' ? c.tracer : c.ink)).attr('stroke-width', 2)
    .on('pointerenter', (e, d) => tip.show(`<b>${d.gene}</b> ${num(d.diff, 2, l)}<br>${d.sig ? l.ui.sig : l.ui.ns}`, xA(d.diff), yA(d.gene)!))
    .on('pointerleave', () => tip.hide());
  // B
  const ox = narrow ? 0 : colW + 40;
  const oy = narrow ? hA + 20 : 0;
  const gB = svg.append('g').attr('transform', `translate(${ox},${oy})`);
  panelTitle(gB as any, 0, 16, l.b, 'b');
  const labelW = Math.min(250, colW * 0.55);
  const xB = d3.scaleLinear().domain([0, 2.8]).range([labelW, colW - 10]);
  const yB = d3.scaleBand().domain(deg.pathways.map((p) => p.name)).range([40, hB - 30]).padding(0.28);
  gB.append('g').attr('transform', `translate(0,${hB - 30})`).call((g) => axisStyle(g.call(d3.axisBottom(xB).ticks(4))));
  const bars = gB.append('g').selectAll('g').data(deg.pathways).join('g').attr('transform', (d) => `translate(0,${yB(d.name)})`);
  bars.append('rect').attr('x', xB(0)).attr('height', yB.bandwidth()).attr('fill', c.tracer).attr('opacity', 0.85)
    .attr('width', (d) => xB(d.nes) - xB(0));
  bars.append('text').attr('x', labelW - 8).attr('y', yB.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').attr('class', 'lbl')
    .text((d) => { const n = tr(d.name, l); return n.length > 34 && labelW < 240 ? n.slice(0, 32) + '…' : n; }).append('title').text((d) => tr(d.name, l));
  bars.append('text').attr('x', (d) => xB(d.nes) - 6).attr('y', yB.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').attr('class', 'lbl-num on-dark').text((d) => num(d.nes, 2, l));
  provenance(el, l, 'approx');
}

/* ---------- DPP4+ cells by compartment ---------- */
function cellChart(el: HTMLElement, l: L) {
  const c = C();
  const h = cells.data.length * 34 + 90;
  const { svg, w } = frame(el, h);
  svg.attr('aria-label', `${l.a}. ${cells.data.map((d) => `${d.cell}: control ${d.control}, SSc ${d.ssc}`).join('; ')}`);
  const tip = tooltip(el);
  const x = d3.scaleLinear().domain([0, 16]).range([110, w - 20]);
  const y = d3.scaleBand().domain(cells.data.map((d) => d.cell)).range([30, h - 50]).padding(0.4);
  svg.append('g').attr('transform', `translate(0,${h - 50})`).call((g) => axisStyle(g.call(d3.axisBottom(x).ticks(8).tickFormat((d) => `${d}%`))));
  svg.append('text').attr('x', x(8)).attr('y', h - 10).attr('text-anchor', 'middle').attr('class', 'axis-title').text(l.a);
  // legend
  const lg = svg.append('g').attr('transform', `translate(${w - 210},10)`);
  [['Control', c.hema, false], ['SSc', c.tracer, true]].forEach(([t, col, f], i) => {
    lg.append('circle').attr('cx', i * 100).attr('cy', 0).attr('r', 5).attr('fill', f ? (col as string) : c.paper).attr('stroke', col as string).attr('stroke-width', 2);
    lg.append('text').attr('x', i * 100 + 10).attr('dy', '0.35em').attr('class', 'lbl').text(tr(t as string, l));
  });
  const row = svg.append('g').selectAll('g').data(cells.data).join('g').attr('transform', (d) => `translate(0,${y(d.cell)! + y.bandwidth() / 2})`);
  row.append('text').attr('x', 100).attr('text-anchor', 'end').attr('dy', '0.35em').attr('class', (d) => (d.cell === 'Fibroblast' ? 'lbl-strong' : 'lbl')).text((d) => tr(d.cell, l));
  row.append('line').attr('x1', (d) => x(d.control)).attr('x2', (d) => x(d.ssc)).attr('stroke', c.ink3).attr('stroke-width', 2);
  row.append('circle').attr('cx', (d) => x(d.control)).attr('r', 6).attr('fill', c.paper).attr('stroke', c.hema).attr('stroke-width', 2);
  row.append('circle').attr('cx', (d) => x(d.ssc)).attr('r', 6).attr('fill', c.tracer).attr('stroke', c.tracer)
    .on('pointerenter', (_, d) => tip.show(`<b>${tr(d.cell, l)}</b><br>${tr('Control', l)} ${num(d.control, 1, l)}% · ${tr('SSc', l)} ${num(d.ssc, 1, l)}%`, x(d.ssc), y(d.cell)!))
    .on('pointerleave', () => tip.hide());
  provenance(el, l, 'approx');
}

/* ---------- fibroblast states beta/q ---------- */
function statesChart(el: HTMLElement, l: L) {
  const c = C();
  const narrow = el.clientWidth < 760;
  const hA = states.sscEffect.length * 40 + 70;
  const hB = states.dpp4Association.length * 40 + 70;
  const { svg, w } = frame(el, narrow ? hA + hB + 20 : Math.max(hA, hB));
  const colW = narrow ? w : (w - 40) / 2;
  const panel = (g: any, data: any[], title: string, letter: string, dom: [number, number], h: number) => {
    panelTitle(g, 0, 16, title, letter);
    const lw = Math.min(170, colW * 0.4);
    const x = d3.scaleLinear().domain(dom).range([lw, colW - 118]);
    const y = d3.scaleBand().domain(data.map((d) => d.state)).range([36, h - 30]).padding(0.3);
    g.append('g').attr('transform', `translate(0,${h - 30})`).call((gg: any) => axisStyle(gg.call(d3.axisBottom(x).ticks(5))));
    g.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', 32).attr('y2', h - 30).attr('stroke', c.ink3).attr('stroke-dasharray', '2 3');
    const r = g.append('g').selectAll('g').data(data).join('g').attr('transform', (d: any) => `translate(0,${y(d.state)})`);
    r.append('text').attr('x', lw - 8).attr('y', y.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').attr('class', 'lbl').text((d: any) => tr(d.state, l));
    r.append('rect').attr('x', (d: any) => x(Math.min(0, d.beta))).attr('width', (d: any) => Math.abs(x(d.beta) - x(0))).attr('height', y.bandwidth())
      .attr('fill', (d: any) => (d.sig === 'up' ? c.tracer : d.sig === 'down' ? c.hema : c.grid));
    r.append('text').attr('class', 'lbl-num').attr('y', y.bandwidth() / 2).attr('dy', '0.35em')
      .attr('x', (d: any) => (d.beta >= 0 ? x(d.beta) + 6 : x(0) + 6)).attr('text-anchor', 'start')
      .text((d: any) => `β ${num(d.beta, 2, l)} · q ${d.q.replace('<', '< ').replace('.', pt(l) ? ',' : '.')}`);
  };
  panel(svg.append('g'), states.sscEffect, l.a, 'a', [-1.6, 1.2], hA);
  panel(svg.append('g').attr('transform', `translate(${narrow ? 0 : colW + 40},${narrow ? hA + 20 : 0})`), states.dpp4Association, l.b, 'b', [-0.45, 0.9], hB);
  const pr = document.createElement('p'); pr.className = 'prov prov-exact';
  pr.textContent = pt(l) ? 'β e q transcritos dos rótulos impressos na figura original.' : 'β and q transcribed from the labels printed on the original figure.';
  el.appendChild(pr);
}

/* ---------- PAGA graph ---------- */
function pagaChart(el: HTMLElement, l: L) {
  const c = C();
  el.innerHTML = '';
  const controls = document.createElement('div');
  controls.className = 'chips';
  const plot = document.createElement('div');
  el.append(controls, plot);
  let active: string | null = 'dpp4';
  const btns = paga.branches.map((b) => {
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'chip';
    btn.textContent = `${b.path.join(' → ')}  ${b.label[l.lang as 'en' | 'pt']}`;
    btn.setAttribute('aria-pressed', String(active === b.id));
    btn.addEventListener('click', () => { active = active === b.id ? null : b.id; btns.forEach((x, i) => x.setAttribute('aria-pressed', String(paga.branches[i].id === active))); draw(); });
    controls.appendChild(btn);
    return btn;
  });
  const hint = document.createElement('span'); hint.className = 'hint'; hint.textContent = l.hint; controls.appendChild(hint);
  const stateName: Record<string, Record<string, string>> = {
    en: { progenitor: 'Progenitor', activated: 'Activated', ecm: 'ECM', myofibroblast: 'Myofibroblast' },
    pt: { progenitor: 'Progenitor', activated: 'Ativado', ecm: 'MEC', myofibroblast: 'Miofibroblasto' },
  };
  const draw = () => {
    const { svg, w } = frame(plot, Math.min(520, Math.max(380, el.clientWidth * 0.6)));
    const h = +svg.attr('height');
    const tip = tooltip(plot);
    const x = d3.scaleLinear().domain([-3.8, 3.9]).range([30, w - 30]);
    const y = d3.scaleLinear().domain([10, 17.1]).range([h - 30, 30]);
    const col = d3.scaleDiverging(d3.interpolateRgbBasis([c.hema, c.paper, c.tracer])).domain([-0.2, 0, 0.2]);
    const path = paga.branches.find((b) => b.id === active)?.path ?? [];
    const onPath = (a: number, b: number) => path.some((n, i) => i < path.length - 1 && ((path[i] === a && path[i + 1] === b) || (path[i] === b && path[i + 1] === a)));
    const node = new Map(paga.nodes.map((n) => [n.id, n]));
    svg.attr('aria-label', `PAGA graph of 11 fibroblast states. ${paga.branches.map((b) => `${b.label[l.lang as 'en' | 'pt']}: ${b.path.join(', ')}`).join('. ')}`);
    svg.append('g').selectAll('line').data(paga.edges).join('line')
      .attr('x1', (d) => x(node.get(d[0])!.x)).attr('y1', (d) => y(node.get(d[0])!.y))
      .attr('x2', (d) => x(node.get(d[1])!.x)).attr('y2', (d) => y(node.get(d[1])!.y))
      .attr('stroke', (d) => (onPath(d[0], d[1]) ? (active === 'dpp4' ? c.tracer : c.ink) : c.grid))
      .attr('stroke-width', (d) => (onPath(d[0], d[1]) ? 4 : d[2] > 1 ? 2 : 0.8))
      .attr('opacity', (d) => (path.length && !onPath(d[0], d[1]) ? 0.45 : 1));
    const g = svg.append('g').selectAll('g').data(paga.nodes).join('g').attr('transform', (d) => `translate(${x(d.x)},${y(d.y)})`)
      .attr('tabindex', 0).attr('role', 'button')
      .attr('aria-label', (d) => `State ${d.id}: ${stateName[l.lang][d.state]}, SSc effect ${fmt(d.ssc)}${d.sig ? ', significant' : ''}`);
    g.append('circle').attr('r', (d) => 6 + d.size * 4).attr('fill', (d) => col(d.ssc))
      .attr('stroke', (d) => (path.includes(d.id) ? c.ink : c.ink3)).attr('stroke-width', (d) => (path.includes(d.id) ? 2.2 : 1));
    g.filter((d) => !!(d as any).root).append('circle').attr('r', (d) => 11 + d.size * 4).attr('fill', 'none').attr('stroke', c.ink).attr('stroke-dasharray', '2 2');
    g.append('text').attr('text-anchor', 'middle').attr('dy', '0.35em').attr('class', 'lbl-num').style('fill', (d) => (Math.abs(d.ssc) > 0.1 ? '#fff' : c.ink)).style('font-weight', 650).text((d) => `${d.id}${d.sig ? '*' : ''}`);
    const show = (d: any) => tip.show(`<b>${l.lang === 'pt' ? 'Estado' : 'State'} ${d.id}</b> · ${stateName[l.lang][d.state]}<br>SSc ${num(d.ssc, 2, l)}${d.sig ? ' *' : ''}`, x(d.x), y(d.y) - 10 - d.size * 4);
    g.on('pointerenter', (_, d) => show(d)).on('focus', (_, d) => show(d)).on('pointerleave blur', () => tip.hide());
    // colour legend
    const lg = svg.append('g').attr('transform', `translate(${w - 160},22)`);
    const grad = svg.append('defs').append('linearGradient').attr('id', 'paga-grad');
    [[0, c.hema], [0.5, c.paper], [1, c.tracer]].forEach(([o, cc]) => grad.append('stop').attr('offset', o as number).attr('stop-color', cc as string));
    lg.append('rect').attr('width', 140).attr('height', 8).attr('fill', 'url(#paga-grad)').attr('stroke', c.rule);
    lg.append('text').attr('y', -6).attr('class', 'lbl-small').text(l.lang === 'pt' ? 'Efeito ES na ocupação' : 'SSc effect on occupancy');
    lg.append('text').attr('y', 20).attr('class', 'lbl-small').text('−0,2'.replace(',', pt(l) ? ',' : '.'));
    lg.append('text').attr('x', 140).attr('y', 20).attr('text-anchor', 'end').attr('class', 'lbl-small').text(pt(l) ? '+0,2' : '+0.2');
  };
  draw();
  provenance(el, l, 'mixed');
  return draw;
}

/* ---------- PROGENy / CollecTRI ---------- */
function signalingChart(el: HTMLElement, l: L) {
  const c = C();
  const narrow = el.clientWidth < 760;
  const hA = progeny.sscVsControl.length * 64 + 80;
  const hB = progeny.dpp4PosVsNeg.length * 52 + 80;
  const { svg, w } = frame(el, narrow ? hA + hB + 20 : Math.max(hA, hB));
  const colW = narrow ? w : (w - 40) / 2;
  const cohorts = [
    { k: 'GSE138669', col: c.hema, shape: d3.symbolCircle },
    { k: 'GSE249279', col: c.ink, shape: d3.symbolSquare },
  ] as const;
  const legend = (g: any, y0: number) => cohorts.forEach((co, i) => {
    g.append('path').attr('d', d3.symbol(co.shape, 60)()).attr('transform', `translate(${i * 120 + 6},${y0})`).attr('fill', co.col);
    g.append('text').attr('x', i * 120 + 16).attr('y', y0).attr('dy', '0.35em').attr('class', 'lbl-num').text(co.k);
  });
  // A forest
  const gA = svg.append('g');
  panelTitle(gA as any, 0, 16, l.a, 'a');
  legend(gA, 36);
  const xA = d3.scaleLinear().domain([-0.1, 2.4]).range([70, colW - 10]);
  const yA = d3.scaleBand().domain(progeny.sscVsControl.map((d) => d.target)).range([56, hA - 30]).padding(0.25);
  gA.append('g').attr('transform', `translate(0,${hA - 30})`).call((g) => axisStyle(g.call(d3.axisBottom(xA).ticks(5))));
  gA.append('line').attr('x1', xA(0)).attr('x2', xA(0)).attr('y1', 52).attr('y2', hA - 30).attr('stroke', c.ink3).attr('stroke-dasharray', '2 3');
  const rA = gA.append('g').selectAll('g').data(progeny.sscVsControl).join('g').attr('transform', (d) => `translate(0,${yA(d.target)})`);
  rA.append('text').attr('x', 60).attr('y', yA.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').attr('class', 'lbl-strong').text((d) => d.target);
  cohorts.forEach((co, i) => {
    const yy = yA.bandwidth() * (i ? 0.72 : 0.28);
    rA.append('line').attr('x1', (d: any) => xA(d[co.k].lo)).attr('x2', (d: any) => xA(d[co.k].hi)).attr('y1', yy).attr('y2', yy).attr('stroke', co.col).attr('stroke-width', 1.6);
    rA.append('path').attr('d', d3.symbol(co.shape, 70)()).attr('transform', (d: any) => `translate(${xA(d[co.k].est)},${yy})`)
      .attr('fill', (d: any) => (d[co.k].sig ? co.col : c.paper)).attr('stroke', co.col).attr('stroke-width', 1.6);
  });
  // B dumbbell
  const gB = svg.append('g').attr('transform', `translate(${narrow ? 0 : colW + 40},${narrow ? hA + 20 : 0})`);
  panelTitle(gB as any, 0, 16, l.b, 'b');
  legend(gB, 36);
  const xB = d3.scaleLinear().domain([-1.9, 1.0]).range([80, colW - 10]);
  const yB = d3.scaleBand().domain(progeny.dpp4PosVsNeg.map((d) => d.pathway)).range([66, hB - 30]).padding(0.3);
  gB.append('g').attr('transform', `translate(0,${hB - 30})`).call((g) => axisStyle(g.call(d3.axisBottom(xB).ticks(6))));
  gB.append('line').attr('x1', xB(0)).attr('x2', xB(0)).attr('y1', 52).attr('y2', hB - 30).attr('stroke', c.ink3).attr('stroke-dasharray', '2 3');
  const rB = gB.append('g').selectAll('g').data(progeny.dpp4PosVsNeg).join('g').attr('transform', (d) => `translate(0,${yB(d.pathway)! + yB.bandwidth() / 2})`);
  rB.append('text').attr('x', 70).attr('dy', '0.35em').attr('text-anchor', 'end').attr('class', 'lbl-strong').text((d) => d.pathway);
  rB.append('line').attr('x1', (d) => xB(d.GSE138669)).attr('x2', (d) => xB(d.GSE249279)).attr('stroke', c.grid).attr('stroke-width', 2);
  cohorts.forEach((co) => rB.append('path').attr('d', d3.symbol(co.shape, 80)()).attr('transform', (d: any) => `translate(${xB(d[co.k])},0)`).attr('fill', co.col));
  gB.append('text').attr('x', xB(-1.85)).attr('y', 54).attr('class', 'lbl-small').text(pt(l) ? '← menor em DPP4⁺' : '← lower in DPP4⁺');
  gB.append('text').attr('x', colW - 10).attr('y', 54).attr('text-anchor', 'end').attr('class', 'lbl-small').text(pt(l) ? 'maior em DPP4⁺ →' : 'higher in DPP4⁺ →');
  provenance(el, l, 'approx', pt(l) ? 'Marcadores cheios: q < 0,05.' : 'Filled markers: q < 0.05.');
}

/* ---------- network proximity ---------- */
function networkChart(el: HTMLElement, l: L) {
  const c = C();
  el.innerHTML = '';
  const plot = document.createElement('div');
  const chips = document.createElement('div'); chips.className = 'chips';
  el.append(chips, plot);
  let sel = 'M4';
  const btns = network.data.map((m) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'chip';
    b.textContent = m.label[l.lang as 'en' | 'pt'];
    b.addEventListener('click', () => { sel = m.id; btns.forEach((x, i) => x.setAttribute('aria-pressed', String(network.data[i].id === sel))); draw(); });
    b.setAttribute('aria-pressed', String(m.id === sel));
    chips.appendChild(b); return b;
  });
  const draw = () => {
    const { svg, w } = frame(plot, 250);
    const x = d3.scaleLinear().domain([-5.2, 3.2]).range([20, w - 20]);
    const y = d3.scaleLinear().domain([0, 0.42]).range([200, 40]);
    const pts = d3.range(-4.2, 3.21, 0.05).map((z) => [z, Math.exp(-z * z / 2) / Math.sqrt(2 * Math.PI)] as [number, number]);
    svg.append('path').datum(pts).attr('d', d3.area<[number, number]>().x((d) => x(d[0])).y0(200).y1((d) => y(d[1])).curve(d3.curveBasis)).attr('fill', c.grid).attr('opacity', 0.45);
    svg.append('text').attr('x', x(0.9)).attr('y', y(0.33)).attr('class', 'lbl-small').text(l.null);
    svg.append('g').attr('transform', 'translate(0,200)').call((g) => axisStyle(g.call(d3.axisBottom(x).ticks(8))));
    svg.append('text').attr('x', x(-1)).attr('y', 242).attr('text-anchor', 'middle').attr('class', 'axis-title').text(l.a);
    const m = svg.append('g').selectAll('g').data(network.data).join('g').attr('transform', (d) => `translate(${x(d.z)},0)`);
    m.append('line').attr('y1', 200).attr('y2', (d) => (d.id === sel ? 46 : 120)).attr('stroke', (d) => (d.q < 0.05 ? c.tracer : c.ink3)).attr('stroke-width', (d) => (d.id === sel ? 2.5 : 1.2));
    m.append('circle').attr('cy', (d) => (d.id === sel ? 46 : 120)).attr('r', (d) => (d.id === sel ? 6 : 4)).attr('fill', (d) => (d.q < 0.05 ? c.tracer : c.paper)).attr('stroke', (d) => (d.q < 0.05 ? c.tracer : c.ink3)).attr('stroke-width', 1.5);
    const s = network.data.find((d) => d.id === sel)!;
    const left = x(s.z) < w / 2;
    svg.append('text').attr('x', x(s.z) + (left ? 12 : -12)).attr('y', 30).attr('text-anchor', left ? 'start' : 'end').attr('class', 'lbl-strong').text(s.label[l.lang as 'en' | 'pt']);
    svg.append('text').attr('x', x(s.z) + (left ? 12 : -12)).attr('y', 50).attr('text-anchor', left ? 'start' : 'end').attr('class', 'lbl-num')
      .text(`z = ${num(s.z, 2, l)} · q = ${num(s.q, 3, l)} ${s.q < 0.05 ? '' : `(${l.ui.ns})`}`);
    svg.attr('aria-label', network.data.map((d) => `${d.label[l.lang as 'en' | 'pt']}: z ${fmt(d.z)}, q ${d.q}`).join('; '));
  };
  draw();
  const paths = document.createElement('div'); paths.className = 'paths';
  paths.innerHTML = `<p class="lbl-small">${l.paths}</p>` + network.paths.items.map((p) => `<p class="mono">${p.path.map((g, i) => (i === p.path.length - 1 ? `<b>${g}</b>` : g)).join('<span class="arr"> — </span>')}</p>`).join('');
  el.appendChild(paths);
  provenance(el, l, 'exact', pt(l) ? 'Caminhos do STRING são ilustrativos; o teste formal é por módulo.' : 'STRING paths are illustrative; the formal test is module-level.');
  return draw;
}

/* ---------- mRSS ---------- */
function mrssChart(el: HTMLElement, l: L) {
  const c = C();
  const h = mrss.data.length * 44 + 70;
  const { svg, w } = frame(el, h);
  const lw = Math.min(200, w * 0.36);
  const x = d3.scaleLinear().domain([-0.4, 0.8]).range([lw, w - 120]);
  const y = d3.scaleBand().domain(mrss.data.map((d) => d.program.en)).range([20, h - 40]).padding(0.3);
  svg.append('g').attr('transform', `translate(0,${h - 40})`).call((g) => axisStyle(g.call(d3.axisBottom(x).ticks(6))));
  svg.append('text').attr('x', x(0.2)).attr('y', h - 6).attr('text-anchor', 'middle').attr('class', 'axis-title').text(l.a);
  svg.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', 14).attr('y2', h - 40).attr('stroke', c.ink3);
  const st: Record<string, string> = { supported: l.ui.supported, directional: l.ui.directional, not: l.ui.notSupported };
  const r = svg.append('g').selectAll('g').data(mrss.data).join('g').attr('transform', (d) => `translate(0,${y(d.program.en)})`);
  r.append('text').attr('x', lw - 8).attr('y', y.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').attr('class', (d) => (d.program.en === 'DPP4' ? 'lbl-gene hot' : 'lbl')).text((d) => d.program[l.lang as 'en' | 'pt']);
  r.append('rect').attr('x', (d) => x(Math.min(0, d.rho))).attr('height', y.bandwidth())
    .attr('width', (d) => Math.abs(x(d.rho) - x(0)))
    .attr('fill', (d) => (d.status === 'supported' ? c.ink : d.status === 'directional' ? c.grid : c.paper))
    .attr('stroke', (d) => (d.status === 'not' ? c.tracer : 'none')).attr('stroke-width', 1.5);
  r.append('text').attr('x', (d) => (d.rho >= 0 ? x(d.rho) + 6 : x(0) + 6)).attr('y', y.bandwidth() / 2).attr('dy', '0.35em').attr('class', 'lbl-num')
    .text((d) => `ρ ${num(d.rho, 2, l)} · ${st[d.status]}`);
  svg.attr('aria-label', mrss.data.map((d) => `${d.program.en} rho ${d.rho.toFixed(2)}, ${d.status}`).join('; '));
  provenance(el, l, 'exact');
}

/* ---------- PK explorer ---------- */
export function simulate(kpu: number, ic50: number) {
  const { ka_per_h: ka, t_half_h: th, kt_skin_per_h: kt, free_plasma_peak_nM: peak } = pk.params;
  const ke = Math.LN2 / th, dt = 0.01, steps = 1200, doses = 12;
  // unit-dose run to find the scale that gives the calibrated plasma peak
  const run = (scale: number) => {
    let G = 0, Cc = 0, Cs = 0;
    const out: { t: number; p: number; s: number }[] = [];
    for (let d = 0; d < doses; d++) {
      G += 1;
      for (let i = 0; i < steps; i++) {
        const dG = -ka * G, dC = ka * G - ke * Cc, dS = kt * (kpu * Cc * scale - Cs);
        G += dG * dt; Cc += dC * dt; Cs += dS * dt;
        if (d === doses - 1 && i % 5 === 0) out.push({ t: i * dt, p: Cc * scale, s: Cs });
      }
    }
    return out;
  };
  const unit = run(1);
  const scale = peak / d3.max(unit, (d) => d.p)!;
  const res = run(scale);
  return res.map((d) => ({ ...d, inh: d.s / (d.s + ic50) }));
}

function pkChart(el: HTMLElement, l: L) {
  const c = C();
  el.innerHTML = '';
  const ctr = document.createElement('div'); ctr.className = 'pk-controls';
  const plot = document.createElement('div');
  const side = document.createElement('div'); side.className = 'pk-side';
  const body = document.createElement('div'); body.className = 'pk-body';
  body.append(plot, side);
  el.append(ctr, body);
  const grid = pk.kpuGrid;
  const st = { kpu: 0.1, ic50: pk.ic50.central_nM, target: 0.8 };
  ctr.innerHTML = `
    <label class="range-row"><span>${l.kpu}</span><input data-k="kpu" type="range" min="0" max="${grid.length - 1}" step="1" value="${grid.indexOf(0.1)}"><output data-o="kpu"></output></label>
    <label class="range-row"><span>${l.ic50}</span><input data-k="ic50" type="range" min="0" max="100" step="1"><output data-o="ic50"></output></label>
    <fieldset class="seg"><legend>${l.target}</legend>
      <label><input type="radio" name="pk-target" value="0.8" checked> ≥ 80%</label>
      <label><input type="radio" name="pk-target" value="0.92"> ≥ 92%</label>
    </fieldset>
    <button type="button" class="btn small" data-reset>${l.reset}</button>`;
  const ic = ctr.querySelector<HTMLInputElement>('[data-k=ic50]')!;
  const icFrom = (p: number) => 10 ** (Math.log10(1) + (p / 100) * (Math.log10(50) - Math.log10(1)));
  const icTo = (v: number) => Math.round(((Math.log10(v) - 0) / Math.log10(50)) * 100);
  ic.value = String(icTo(st.ic50));
  ctr.addEventListener('input', (e) => {
    const t = e.target as HTMLInputElement;
    if (t.dataset.k === 'kpu') st.kpu = grid[+t.value];
    if (t.dataset.k === 'ic50') st.ic50 = icFrom(+t.value);
    if (t.name === 'pk-target') st.target = +t.value;
    draw();
  });
  ctr.querySelector('[data-reset]')!.addEventListener('click', () => {
    st.kpu = 0.1; st.ic50 = pk.ic50.central_nM; st.target = 0.8;
    (ctr.querySelector('[data-k=kpu]') as HTMLInputElement).value = String(grid.indexOf(0.1));
    ic.value = String(icTo(st.ic50));
    (ctr.querySelector('input[name=pk-target][value="0.8"]') as HTMLInputElement).checked = true;
    draw();
  });

  const draw = () => {
    const data = simulate(st.kpu, st.ic50);
    const cover = data.filter((d) => d.inh >= st.target).length / data.length;
    const thr = (st.ic50 * st.target) / (1 - st.target);
    (ctr.querySelector('[data-o=kpu]') as HTMLElement).textContent = num(st.kpu, st.kpu < 0.1 ? 2 : 1, l);
    (ctr.querySelector('[data-o=ic50]') as HTMLElement).textContent = `${num(st.ic50, 1, l)} nM`;
    const { svg, w } = frame(plot, 300, 280);
    const x = d3.scaleLinear().domain([0, 12]).range([52, w - 16]);
    const y = d3.scaleLog().domain([1, 1000]).range([250, 16]).clamp(true);
    svg.append('g').attr('transform', 'translate(0,250)').call((g) => axisStyle(g.call(d3.axisBottom(x).ticks(6))));
    svg.append('g').attr('transform', 'translate(52,0)').call((g) => axisStyle(g.call(d3.axisLeft(y).ticks(3, '~s'))));
    svg.append('text').attr('x', (w + 52) / 2).attr('y', 288).attr('text-anchor', 'middle').attr('class', 'axis-title').text(l.time);
    svg.append('text').attr('transform', 'rotate(-90)').attr('x', -133).attr('y', 12).attr('text-anchor', 'middle').attr('class', 'axis-title').text(l.conc);
    // above-target band
    const above = data.filter((d) => d.s >= thr);
    svg.append('g').selectAll('rect').data(above).join('rect').attr('x', (d) => x(d.t)).attr('width', Math.max(1, x(0.05) - x(0) + 0.5)).attr('y', 16).attr('height', 234).attr('fill', c.wash).attr('opacity', 0.55);
    svg.append('line').attr('x1', 52).attr('x2', w - 16).attr('y1', y(thr)).attr('y2', y(thr)).attr('stroke', c.tracerInk).attr('stroke-dasharray', '4 3');
    svg.append('text').attr('x', w - 18).attr('y', y(thr) - 6).attr('text-anchor', 'end').attr('class', 'lbl-small hot').text(`${Math.round(st.target * 100)}% · ${num(thr, 0, l)} nM`);
    const line = (k: 'p' | 's') => d3.line<any>().x((d) => x(d.t)).y((d) => y(Math.max(1, d[k])));
    svg.append('path').datum(data).attr('d', line('p')).attr('fill', 'none').attr('stroke', c.ink).attr('stroke-width', 2);
    svg.append('path').datum(data).attr('d', line('s')).attr('fill', 'none').attr('stroke', c.tracer).attr('stroke-width', 2.5);
    const lastP = data[Math.floor(data.length * 0.12)];
    svg.append('text').attr('x', x(lastP.t) + 8).attr('y', y(lastP.p)).attr('class', 'lbl-strong').text(l.plasma);
    const pkS = data.reduce((a, b) => (b.s > a.s ? b : a));
    svg.append('text').attr('x', x(pkS.t) + 6).attr('y', y(Math.max(1, pkS.s)) - 8).attr('class', 'lbl-strong hot').text(`${l.skin} · Kpu ${num(st.kpu, st.kpu < 0.1 ? 2 : 1, l)}`);
    svg.attr('aria-label', `${l.skin} Kpu ${st.kpu}: ${Math.round(cover * 100)}% ${l.cover}`);
    const inh = data.map((d) => d.inh);
    side.innerHTML = `
      <p class="big-num">${Math.round(cover * 100)}<small>%</small></p>
      <p class="lbl">${l.cover}</p>
      <p class="lbl-num">${l.inh}: ${Math.round(d3.min(inh)! * 100)}–${Math.round(d3.max(inh)! * 100)}%</p>
      <table class="kpu-table"><caption>${l.tableTitle}</caption>
        <thead><tr><th scope="col">${l.target}</th><th scope="col">≥ 50%</th><th scope="col">≥ 80%</th></tr></thead>
        <tbody>${pk.thresholdTable.rows.map((r) => `<tr><th scope="row">≥ ${r.inhibition}%</th>${[r.coverage50, r.coverage80].map((k) => `<td class="${st.kpu >= k ? 'met' : ''}">${num(k, 2, l)}</td>`).join('')}</tr>`).join('')}</tbody>
        <tfoot><tr><td colspan="3">${l.tableCov}</td></tr></tfoot>
      </table>`;
  };
  draw();
  provenance(el, l, 'model', pt(l) ? 'A tabela é o resultado exato do estudo; o modelo a reproduz na grade de Kpu.' : 'The table is the study’s exact result; this model reproduces it on the Kpu grid.');
  return draw;
}

/* ---------- evidence landscape ---------- */
function landscapeChart(el: HTMLElement, l: L) {
  el.innerHTML = '';
  const roles = ['supports', 'refines', 'nosupport', 'experiment'] as const;
  const box = document.createElement('div'); box.className = 'landscape';
  roles.forEach((r, i) => {
    const col = document.createElement('div'); col.className = `ls-col ls-${r}`;
    col.innerHTML = `<h4>${l.cols[i]}</h4>`;
    const ul = document.createElement('ul');
    (landscape.items as any[]).filter((it) => it.role === r).forEach((it) => {
      const li = document.createElement('li');
      const title = l.lang === 'pt' && it.pt ? it.pt.title : it.title;
      const finding = l.lang === 'pt' && it.pt ? it.pt.finding : it.finding;
      li.innerHTML = `<a href="#${it.anchor}"><span class="ls-dot" aria-hidden="true"></span><span class="ls-title">${title}</span><span class="ls-finding">${finding}</span></a>`;
      ul.appendChild(li);
    });
    col.appendChild(ul);
    box.appendChild(col);
  });
  el.appendChild(box);
  provenance(el, l, 'exact');
}

const registry: Record<string, (el: HTMLElement, l: L) => void | (() => void)> = {
  ruler, deg: degChart, celltypes: cellChart, states: statesChart, paga: pagaChart, signaling: signalingChart,
  network: networkChart, mrss: mrssChart, pk: pkChart, landscape: landscapeChart,
};

export function mountAll() {
  document.querySelectorAll<HTMLElement>('[data-chart]').forEach((el) => {
    const fn = registry[el.dataset.chart!];
    if (!fn) return;
    const l = JSON.parse(el.dataset.labels || '{}');
    const render = () => { try { fn(el, l); } catch (e) { console.error(el.dataset.chart, e); } };
    render();
    let w = el.clientWidth, raf = 0;
    new ResizeObserver(() => {
      if (Math.abs(el.clientWidth - w) < 24) return;
      w = el.clientWidth;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(render);
    }).observe(el);
  });
}

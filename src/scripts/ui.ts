// Small page behaviours: mechanism chain, citation popovers, experiment
// decision logic and the "develop" reveal for plates.

export function mountUi() {
  mountChain();
  mountCitations();
  mountExperiment();
  mountDevelop();
}

function mountChain() {
  const root = document.querySelector<HTMLElement>('[data-chain]');
  if (!root) return;
  const nodes = [...root.querySelectorAll<HTMLButtonElement>('.chain-node')];
  const panels = [...root.querySelectorAll<HTMLElement>('.chain-panel')];
  const select = (i: number) => {
    nodes.forEach((n, j) => n.setAttribute('aria-pressed', String(i === j)));
    panels.forEach((p, j) => (p.hidden = i !== j));
  };
  nodes.forEach((n, i) => {
    n.addEventListener('click', () => select(i));
    n.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); nodes[Math.min(i + 1, nodes.length - 1)].focus(); select(Math.min(i + 1, nodes.length - 1)); }
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); nodes[Math.max(i - 1, 0)].focus(); select(Math.max(i - 1, 0)); }
    });
  });
}

function mountCitations() {
  const pop = document.querySelector<HTMLElement>('[data-cite-pop]');
  const dataEl = document.getElementById('refdata');
  if (!pop || !dataEl) return;
  const data: Record<string, { n: number; html: string; url?: string }> = JSON.parse(dataEl.textContent || '{}');
  let openFor: HTMLElement | null = null;

  const close = () => { pop.hidden = true; openFor?.setAttribute('aria-expanded', 'false'); openFor = null; };
  const open = (a: HTMLAnchorElement) => {
    const keys = (a.dataset.refs || '').split(' ').filter(Boolean);
    pop.innerHTML = keys.map((k) => {
      const r = data[k];
      if (!r) return '';
      const link = r.url ? ` <a href="${r.url}">${r.url.includes('doi.org') ? 'DOI' : 'Link'}</a>` : '';
      return `<p><b>${r.n}</b> ${r.html}${link}</p>`;
    }).join('') + `<p class="pop-all"><a href="${a.getAttribute('href')}">${document.documentElement.lang.startsWith('pt') ? 'Referências' : 'References'}</a></p>`;
    pop.hidden = false;
    const r = a.getBoundingClientRect();
    const w = Math.min(380, window.innerWidth - 32);
    pop.style.width = `${w}px`;
    const left = Math.max(16, Math.min(r.left + window.scrollX - w / 2, window.scrollX + window.innerWidth - w - 16));
    pop.style.left = `${left}px`;
    pop.style.top = `${r.bottom + window.scrollY + 8}px`;
    a.setAttribute('aria-expanded', 'true');
    openFor = a;
  };

  document.querySelectorAll<HTMLAnchorElement>('sup.cite a').forEach((a) => {
    a.setAttribute('aria-haspopup', 'dialog');
    a.setAttribute('aria-expanded', 'false');
    a.addEventListener('click', (e) => {
      e.preventDefault();
      if (openFor === a) close(); else open(a);
    });
  });
  document.addEventListener('click', (e) => {
    if (openFor && !pop.contains(e.target as Node) && !(e.target as HTMLElement).closest('sup.cite')) close();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && openFor) { const a = openFor; close(); a.focus(); }
  });
}

function mountExperiment() {
  const root = document.querySelector<HTMLElement>('[data-experiment]');
  if (!root) return;
  const out = root.querySelector<HTMLElement>('.outcome')!;
  const outcomes: { id: string; drug: boolean; kd: boolean; title: string; text: string }[] = JSON.parse(out.dataset.outcomes || '[]');
  const update = () => {
    const kd = (root.querySelector<HTMLInputElement>('input[name=kd]:checked')?.value ?? '1') === '1';
    const drug = (root.querySelector<HTMLInputElement>('input[name=drug]:checked')?.value ?? '1') === '1';
    const o = outcomes.find((x) => x.kd === kd && x.drug === drug)!;
    out.dataset.state = o.id;
    out.querySelector('.outcome-title')!.textContent = o.title;
    out.querySelector('.outcome-text')!.textContent = o.text;
  };
  root.addEventListener('change', update);
  update();
}

function mountDevelop() {
  const els = document.querySelectorAll<HTMLElement>('[data-develop]');
  if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('developed')); return; }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add('developed'); io.unobserve(e.target); }
  }, { rootMargin: '0px 0px -12% 0px' });
  els.forEach((e) => io.observe(e));
}

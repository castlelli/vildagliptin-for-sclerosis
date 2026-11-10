// Schematic fibroblast field for the first viewport. Illustrates the
// hypothesis (DPP4+ fibroblasts lay down matrix; inhibiting DPP-4 slows it).
// It is not data and is labelled as such on the page.

interface Cell {
  x: number; y: number; a: number; len: number; w: number;
  dpp4: boolean; phase: number; vx: number; vy: number;
}

const css = (n: string) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

export function mountField(root: HTMLElement) {
  const canvas = root.querySelector('canvas')!;
  const slider = root.querySelector<HTMLInputElement>('input[type=range]')!;
  const rateOut = root.querySelector<HTMLElement>('[data-rate]')!;
  const inhOut = root.querySelector<HTMLElement>('[data-inh]')!;
  const tip = root.querySelector<HTMLElement>('[data-tip]')!;
  const ctx = canvas.getContext('2d')!;
  const layer = document.createElement('canvas');
  const lctx = layer.getContext('2d')!;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const ink = css('--ink'), tracer = css('--tracer'), paper = css('--paper');
  let W = 0, H = 0, dpr = 1;
  let cells: Cell[] = [];
  let inhibition = Number(slider.value) / 100;
  let deposited = 0;
  let running = false;
  let raf = 0;
  let hover: Cell | null = null;

  // a slow flow field gives the tissue a grain, like the reticular dermis
  const angleAt = (x: number, y: number) =>
    Math.sin(x * 0.004 + Math.cos(y * 0.006)) * 0.9 + Math.cos(y * 0.003) * 0.4 - 0.25;

  function seed() {
    const n = Math.round((W * H) / 4200);
    let s = 7;
    const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
    cells = Array.from({ length: n }, () => {
      const x = rnd() * W, y = rnd() * H;
      const dpp4 = rnd() < 0.3;
      return {
        x, y, a: angleAt(x, y) + (rnd() - 0.5) * 0.5,
        len: (dpp4 ? 26 : 20) + rnd() * 16, w: 3.2 + rnd() * 2.2,
        dpp4, phase: rnd() * Math.PI * 2, vx: 0, vy: 0,
      };
    });
  }

  function resize() {
    const r = canvas.getBoundingClientRect();
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = Math.max(1, r.width); H = Math.max(1, r.height);
    for (const c of [canvas, layer]) { c.width = W * dpr; c.height = H * dpr; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    lctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    lctx.clearRect(0, 0, W, H);
    deposited = 0;
    seed();
    // pre-develop some matrix so the first frame already shows fibrosis
    for (let i = 0; i < (reduce ? 260 : 140); i++) deposit(1 - inhibition, true);
    draw(0);
  }

  function deposit(activity: number, warm = false) {
    lctx.lineCap = 'round';
    for (const c of cells) {
      if (!c.dpp4) continue;
      if (Math.random() > 0.11 * activity * (warm ? 1.6 : 1)) continue;
      const along = (Math.random() - 0.5) * c.len * 2.4;
      const off = (Math.random() - 0.5) * 18;
      const ca = Math.cos(c.a), sa = Math.sin(c.a);
      const x = c.x + ca * along - sa * off, y = c.y + sa * along + ca * off;
      const L = 14 + Math.random() * 30;
      const a = angleAt(x, y) + (Math.random() - 0.5) * 0.3;
      lctx.strokeStyle = tracer;
      lctx.globalAlpha = 0.2 + Math.random() * 0.2;
      lctx.lineWidth = 0.7 + Math.random() * 1.1;
      lctx.beginPath();
      lctx.moveTo(x - Math.cos(a) * L, y - Math.sin(a) * L);
      lctx.quadraticCurveTo(x + Math.sin(a) * 4, y - Math.cos(a) * 4, x + Math.cos(a) * L, y + Math.sin(a) * L);
      lctx.stroke();
      deposited++;
    }
    lctx.globalAlpha = 1;
  }

  function spindle(c: Cell, t: number) {
    const act = c.dpp4 ? 1 - inhibition : 0;
    const breathe = 1 + Math.sin(t * 0.0012 + c.phase) * 0.04;
    ctx.save();
    ctx.translate(c.x, c.y);
    ctx.rotate(c.a);
    ctx.beginPath();
    const L = c.len * breathe, w = c.w;
    ctx.moveTo(-L, 0);
    ctx.bezierCurveTo(-L * 0.4, -w * 1.6, L * 0.4, -w * 1.6, L, 0);
    ctx.bezierCurveTo(L * 0.4, w * 1.6, -L * 0.4, w * 1.6, -L, 0);
    if (c.dpp4) {
      ctx.globalAlpha = 0.25 + act * 0.75;
      ctx.fillStyle = tracer;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.lineWidth = 0.8;
      ctx.strokeStyle = ink;
      ctx.stroke();
    } else {
      ctx.fillStyle = paper;
      ctx.fill();
      ctx.lineWidth = 0.9;
      ctx.strokeStyle = ink;
      ctx.globalAlpha = 0.55;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
    // nucleus
    ctx.beginPath();
    ctx.ellipse(0, 0, w * 1.1, w * 0.62, 0, 0, Math.PI * 2);
    ctx.fillStyle = ink;
    ctx.globalAlpha = c.dpp4 ? 0.9 : 0.5;
    ctx.fill();
    ctx.globalAlpha = 1;
    if (c === hover) {
      ctx.lineWidth = 1.2;
      ctx.strokeStyle = ink;
      ctx.beginPath();
      ctx.ellipse(0, 0, L + 7, w * 2.6 + 6, 0, 0, Math.PI * 2);
      ctx.setLineDash([3, 3]);
      ctx.stroke();
      ctx.setLineDash([]);
    }
    ctx.restore();
  }

  let last = 0, smoothRate = 1 - inhibition;
  function draw(t: number) {
    const activity = 1 - inhibition;
    if (!reduce) {
      deposit(activity);
      // remodelling: matrix turns over slowly; faster when deposition stops
      lctx.globalCompositeOperation = 'destination-out';
      lctx.fillStyle = `rgba(0,0,0,${0.0035 + inhibition * 0.006})`;
      lctx.fillRect(0, 0, W, H);
      lctx.globalCompositeOperation = 'source-over';
      for (const c of cells) {
        c.x += Math.cos(c.a) * Math.sin(t * 0.0004 + c.phase) * 0.05;
        c.y += Math.sin(c.a) * Math.sin(t * 0.0004 + c.phase) * 0.05;
      }
    }
    ctx.clearRect(0, 0, W, H);
    ctx.drawImage(layer, 0, 0, W, H);
    for (const c of cells) spindle(c, t);
    smoothRate += (activity - smoothRate) * 0.06;
    if (t - last > 120 || reduce) {
      rateOut.textContent = `${Math.round(smoothRate * 100)}%`;
      last = t;
    }
  }

  function loop(t: number) {
    draw(t);
    if (running) raf = requestAnimationFrame(loop);
  }

  slider.addEventListener('input', () => {
    inhibition = Number(slider.value) / 100;
    inhOut.textContent = `${slider.value}%`;
    slider.setAttribute('aria-valuetext', `${slider.value}% DPP-4 inhibition`);
    if (reduce) draw(performance.now());
  });

  canvas.addEventListener('pointermove', (e) => {
    const r = canvas.getBoundingClientRect();
    const px = e.clientX - r.left, py = e.clientY - r.top;
    let best: Cell | null = null, bd = 900;
    for (const c of cells) {
      const d = (c.x - px) ** 2 + (c.y - py) ** 2;
      if (d < bd) { bd = d; best = c; }
    }
    hover = best;
    if (best) {
      tip.hidden = false;
      tip.textContent = best.dpp4 ? tip.dataset.pos! : tip.dataset.neg!;
      tip.style.transform = `translate(${Math.min(best.x + 14, W - 180)}px, ${best.y - 34}px)`;
    } else tip.hidden = true;
    if (reduce) draw(performance.now());
  });
  canvas.addEventListener('pointerleave', () => { hover = null; tip.hidden = true; });

  new ResizeObserver(() => resize()).observe(canvas);
  new IntersectionObserver(([e]) => {
    if (reduce) return;
    if (e.isIntersecting && !running) { running = true; raf = requestAnimationFrame(loop); }
    else if (!e.isIntersecting) { running = false; cancelAnimationFrame(raf); }
  }).observe(root);
}

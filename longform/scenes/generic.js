// GENERIC scene kinds (15 Nov 2026) - data-driven, so the daily robot can make a new long video on ANY topic
// without writing new drawing code. Loaded after scenes.js; registers into KIND. One "beat" per voice line (cue).
// Kinds: hook2, story, stat, headline, dates, flow2, celebrate2 (+ compare / checklist / outro from scenes.js).

const COL = n => C[n] || n || C.teal;
const beatAt = (t, n) => { let k = 0; for (let i = 0; i < Math.min(n, SC.cues.length); i++) if (t >= cs(i) - .25) k = i; return k; };
function fitSize(s, size, maxw, fam = 'Inter', w = 800) { const x = tw(s, size, fam, w); return x > maxw ? size * maxw / x : size; }
function lines(s, size, maxw, fam = 'Inter', max = 3) { const L = wrap(String(s || ''), size, maxw, fam); return L.slice(0, max); }

// ---------- props by name ----------
function prop(p, x, y, t, s = 1) {
  if (!p) return '';
  const o = typeof p === 'string' ? {name: p} : p;
  const n = o.name, lab = o.label || '';
  let inner = '';
  if (n === 'doc') inner = doc(lab || 'PDF', COL(o.color || 'red'));
  else if (n === 'einvoice') inner = einv();
  else if (n === 'envelope') inner = envelope(1.3);
  else if (n === 'laptop') inner = laptop(0, 60, 1.3);
  else if (n === 'clock') inner = clock(0, 0, t, 1.6, 2);
  else if (n === 'calendar') inner = calendarPage(0, 0, o.top || 'DEADLINE', o.big || '1', o.sub || '', 1, COL(o.color || 'coral'));
  else if (n === 'server') inner = server(0, 0, lab, COL(o.color || 'sky'), 1, t);
  else if (n === 'gov') inner = gov(0, 0, lab || 'TAX', .9);
  else if (n === 'office') inner = office(-115, -140, lab || 'Company');
  else if (n === 'coins') { for (let i = 0; i < 7; i++) inner += coin(Math.sin(i * 2.3) * 70, 60 - i * 22, 1.1, i * 20); }
  else if (n === 'chart_up' || n === 'chart_down') {
    const up = n === 'chart_up', pts = [0, 1, 2, 3, 4].map(i => [-150 + i * 75, (up ? 1 : -1) * (60 - i * 30) + Math.sin(i * 1.7) * 14]);
    inner = card(-190, -140, 380, 280, {r: 22}) + draw('M ' + pts.map(q => q.join(' ')).join(' L '), P(t, .2, 1.4), up ? C.green : C.red, 10);
    inner += `<g transform="translate(${pts[4][0]},${pts[4][1]})">${up ? '<path d="M -18 6 L 0 -18 L 18 6 Z" fill="' + C.green + '"/>' : '<path d="M -18 -6 L 0 18 L 18 -6 Z" fill="' + C.red + '"/>'}</g>`;
  } else if (n === 'warning') inner = `<path d="M 0 -120 L 125 100 L -125 100 Z" fill="${C.amber}" ${STK} stroke-width="8"/>` + text(0, 70, '!', 150, {anchor: 'middle', w: 900});
  else if (n === 'phone') inner = `<rect x="-70" y="-130" width="140" height="260" rx="24" fill="${C.navy}" ${STK} stroke-width="6"/><rect x="-56" y="-108" width="112" height="200" rx="10" fill="#dbe7f7"/>` + (lab ? text(0, 0, lab, 26, {anchor: 'middle', w: 800}) : '');
  else if (n === 'robot') inner = `<rect x="-80" y="-70" width="160" height="130" rx="28" fill="${C.sky}" ${STK} stroke-width="7"/><circle cx="-32" cy="-10" r="16" fill="#fff"/><circle cx="32" cy="-10" r="16" fill="#fff"/><line x1="0" y1="-70" x2="0" y2="-110" ${STK} stroke-width="7"/><circle cx="0" cy="-118" r="12" fill="${C.amber}" ${STK} stroke-width="5"/><rect x="-40" y="30" width="80" height="10" rx="5" fill="#fff"/>`;
  else if (n === 'magnifier') inner = `<circle cx="-20" cy="-20" r="80" fill="#eaf3ff" ${STK} stroke-width="10"/><line x1="40" y1="40" x2="110" y2="110" ${STK} stroke-width="20"/>`;
  else if (n === 'lock') inner = `<path d="M -50 -20 v -40 a 50 50 0 0 1 100 0 v 40" fill="none" ${STK} stroke-width="14"/><rect x="-80" y="-20" width="160" height="130" rx="20" fill="${C.amber}" ${STK} stroke-width="7"/>`;
  else if (n === 'stack') { for (let i = 0; i < 6; i++) inner += `<g transform="translate(${(i % 2) * 14 - 7},${-i * 26}) rotate(${(i % 3 - 1) * 4})">${doc('', C.red, {w: 150, h: 40})}</g>`; }
  const sc = (o.s || 1) * s;
  return `<g transform="translate(${x},${y}) scale(${sc})">${inner}</g>`;
}

// ---------- HOOK: one beat per line ----------
function beatView(b, t, t0, i) {
  if (!b) return '';
  const k = P(t, t0, .6);
  if (b.t === 'headline') {
    let s = card(330, 230, 1260, 470, {r: 28});
    s += `<rect x="330" y="230" width="1260" height="16" rx="8" fill="${COL(b.color || 'coral')}"/>`;
    s += pill(390, 310, b.tag || 'IN THE NEWS', {fill: COL(b.color || 'coral'), size: 26});
    s += text(1530, 320, [b.source, b.date].filter(Boolean).join('  ·  '), 28, {anchor: 'end', w: 700, fill: C.mute});
    const L = lines(b.text, 62, 1120, 'Inter', 3);
    L.forEach((l, j) => s += text(390, 430 + j * 82, l, 62, {w: 850}));
    return `<g transform="translate(0,${(1 - eOut(k)) * 60})" opacity="${eOut(k)}">${s}</g>` + guy({x: 1700, y: 900, s: 1.1, t, pose: 'worried', color: C.amber, face: -1, op: eOut(P(t, t0 + .4, .5))});
  }
  if (b.t === 'stat') {
    let s = text(960, 560, b.value, fitSize(b.value, 230, 1500, 'Inter', 900), {anchor: 'middle', w: 900, fill: COL(b.color || 'coral')});
    s += writeOn(960, 690, b.label || '', 64, P(t, t0 + .5, 1.2), {anchor: 'middle', fill: C.ink});
    return `<g transform="translate(960,520) scale(${eBack(k)}) translate(-960,-520)">${s}</g>`;
  }
  if (b.t === 'title') {
    let s = text(960, 380, b.title, fitSize(b.title, 120, 1600, 'Inter', 900), {anchor: 'middle', w: 900, ls: -2, op: eOut(k)});
    if (b.sub) s += text(960, 500, b.sub, fitSize(b.sub, 80, 1500, 'Inter', 800), {anchor: 'middle', w: 800, fill: C.teal, op: eOut(P(t, t0 + .3, .6))});
    s += underline(700, 535, 520, P(t, t0 + .7, .8));
    const chips = b.chips || [], cols = [C.sky, C.coral, C.amber, C.teal, C.lav];
    let x = 960 - (chips.reduce((a, c) => a + tw(c, 30, 'Inter', 750) + 44 + 24, 0) - 24) / 2;
    chips.forEach((c, j) => { const w = tw(c, 30, 'Inter', 750) + 44; const p = eBack(P(t, t0 + .9 + j * .35, .5));
      if (p > 0) s += `<g transform="translate(${x + w / 2},700) scale(${p})">${pill(0, 0, c, {anchor: 'middle', fill: cols[j % cols.length], size: 30})}</g>`; x += w + 24; });
    return s;
  }
  // default "guy" beat: character + prop + hand-written line
  let s = guy({x: 560, y: 880, s: 1.35, t, pose: b.pose || 'present', color: COL(b.color || 'teal'), tie: C.navy});
  s += `<g opacity="${eOut(P(t, t0 + .2, .5))}">${prop(b.prop, 1240, 560, t - t0, 1.3)}</g>`;
  if (b.stamp) s += stamp(1560, 330, b.stamp, P(t, t0 + .9, .35), COL(b.stamp_color || 'red'), -10, 54);
  lines(b.text, 66, 1500, 'Kalam', 2).forEach((l, j) => s += writeOn(960, 200 + j * 86, l, 66, P(t, t0 + .3 + j * .5, 1.2), {anchor: 'middle', fill: j ? C.coral : C.ink}));
  return s;
}
function sHook2(t) {
  const B = SC.visual.beats || []; let o = '';
  B.forEach((b, i) => { if (i >= SC.cues.length) return;
    const s0 = i ? cs(i) : .1, e0 = i + 1 < Math.min(B.length, SC.cues.length) ? cs(i + 1) - .45 : null;
    o += G(t, s0, e0, beatView(b, t, s0, i)); });
  return o;
}

// ---------- STORY: geometric cartoon, one beat per line ----------
function sStory(t) {
  const B = SC.visual.beats || []; let o = '';
  B.forEach((b, i) => { if (i >= SC.cues.length) return;
    const s0 = i ? cs(i) : .1, e0 = i + 1 < Math.min(B.length, SC.cues.length) && !(B[i + 1] || {}).keep ? cs(i + 1) - .4 : null;
    o += G(t, s0, e0, beatView({...b, t: b.t || 'guy'}, t, s0, i)); });
  if (SC.visual.title) o += writeOn(150, 120, SC.visual.title, 44, P(t, .2, 1), {fill: C.mute});
  return o;
}

// ---------- STAT: up to 3 big numbers, one per line ----------
function countUp(v, p) { const m = String(v).match(/^([^\d]*)([\d,.]+)(.*)$/); if (!m) return v;
  const n = parseFloat(m[2].replace(/,/g, '')); if (!isFinite(n)) return v; const dec = (m[2].split('.')[1] || '').length;
  const x = n * eOut(p); return m[1] + x.toLocaleString('en-US', {minimumFractionDigits: dec, maximumFractionDigits: dec}) + m[3]; }
function sStat(t) {
  const v = SC.visual, S = (v.stats || []).slice(0, 3); let o = '';
  if (v.title) o += writeOn(960, 200, v.title, 60, P(t, .15, 1.2), {anchor: 'middle'});
  const n = S.length, w = n === 1 ? 1100 : n === 2 ? 760 : 520, gap = 50, x0 = 960 - (n * w + (n - 1) * gap) / 2;
  S.forEach((s, i) => { const s0 = i < SC.cues.length ? (i ? cs(i) : .3) : cs(SC.cues.length - 1) + i * .4;
    const p = eBack(P(t, s0, .55)); if (p <= 0) return; const x = x0 + i * (w + gap), col = COL(s.color || ['coral', 'teal', 'sky'][i]);
    let c = card(x, 300, w, 470, {r: 30}) + `<rect x="${x}" y="300" width="${w}" height="14" rx="7" fill="${col}"/>`;
    const val = countUp(s.value, P(t, s0 + .1, 1.1));
    c += text(x + w / 2, 520, val, fitSize(s.value, n === 1 ? 170 : 120, w - 80, 'Inter', 900), {anchor: 'middle', w: 900, fill: col});
    lines(s.label, 40, w - 80, 'Inter', 2).forEach((l, j) => c += text(x + w / 2, 620 + j * 52, l, 40, {anchor: 'middle', w: 650, fill: '#4a5163'}));
    if (s.note) c += text(x + w / 2, 735, s.note, 26, {anchor: 'middle', w: 600, fill: C.mute});
    o += `<g transform="translate(${x + w / 2},535) scale(${p}) translate(${-x - w / 2},-535)">${c}</g>`; });
  if (v.footer) o += G(t, at(SC.cues.length - 1, .4), null, writeOn(960, 880, v.footer, 46, P(t, at(SC.cues.length - 1, .4), 1.3), {anchor: 'middle', fill: C.coral}));
  return o;
}

// ---------- HEADLINE: news cards (source + date), one per line ----------
function sHeadline(t) {
  const v = SC.visual, N = (v.items || []).slice(0, 3); let o = '';
  if (v.title) o += writeOn(150, 190, v.title, 58, P(t, .15, 1.2));
  N.forEach((it, i) => { const s0 = i < SC.cues.length ? (i ? cs(i) : .3) : cs(SC.cues.length - 1) + i * .4;
    const p = eOut(P(t, s0, .6)); if (p <= 0) return; const y = 260 + i * 210;
    let c = card(150, y, 1320, 180, {r: 22}) + `<rect x="150" y="${y}" width="14" height="180" rx="7" fill="${COL(it.color || 'sky')}"/>`;
    c += text(200, y + 50, [it.source, it.date].filter(Boolean).join('  ·  '), 26, {w: 700, fill: C.mute});
    lines(it.text, 42, 1220, 'Inter', 2).forEach((l, j) => c += text(200, y + 105 + j * 50, l, 42, {w: 800}));
    o += `<g transform="translate(${(1 - p) * -80},0)" opacity="${p}">${c}</g>`; });
  o += guy({x: 1690, y: 880, s: 1.15, t, pose: t > cs(Math.min(1, SC.cues.length - 1)) ? 'point' : 'stand', color: C.teal, tie: C.navy, face: -1, op: eOut(P(t, .5, .5))});
  return o;
}

// ---------- DATES: generic timeline, one point per line ----------
function sDates(t) {
  const v = SC.visual, D = (v.items || []).slice(0, 6); let o = board(120, 130, 1680, 760);
  o += writeOn(180, 225, v.title || 'Key dates', 60, P(t, .2, 1.2));
  const n = D.length, X0 = 260, X1 = 1660, y = 560, xs = D.map((_, i) => n === 1 ? 960 : X0 + i * (X1 - X0) / (n - 1));
  o += `<line x1="${X0 - 40}" y1="${y}" x2="${X1 + 40}" y2="${y}" stroke="#efebe4" stroke-width="12" stroke-linecap="round"/>`;
  D.forEach((d, i) => { const s0 = i < SC.cues.length ? (i ? cs(i) : .5) : cs(SC.cues.length - 1) + i * .5; const p = eBack(P(t, s0, .5)); if (p <= 0) return;
    const col = COL(d.color || ['sky', 'amber', 'coral', 'teal', 'lav', 'green'][i % 6]);
    if (i) o += `<line x1="${xs[i - 1]}" y1="${y}" x2="${lerp(xs[i - 1], xs[i], eIO(P(t, s0 - .2, .5)))}" y2="${y}" stroke="${col}" stroke-width="12" stroke-linecap="round"/>`;
    o += `<g transform="translate(${xs[i]},${y}) scale(${p})"><circle r="24" fill="${d.big ? col : '#fff'}" stroke="${col}" stroke-width="9"/></g>`;
    const up = i % 2 === 0;
    o += text(xs[i], up ? y - 60 : y + 90, d.date, fitSize(d.date, 36, 300), {anchor: 'middle', w: 850, op: clamp(p)});
    lines(d.label, 30, 280, 'Kalam', 2).forEach((l, j) => o += text(xs[i], (up ? y - 150 : y + 140) + j * 38 - (up ? 38 : 0), l, 30, {anchor: 'middle', hand: true, w: 700, fill: '#4a5163', op: clamp(p)}));
  });
  return o;
}

// ---------- FLOW2: 2-5 steps, revealed across the lines ----------
function sFlow2(t) {
  const v = SC.visual, S = (v.steps || []).slice(0, 5), n = S.length; let o = board(120, 130, 1680, 760);
  o += writeOn(180, 225, v.title || '', 60, P(t, .2, 1.3));
  const gap = 40, w = (1600 - (n - 1) * gap) / n, x0 = 160, nc = SC.cues.length;
  S.forEach(([ti, sub], i) => {
    const ci = Math.min(nc - 1, Math.floor(i * nc / n)), tm = cs(ci) + (i * nc / n - ci) * cd(ci) + .2;
    const p = eBack(P(t, tm, .55)); if (p <= 0) return; const x = x0 + i * (w + gap), y = 320;
    let c = card(x, y, w, 420, {r: 26, stroke: i === n - 1 ? C.teal : '#ebe5da', sw: i === n - 1 ? 6 : 3});
    c += `<circle cx="${x + 56}" cy="${y + 62}" r="32" fill="${C.navy}"/>` + text(x + 56, y + 75, String(i + 1), 34, {anchor: 'middle', fill: '#fff', w: 900});
    lines(ti, fitSize(ti, 36, w - 60), w - 60, 'Inter', 2).forEach((l, k) => c += text(x + 30, y + 160 + k * 44, l, Math.min(36, fitSize(ti, 36, w - 60)), {w: 800}));
    lines(sub || '', 32, w - 60, 'Kalam', 4).forEach((l, k) => c += text(x + 30, y + 255 + k * 42, l, 32, {hand: true, w: 400, fill: '#4a5163'}));
    o += `<g transform="translate(${x + w / 2},${y + 210}) scale(${p}) translate(${-x - w / 2},${-y - 210})">${c}</g>`;
    if (i < n - 1) o += arrow(x + w + 4, y + 210, x + w + gap - 4, y + 210, P(t, tm + .4, .4), C.mute, 6);
  });
  if (v.footer) o += G(t, at(nc - 1, .6), null, pill(960, 810, v.footer, {anchor: 'middle', fill: C.green, size: 30}));
  return o;
}

// ---------- CELEBRATE2 ----------
function sCelebrate2(t) {
  const v = SC.visual;
  let o = `<g transform="translate(960,400) scale(${eBack(P(t, .1, .6)) * 1.05})">${calendarPage(0, 0, v.top || 'DONE', v.big || '✓', v.sub || '', 1, C.teal)}</g>`;
  o += ring(960, 450, 200, 170, P(t, .9, .9), C.green) + check(1150, 300, 90, P(t, 1.5, .5));
  o += guy({x: 560, y: 860, t, pose: 'cheer', color: C.teal, tie: C.navy});
  o += guy({x: 1360, y: 860, t: t + .3, pose: 'cheer', color: C.amber, face: -1});
  return o + confetti(t, 80, 3, .6);
}

Object.assign(KIND, {hook2: sHook2, story: sStory, stat: sStat, headline: sHeadline, dates: sDates, flow2: sFlow2, celebrate2: sCelebrate2});

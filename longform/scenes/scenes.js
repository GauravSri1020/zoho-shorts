// Scene templates. window.setup(data) once per scene, then window.render(t) per frame (t = seconds into the scene).
let SC = null;
const $ = id => document.getElementById(id);
const cs = i => SC.cues[Math.max(0, Math.min(i, SC.cues.length - 1))].s;
const ce = i => SC.cues[Math.max(0, Math.min(i, SC.cues.length - 1))].e;
const cd = i => ce(i) - cs(i);
const at = (i, f) => cs(i) + cd(i) * f;               // time at fraction f of cue i
function grp(t, s, e, fin = .5, fout = .4) {           // group in/out envelope -> [opacity, dy]
  const i = eOut(P(t, s, fin)), o = e == null ? 0 : eIn(P(t, e, fout));
  return [i * (1 - o), (1 - i) * 30 - o * 30];
}
function G(t, s, e, inner) { const [op, dy] = grp(t, s, e); return op <= 0.001 ? '' : `<g transform="translate(0,${dy.toFixed(1)})" opacity="${op.toFixed(3)}">${inner}</g>`; }
function lvl(t) { const L = SC.level || []; const i = Math.floor(t * 30); return L[Math.max(0, Math.min(L.length - 1, i))] || 0; }

// ============ HOOK ============
function sHook(t) {
  let o = '';
  const a1 = cs(1), a2 = cs(2), a3 = cs(3);
  // 1) date + PDF by email crossed out
  o += G(t, .1, a1 - .45, (() => {
    let s = `<g transform="translate(560,520) scale(${eBack(P(t, .15, .7)) * 1.25})">${calendarPage(0, 0, 'JANUARY', '1', '2027', 1)}</g>`;
    const k = P(t, 1.2, 1.2);
    s += guy({x: 1180, y: 860, s: 1.3, t, pose: k < 1 ? 'carry' : 'present', walk: k < 1, color: C.teal, tie: C.navy, hold: k < 1 ? `<g transform="scale(.7)">${doc('PDF')}</g>` : ''});
    const fly = P(t, 2.2, 1.6);
    if (fly > 0) s += `<g transform="translate(${lerp(1300, 1500, eOut(fly))},${lerp(620, 470, eOut(fly))}) rotate(${-8 * fly})">${envelope(1.1)}<g transform="translate(70,-40) scale(.55)">${doc('PDF')}</g></g>`;
    s += cross(1520, 480, 190, P(t, at(0, .62), .6));
    s += writeOn(1520, 690, 'no longer enough', 62, P(t, at(0, .7), 1.2), {anchor: 'middle', fill: C.coral});
    return s;
  })());
  // 2) structured e-invoice through an ASP to the FTA
  o += G(t, a1, a2 - .45, (() => {
    let s = guy({x: 300, y: 860, s: 1.25, t, pose: 'present', color: C.teal, tie: C.navy});
    s += `<g transform="translate(960,640) scale(${eBack(P(t, a1 + .4, .6))})">${server(0, 0, '', C.sky, 1, P(t, a1, 20))}</g>`;
    s += text(960, 830, 'Accredited provider (ASP)', 36, {anchor: 'middle', op: eOut(P(t, a1 + .6, .5))});
    s += `<g transform="translate(1560,620)">${gov(0, 0, 'FTA', .9 * eBack(P(t, a1 + .8, .6)))}</g>`;
    s += arrow(420, 640, 820, 640, P(t, at(1, .25), .8), C.ink, 7, true) + arrow(1100, 620, 1380, 520, P(t, at(1, .6), .8), C.ink, 7, true);
    const k1 = eIO(P(t, at(1, .2), 1.4)), k2 = eIO(P(t, at(1, .62), 1.2));
    const px = k2 > 0 ? lerp(960, 1520, k2) : lerp(390, 960, k1), py = k2 > 0 ? lerp(560, 420, k2) : lerp(560, 560, k1);
    if (k2 < 1) s += `<g transform="translate(${px},${py}) scale(.62) rotate(${Math.sin(t * 3) * 4})" opacity="${1 - eIn(P(t, at(1, .62) + .9, .3))}">${einv()}</g>`;
    s += G(t, at(1, .8), null, pill(1560, 200, 'near real time', {anchor: 'middle', fill: C.teal, size: 30}));
    return s;
  })());
  // 3) smaller business - later date, clock ticking
  o += G(t, a2, a3 - .45, (() => {
    let s = clock(620, 520, t, 2.4, 3);
    s += G(t, a2 + .5, null, pill(1300, 430, 'AED 50M+  →  1 Jan 2027', {anchor: 'middle', fill: C.coral, size: 40}));
    s += G(t, at(2, .3), null, pill(1300, 560, 'Under AED 50M  →  1 Jul 2027', {anchor: 'middle', fill: C.teal, size: 40}));
    s += writeOn(1300, 720, 'the clock has started', 56, P(t, at(2, .62), 1.2), {anchor: 'middle', fill: C.ink});
    return s;
  })());
  // 4) title
  o += G(t, a3, null, (() => {
    let s = text(960, 360, 'UAE E-Invoicing', 132, {anchor: 'middle', w: 900, ls: -2});
    s += text(960, 490, 'in Zoho Books', 96, {anchor: 'middle', w: 800, fill: C.teal, op: eOut(P(t, a3 + .3, .6))});
    s += underline(700, 525, 520, P(t, a3 + .7, .8));
    s += writeOn(960, 615, 'everything to do before your deadline', 54, P(t, a3 + .9, 1.6), {anchor: 'middle', fill: C.mute});
    const chips = ['What changes', 'Who goes live when', 'The fines', 'Zoho Books setup'];
    const cols = [C.sky, C.coral, C.amber, C.teal];
    let x = 960 - (chips.reduce((a, c) => a + tw(c, 30, 'Inter', 750) + 44 + 24, 0) - 24) / 2;
    chips.forEach((c, i) => { const w = tw(c, 30, 'Inter', 750) + 44; const p = eBack(P(t, at(3, .12 + i * .17), .5));
      if (p > 0) s += `<g transform="translate(${x + w / 2},740) scale(${p})">${pill(0, 0, c, {anchor: 'middle', fill: cols[i], size: 30})}</g>`; x += w + 24; });
    return s;
  })());
  return o;
}

// ============ CARTOONS ============
function sOldWay(t) {
  let o = '';
  const dim = eOut(P(t, cs(2) - .1, .6));
  let w = office(90, 500, 'Your company') + office(1600, 500, 'Client', '#fde9cf');
  w += `<g opacity="${.35 + .65 * eOut(P(t, cs(1), .6))}">${gov(1170, 420, 'FTA', .62)}</g>`;
  const k = P(t, .4, Math.max(2, at(0, .55) - .4));
  const fly = P(t, at(0, .62), 1.6);
  w += guy({x: lerp(420, 820, eIO(k)), y: 870, s: 1.25, t, pose: k < 1 ? 'carry' : 'present', walk: k < 1, color: C.teal, tie: C.navy, hold: k < 1 ? `<g transform="scale(.62)">${doc('PDF')}</g>` : ''});
  if (k >= 1 && fly <= 0) w += `<g transform="translate(930,520) scale(.62)">${doc('PDF')}</g>`;
    if (fly > 0 && fly < 1) w += `<g transform="translate(${lerp(960, 1640, eIO(fly))},${lerp(540, 600, eIO(fly)) - Math.sin(fly * Math.PI) * 160}) rotate(${Math.sin(fly * 6) * 8})" opacity="${1 - eIn(P(fly, .8, .2))}">${envelope(.9)}</g>`;
  w += G(t, at(0, .62), null, text(1290, 560, '@ email', 40, {anchor: 'middle', w: 800, fill: C.sky}));
  // client retypes
  if (t > cs(1) - .2) {
    w += guy({x: 1480, y: 880, s: 1.15, t, pose: 'type', color: C.amber, face: -1, op: eOut(P(t, cs(1) - .2, .5))});
    w += `<g opacity="${eOut(P(t, cs(1), .5))}">${laptop(1350, 860, 1.05)}</g>`;
    w += writeOn(1420, 470, 'types it in again', 42, P(t, cs(1) + .6, 1.2), {anchor: 'middle', fill: C.coral});
    w += draw('M 330 500 C 600 250, 900 220, 1050 260', P(t, at(1, .5), 1.2), C.mute, 6, 'stroke-dasharray="0.02 0.03"');
    w += writeOn(700, 250, 'months later, in the VAT return', 40, P(t, at(1, .55), 1.6), {anchor: 'middle', fill: C.mute});
  }
  o += `<g opacity="${1 - .82 * dim}">${w}</g>`;
  if (dim > 0) {
    const items = [['PDF', C.red], ['Word', C.sky], ['Scan', C.mute], ['Email', C.amber]];
    o += writeOn(960, 300, 'NOT an e-invoice', 96, P(t, cs(2) + .2, 1.2), {anchor: 'middle', fill: C.coral});
    items.forEach(([l, c], i) => {
      const x = 480 + i * 320, p = eBack(P(t, at(2, .1 + i * .13), .5));
      if (p <= 0) return;
      o += `<g transform="translate(${x},600) scale(${p})">${l === 'Email' ? envelope(1.3) : doc(l, c)}</g>`;
      o += cross(x, 600, 170, P(t, at(2, .2 + i * .13), .45));
    });
  }
  return o;
}

function sFiveCorner(t) {
  let o = '';
  const N = [[300, 860], [730, 700], [1190, 700], [1630, 860], [960, 400]];
  o += writeOn(150, 215, 'The 5-corner model', 64, P(t, .3, 1.4), {fill: C.ink});
  o += underline(150, 240, 520, P(t, 1.4, .7));
  // peppol band
  const pb = eOut(P(t, at(0, .5), .8));
  o += `<g opacity="${pb}"><rect x="640" y="590" width="640" height="230" rx="40" fill="${C.sky}" opacity=".08"/>${pill(960, 860, 'Peppol network', {anchor: 'middle', fill: C.sky, size: 28})}</g>`;
  // corner placeholders pop in during cue 0
  N.forEach(([x, y], i) => {
    const p = eBack(P(t, at(0, .15 + i * .1), .45)); if (p <= 0) return;
    const by = i === 4 ? y - 200 : (i === 0 || i === 3 ? y - 330 : y - 170);
    o += `<g transform="translate(${x + (i === 4 ? -200 : -90)},${by}) scale(${p})"><circle r="30" fill="${C.navy}"/>${text(0, 11, String(i + 1), 32, {anchor: 'middle', fill: '#fff', w: 900})}</g>`;
  });
  const show = (i, s) => eOut(P(t, s, .6));
  o += `<g opacity="${.15 + .85 * show(0, cs(1))}">${guy({x: N[0][0], y: N[0][1], t, pose: t > at(1, .4) && t < at(1, .9) ? 'present' : 'stand', color: C.teal, tie: C.navy})}${text(N[0][0], N[0][1] + 60, 'You (supplier)', 30, {anchor: 'middle'})}</g>`;
  o += `<g opacity="${.15 + .85 * show(1, at(1, .35))}">${server(N[1][0], N[1][1], 'Your ASP', C.sky, .9, t > cs(2) ? t : 0)}</g>`;
  o += `<g opacity="${.15 + .85 * show(2, cs(2))}">${server(N[2][0], N[2][1], "Buyer's ASP", C.lav, .9, t > at(2, .4) ? t : 0)}</g>`;
  o += `<g opacity="${.15 + .85 * show(3, at(2, .55))}">${guy({x: N[3][0], y: N[3][1], t, pose: t > at(2, .85) ? 'cheer' : 'stand', color: C.amber, face: -1})}${text(N[3][0], N[3][1] + 60, 'Buyer', 30, {anchor: 'middle'})}</g>`;
  o += `<g opacity="${.15 + .85 * show(4, cs(3))}">${gov(N[4][0], N[4][1], 'FTA', .75)}</g>`;
  o += arrow(380, 700, 610, 700, P(t, at(1, .5), .7), C.ink, 6);
  o += arrow(850, 700, 1060, 700, P(t, at(2, .15), .6), C.ink, 6);
  o += arrow(1310, 700, 1540, 760, P(t, at(2, .6), .6), C.ink, 6);
  o += arrow(760, 590, 880, 420, P(t, at(3, .25), .7), C.teal, 7);
  // invoice token path
  const k1 = eIO(P(t, at(1, .55), 1.2)), k2 = eIO(P(t, at(2, .2), 1.3)), k3 = eIO(P(t, at(2, .65), 1.0));
  let tx = lerp(380, 730, k1), ty = 610;
  if (k2 > 0) { tx = lerp(730, 1190, k2); }
  if (k3 > 0) { tx = lerp(1190, 1560, k3); ty = lerp(610, 700, k3); }
  if (t > at(1, .5)) o += `<g transform="translate(${tx},${ty - 40}) scale(.45)">${einv()}</g>`;
  o += check(730, 520, 60, P(t, at(2, .05), .4));
  // tax data packet to FTA
  const k4 = eIO(P(t, at(3, .4), 1.1));
  if (k4 > 0 && k4 < 1) o += `<g transform="translate(${lerp(760, 880, k4)},${lerp(590, 430, k4)})"><rect x="-60" y="-24" width="120" height="48" rx="12" fill="${C.teal}"/>${text(0, 9, 'tax data', 22, {anchor: 'middle', fill: '#fff', w: 800})}</g>`;
  o += check(1100, 230, 70, P(t, at(3, .75), .4));
  o += G(t, cs(4), null, pill(1540, 330, 'No retyping', {anchor: 'middle', fill: C.navy, size: 30}) );
  o += G(t, at(4, .45), null, pill(1540, 410, 'Near real time', {anchor: 'middle', fill: C.teal, size: 30}));
  return o;
}

function sFourteen(t) {
  let o = card(150, 190, 820, 650);
  o += writeOn(200, 270, 'After go-live, every e-invoice:', 46, P(t, .3, 1.4));
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
  days.forEach((d, i) => o += text(250 + i * 150, 340, d, 26, {anchor: 'middle', fill: C.mute, w: 700}));
  for (let n = 0; n < 15; n++) {
    const r = Math.floor(n / 5), c = n % 5, x = 190 + c * 150, y = 365 + r * 130;
    const on = P(t, at(1, .1 + n * .055), .25);
    const fill = n < 14 && on > 0 ? C.teal : '#f2f0ec';
    o += `<rect x="${x}" y="${y}" width="120" height="110" rx="18" fill="${fill}" opacity="${n < 14 ? (.25 + .75 * Math.max(on, n < 14 ? 0 : 0)) + (on > 0 ? 0 : .5) : .5}"/>`;
    o += text(x + 60, y + 70, String(n + 1), 44, {anchor: 'middle', w: 800, fill: on > 0 && n < 14 ? '#fff' : C.mute});
  }
  o += ring(190 + 3 * 150 + 60, 365 + 2 * 130 + 55, 80, 66, P(t, at(1, .88), .6));
  o += G(t, at(1, .9), null, pill(560, 800, 'issued + sent within 14 business days', {anchor: 'middle', fill: C.coral, size: 28}));
  // right: person with growing pile
  const worried = t > cs(2);
  o += guy({x: 1300, y: 870, s: 1.25, t, pose: worried ? 'worried' : 'present', color: C.teal, tie: C.navy, face: -1});
  const pile = Math.floor(clamp(P(t, cs(2) - .3, cd(2) * .8)) * 9);
  for (let i = 0; i < pile; i++) o += `<g transform="translate(${1600 + Math.sin(i * 1.7 + t * 2) * (i * .8)},${845 - i * 26}) rotate(${(rnd(i) - .5) * 14})"><rect x="-90" y="-14" width="180" height="26" rx="4" fill="#fff" ${STK} stroke-width="5"/></g>`;
  if (pile > 0) o += text(1600, 845 - pile * 26 - 40, 'month end', 34, {anchor: 'middle', hand: true, fill: C.coral});
  o += cross(1600, 700, 120, P(t, at(2, .75), .5));
  return o;
}

function sPenalty(t) {
  let o = '';
  // cue 0: decision paper
  o += G(t, .2, cs(1) - .1, (() => {
    let s = card(560, 200, 800, 600, {r: 18});
    s += `<circle cx="960" cy="330" r="62" fill="none" stroke="${C.amber}" stroke-width="8"/><circle cx="960" cy="330" r="44" fill="${C.amber}" opacity=".25"/>`;
    s += text(960, 345, '173', 40, {anchor: 'middle', w: 900});
    s += text(960, 480, 'Cabinet Decision', 58, {anchor: 'middle', w: 800});
    s += text(960, 560, 'No. 173 of 2026', 58, {anchor: 'middle', w: 800, fill: C.coral});
    s += writeOn(960, 660, 'e-invoicing fines', 46, P(t, .9, 1.2), {anchor: 'middle', fill: C.mute});
    return s;
  })());
  // cue 1: monthly fine with cap
  const L = G(t, cs(1), null, (() => {
    let s = card(130, 170, 800, 680);
    s += text(180, 250, 'No system / no ASP', 40, {w: 800});
    s += text(180, 345, 'AED 5,000', 84, {w: 900, fill: C.coral});
    s += text(180, 395, 'for every month', 32, {w: 600, fill: C.mute});
    const months = 'JFMAMJ'.split('');
    const k = clamp(P(t, at(1, .35), cd(1) * .6)) * 6;
    let sum = 0;
    months.forEach((m, i) => { const on = k > i; if (on) sum += 5000;
      s += `<rect x="${180 + i * 112}" y="440" width="96" height="60" rx="12" fill="${on ? C.coral : '#f2f0ec'}"/>` + text(228 + i * 112, 480, m, 28, {anchor: 'middle', w: 800, fill: on ? '#fff' : C.mute}); });
    const bw = 700 * sum / 30000;
    s += `<rect x="180" y="560" width="700" height="56" rx="14" fill="#f2f0ec"/><rect x="180" y="560" width="${bw}" height="56" rx="14" fill="${C.coral}"/>`;
    s += text(180, 720, 'AED ' + sum.toLocaleString('en-US'), 64, {w: 900});
    s += text(180, 775, sum >= 30000 ? '6 months late = AED 30,000' : 'and it keeps adding up', 32, {w: 600, fill: C.mute});
    return s;
  })());
  o += L;
  // cue 2: per invoice
  o += G(t, cs(2), null, (() => {
    let s = card(990, 170, 800, 680);
    s += text(1040, 250, 'E-invoice not issued / sent', 40, {w: 800});
    s += text(1040, 345, 'AED 100', 84, {w: 900, fill: C.coral});
    s += text(1040, 395, 'per invoice', 32, {w: 600, fill: C.mute});
    const n = Math.floor(clamp(P(t, at(2, .2), cd(2) * .55)) * 24);
    for (let i = 0; i < n; i++) { const x = 1060 + (i % 8) * 88, y = 470 + Math.floor(i / 8) * 96;
      s += `<g transform="translate(${x + 30},${y + 35}) scale(.36)">${doc('', C.red)}</g>` + text(x + 58, y + 24, '-100', 22, {w: 900, fill: C.coral}); }
    s += G(t, at(2, .55), null, pill(1390, 780, 'max AED 5,000 a month', {anchor: 'middle', fill: C.navy, size: 28}));
    s += G(t, at(2, .78), null, text(1390, 838, 'same for e-credit notes', 30, {anchor: 'middle', hand: true, fill: C.mute}));
    return s;
  })());
  o += stamp(760, 230, 'EVERY MONTH', P(t, at(1, .3), .35), C.red, -8, 30);
  if (t > cs(3)) { for (let i = 0; i < 10; i++) { const tt = t - cs(3) - i * .25; if (tt < 0) continue;
      if (tt < 2.2) o += coin(960 + Math.sin(i * 2.1) * 260 * Math.min(1, tt), 820 - tt * 330 + tt * tt * 60, .9, tt * 200); } }
  o += writeOn(960, 140, 'small amounts that add up fast', 50, P(t, cs(3) + .2, 1.4), {anchor: 'middle', fill: C.coral});
  return o;
}

function sCelebrate(t) {
  let o = `<g transform="translate(960,400) scale(${eBack(P(t, .1, .6)) * 1.05})">${calendarPage(0, 0, 'JANUARY', '1', '2027', 1, C.teal)}</g>`;
  o += ring(960, 450, 200, 170, P(t, .9, .9), C.green) + check(1150, 300, 90, P(t, 1.5, .5));
  o += guy({x: 560, y: 860, t, pose: 'cheer', color: C.teal, tie: C.navy});
  o += guy({x: 1360, y: 860, t: t + .3, pose: 'cheer', color: C.amber, face: -1});
  o += confetti(t, 80, 3, .6);
  return o;
}

// ============ BOARDS ============
function sCompare(t) {
  const v = SC.visual; let o = board(120, 130, 1680, 760);
  o += writeOn(190, 235, v.title, 64, P(t, .2, 1.5));
  o += underline(190, 262, tw(v.title, 64, 'Kalam') , P(t, 1.5, .7));
  o += draw('M 960 300 L 960 850', P(t, .6, .8), '#e6e0d6', 5);
  const when = {};
  v.cues.forEach(([ci, ...ids]) => ids.forEach((id, k) => when[id] = cs(ci) + .3 + k * Math.min(1.6, cd(ci) / (ids.length + .5))));
  const hdr = (x, label, col, tm) => G(t, tm, null, pill(x, 330, label, {fill: col, size: 30}));
  o += hdr(200, v.left.title, C.green, (when.L0 || 0) - .3) + hdr(1010, v.right.title, C.red, (when.R0 || 0) - .3);
  v.left.items.forEach((it, i) => { const tm = when['L' + i]; if (tm == null) return;
    o += check(225, 425 + i * 105 - 14, 44, P(t, tm, .4)) + writeOn(275, 425 + i * 105, it, 48, P(t, tm + .15, 1.1)); });
  v.right.items.forEach((it, i) => { const tm = when['R' + i]; if (tm == null) return;
    o += cross(1035, 425 + i * 105 - 14, 34, P(t, tm, .4)) + writeOn(1085, 425 + i * 105, it, 48, P(t, tm + .15, 1.1)); });
  return o;
}

function sTimeline(t) {
  const v = SC.visual; let o = board(120, 130, 1680, 760);
  o += writeOn(180, 220, v.title, 58, P(t, .2, 1.4));
  const X0 = 720, X1 = 1720, mx = m => X0 + m * (X1 - X0) / 17.5;
  const pe = eOut(P(t, .4, .8));
  o += `<g opacity="${pe}"><rect x="${mx(0)}" y="250" width="${mx(6) - mx(0) - 6}" height="40" rx="10" fill="#f2efe9"/><rect x="${mx(6)}" y="250" width="${mx(17.5) - mx(6)}" height="40" rx="10" fill="#eaf4f2"/>
    ${text((mx(0) + mx(6)) / 2, 279, '2026', 26, {anchor: 'middle', w: 800, fill: C.mute})}${text((mx(6) + mx(17.5)) / 2, 279, '2027', 26, {anchor: 'middle', w: 800, fill: C.teal})}
    <line x1="${mx(6) - 3}" y1="250" x2="${mx(6) - 3}" y2="860" stroke="#e3ddd2" stroke-width="3" stroke-dasharray="6 10"/></g>`;
  const mon = {'1 Jul 2026': 0, '30 Oct 2026': 3.97, '1 Jan 2027': 6, '31 Mar 2027': 8.97, '1 Jul 2027': 12, '1 Oct 2027': 15};
  v.rows.forEach((r, i) => {
    const s0 = cs(i), y = 380 + i * 135, col = C[r.color] || C.ink;
    const op = eOut(P(t, s0, .5)); if (op <= 0) return;
    o += `<g opacity="${op}">`;
    o += `<rect x="160" y="${y - 44}" width="10" height="88" rx="5" fill="${col}"/>`;
    o += writeOn(190, y + 14, r.who, 40, P(t, s0 + .1, 1));
    o += `<line x1="${X0}" y1="${y}" x2="${X1}" y2="${y}" stroke="#efebe4" stroke-width="10" stroke-linecap="round"/>`;
    const st = r.steps.map((s, k) => ({...s, x: mx(mon[s[0]]), tm: k === 0 ? s0 + Math.min(1.2, cd(i) * .2) : at(i, .58)}));
    if (st.length > 1) o += `<line x1="${st[0].x}" y1="${y}" x2="${lerp(st[0].x, st[1].x, eIO(P(t, st[0].tm + .3, st[1].tm - st[0].tm)))}" y2="${y}" stroke="${col}" stroke-width="10" stroke-linecap="round"/>`;
    st.forEach((s, k) => { const p = eBack(P(t, s.tm, .5)); if (p <= 0) return;
      const live = s[1] === 'GO LIVE';
      o += `<g transform="translate(${s.x},${y}) scale(${p})"><circle r="${live ? 20 : 15}" fill="${live ? col : '#fff'}" stroke="${col}" stroke-width="7"/></g>`;
      const near = st.length > 1 && Math.abs(st[1].x - st[0].x) < 260; const an = near ? (k === 0 ? 'end' : 'start') : 'middle', dx = near ? (k === 0 ? 14 : -14) : 0;
      o += text(s.x + dx, y - 34, s[0], 28, {anchor: an, w: 800, op: p > .5 ? 1 : 0});
      o += live ? `<g opacity="${clamp(p)}">${pill(s.x, y + 52, 'GO LIVE', {anchor: 'middle', fill: col, size: 22, pad: 14})}</g>` : text(s.x + dx, y + 58, s[1], 30, {anchor: an, hand: true, w: 700, fill: C.mute, op: p > .5 ? 1 : 0});
    });
    o += '</g>';
  });
  return o;
}

function sBadge(t) {
  const v = SC.visual; let o = '';
  o += G(t, .2, null, (() => {
    let s = card(420, 190, 1080, 520, {r: 32});
    s += `<rect x="420" y="190" width="1080" height="18" rx="9" fill="${C.teal}"/>`;
    s += `<g transform="translate(600,450)"><path d="M 0 -130 L 110 -90 V 10 C 110 80 50 120 0 140 C -50 120 -110 80 -110 10 V -90 Z" fill="${C.teal}" opacity=".12" stroke="${C.teal}" stroke-width="8"/></g>`;
    s += check(600, 450, 110, P(t, at(1, .5), .6), C.teal, 16);
    s += text(760, 330, 'UAE Ministry of Finance', 30, {w: 700, fill: C.mute});
    s += text(760, 372, 'accredited e-invoicing service providers', 30, {w: 700, fill: C.mute});
    s += writeOn(760, 480, v.name, 58, P(t, at(1, .2), 1.6), {hand: false, w: 850});
    s += G(t, at(1, .7), null, pill(760, 560, 'Accredited ASP', {fill: C.green, size: 28}));
    return s;
  })());
  o += `<g transform="translate(330,250) rotate(-7) scale(${eBack(P(t, .3, .6))})"><rect x="-120" y="-60" width="240" height="120" rx="8" fill="#ffe7a8"/>${text(0, 14, 'Good news', 40, {anchor: 'middle', hand: true})}</g>`;
  const fy = 820, xs = [560, 960, 1360], labels = ['Zoho Books', 'Peppol', 'Your customer'], cols = [C.navy, C.sky, C.amber];
  xs.forEach((x, i) => { const p = eBack(P(t, at(2, .15 + i * .2), .5)); if (p > 0) o += `<g transform="translate(${x},${fy}) scale(${p})">${pill(0, 0, labels[i], {anchor: 'middle', fill: cols[i], size: 32})}</g>`; });
  o += arrow(680, fy, 860, fy, P(t, at(2, .3), .5)) + arrow(1060, fy, 1220, fy, P(t, at(2, .5), .5));
  return o;
}

function wrap(s, size, maxw, fam = 'Kalam') { const ws = s.split(' '); const L = []; let cur = '';
  ws.forEach(w => { const n = cur ? cur + ' ' + w : w; if (tw(n, size, fam, 700) > maxw && cur) { L.push(cur); cur = w; } else cur = n; }); if (cur) L.push(cur); return L; }

function sFlow(t) {
  const v = SC.visual; let o = board(120, 130, 1680, 760);
  o += writeOn(180, 225, v.title, 60, P(t, .2, 1.3));
  const when = {}; v.cues.forEach(([ci, ...ids]) => ids.forEach((id, k) => when[id] = cs(ci) + .2 + k * cd(ci) * .45));
  v.steps.forEach(([ti, sub], i) => {
    const tm = when[i]; const p = eBack(P(t, tm, .55)); if (p <= 0) return;
    const x = 175 + i * 410, y = 330;
    o += `<g transform="translate(${x + 170},${y + 200}) scale(${p}) translate(${-x - 170},${-y - 200})">`;
    o += card(x, y, 340, 400, {r: 26, stroke: i === 3 ? C.teal : '#ebe5da', sw: i === 3 ? 6 : 3});
    o += `<circle cx="${x + 60}" cy="${y + 64}" r="32" fill="${C.navy}"/>` + text(x + 60, y + 77, String(i + 1), 34, {anchor: 'middle', fill: '#fff', w: 900});
    o += text(x + 32, y + 160, ti, 36, {w: 800});
    wrap(sub, 34, 280).forEach((l, k) => o += text(x + 32, y + 220 + k * 46, l, 34, {hand: true, w: 400, fill: '#4a5163'}));
    if (i === 3) o += `<rect x="${x + 32}" y="${y + 300}" width="276" height="56" rx="12" fill="${C.sky}"/>` + text(x + 170, y + 336, 'Verify & Complete', 24, {anchor: 'middle', fill: '#fff', w: 800});
    o += '</g>';
    if (i < 3) o += arrow(x + 352, y + 200, x + 400, y + 200, P(t, tm + .4, .4), C.mute, 6);
  });
  o += G(t, at(2, .7), null, pill(1485, 800, '●  Connection active', {anchor: 'middle', fill: C.green, size: 30}));
  return o;
}

function sFormula(t) {
  let o = board(120, 130, 1680, 760);
  o += writeOn(180, 225, 'Your Peppol ID', 64, P(t, .2, 1.2));
  o += G(t, .8, null, `<g transform="translate(1620,210) rotate(8)"><rect x="-110" y="-44" width="220" height="88" rx="8" fill="#ffe7a8"/>${text(0, 12, 'confusing?', 36, {anchor: 'middle', hand: true})}</g>`);
  const box = (x, y, w, label, sub, col, p) => p <= 0 ? '' : `<g transform="translate(${x + w / 2},${y}) scale(${eBack(p)})"><rect x="${-w / 2}" y="-60" width="${w}" height="120" rx="22" fill="${col}"/>${text(0, 12, label, 46, {anchor: 'middle', fill: '#fff', w: 900})}${sub ? text(0, 100, sub, 28, {anchor: 'middle', hand: true, fill: C.mute}) : ''}</g>`;
  const y = 410;
  const gop = eOut(P(t, .5, .5)) * (1 - eOut(P(t, cs(1) - .2, .4)));
  if (gop > 0) o += guy({x: 960, y: 820, s: 1.3, t, pose: 'shrug', color: C.teal, tie: C.navy, op: gop}) + `<g opacity="${gop}">${text(960, 420, '?', 160, {anchor: 'middle', w: 900, fill: C.amber})}</g>`;
  o += box(220, y, 300, '0235', 'fixed prefix', C.navy, P(t, at(1, .02), .5));
  o += G(t, at(1, .15), null, text(585, y + 20, '+', 80, {anchor: 'middle', w: 900}));
  o += box(650, y, 520, 'TIN  (10 digits)', 'your tax number', C.teal, P(t, at(1, .2), .5));
  o += G(t, at(1, .35), null, text(1240, y + 20, '=', 80, {anchor: 'middle', w: 900}));
  o += box(1310, y, 420, 'Peppol ID', '', C.amber, P(t, at(1, .35), .5));
  // TRN digits
  const trn = '100123456700003'.split('');
  const t0 = at(1, .5);
  trn.forEach((d, i) => { const p = eBack(P(t, t0 + i * .06, .4)); if (p <= 0) return;
    const x = 420 + i * 72; o += `<g transform="translate(${x},660) scale(${p})"><rect x="-30" y="-40" width="60" height="80" rx="12" fill="${i < 10 ? '#e3f4f1' : '#f2f0ec'}" stroke="${i < 10 ? C.teal : '#ddd6ca'}" stroke-width="4"/>${text(0, 16, d, 44, {anchor: 'middle', w: 800})}</g>`; });
  o += G(t, t0, null, text(380, 672, 'TRN', 40, {anchor: 'end', w: 900}) + text(1520, 672, '(example)', 28, {hand: true, fill: C.mute}));
  o += draw(`M 392 720 q 0 30 30 30 h 290 q 30 0 30 22 q 0 -22 30 -22 h 290 q 30 0 30 -30`, P(t, at(1, .72), .8), C.teal, 6);
  o += writeOn(720, 820, 'first 10 digits = TIN', 40, P(t, at(1, .78), 1), {anchor: 'middle', fill: C.teal});
  o += G(t, cs(2), null, pill(1460, 760, 'Your ASP creates it', {anchor: 'middle', fill: C.green, size: 28}));
  o += G(t, at(2, .45), null, pill(1460, 835, 'Keep your TRN correct', {anchor: 'middle', fill: C.coral, size: 28}));
  return o;
}

function sRecord(t) {
  const v = SC.visual; let o = '';
  o += G(t, .2, null, (() => {
    let s = card(150, 170, 1000, 690, {r: 26});
    s += `<rect x="150" y="170" width="1000" height="90" rx="26" fill="#f4f6f9"/><rect x="150" y="230" width="1000" height="30" fill="#f4f6f9"/>`;
    s += text(200, 228, 'Customer', 34, {w: 800});
    const tabs = ['Address', 'Other Details', 'Contact Persons']; let x = 200;
    tabs.forEach((tb, i) => { const w = tw(tb, 26, 'Inter', 700) + 30; const on = i === 1 && t > at(0, .5);
      s += text(x + 15, 310, tb, 26, {w: 700, fill: on ? C.sky : C.mute}); if (on) s += `<rect x="${x}" y="326" width="${w * eOut(P(t, at(0, .5), .4))}" height="5" rx="2" fill="${C.sky}"/>`; x += w + 20; });
    s += `<line x1="200" y1="332" x2="1100" y2="332" stroke="#eceff3" stroke-width="3"/>`;
    const vals = ['1001234567', 'Sample Trading LLC', '0235 1001234567', ''];
    v.customer.fields.forEach((f, i) => { const y = 400 + i * 110;
      s += text(200, y + 8, f, 28, {w: 650, fill: '#4a5163'});
      s += `<rect x="560" y="${y - 32}" width="520" height="62" rx="12" fill="#fff" stroke="#dfe3ea" stroke-width="3"/>`;
      const tm = at(1, .08 + i * .2); const p = P(t, tm, .9);
      if (i < 3) { const n = Math.floor(vals[i].length * p); s += text(582, y + 10, vals[i].slice(0, n), 28, {w: 600}); if (p > 0 && p < 1 && Math.floor(t * 4) % 2) s += `<rect x="${586 + tw(vals[i].slice(0, n), 28, 'Inter', 600)}" y="${y - 16}" width="3" height="32" fill="${C.ink}"/>`; }
      else if (p > 0) s += `<g opacity="${eOut(p)}">${pill(582, y - 1, '✓', {fill: C.green, size: 24, pad: 16})}</g>`;
      s += check(1110, y - 4, 34, P(t, tm + .9, .35));
    });
    s += text(1130, 845, 'illustration', 22, {anchor: 'end', fill: C.mute, w: 500});
    return s;
  })());
  o += G(t, cs(2), null, (() => {
    let s = card(1220, 240, 550, 470, {r: 26});
    s += text(1270, 310, 'Item', 34, {w: 800});
    s += text(1270, 390, 'Type', 28, {w: 650, fill: '#4a5163'});
    const pick = t > at(2, .45) ? 0 : -1;
    ['Goods', 'Service'].forEach((x, i) => { s += `<rect x="${1270 + i * 200}" y="415" width="180" height="62" rx="14" fill="${pick === i ? C.navy : '#f2f0ec'}"/>` + text(1360 + i * 200, 456, x, 28, {anchor: 'middle', w: 750, fill: pick === i ? '#fff' : C.ink}); });
    s += text(1270, 540, 'Unit', 28, {w: 650, fill: '#4a5163'});
    s += `<rect x="1270" y="560" width="440" height="62" rx="12" fill="#fff" stroke="#dfe3ea" stroke-width="3"/>`;
    s += text(1292, 602, t > at(2, .7) ? 'pcs' : '', 28, {w: 600});
    s += check(1730, 590, 34, P(t, at(2, .8), .35));
    return s;
  })());
  o += stamp(1495, 800, 'CLEAN DATA', P(t, cs(3) + .1, .35), C.green, -8, 46);
  return o;
}

function sChecklist(t) {
  const v = SC.visual; let o = board(120, 130, 1680, 760);
  o += writeOn(180, 225, v.title, 62, P(t, .1, 1.2));
  o += underline(180, 250, tw(v.title, 62, 'Kalam'), P(t, 1.2, .6));
  o += guy({x: 1560, y: 840, s: 1.2, t, pose: t > at(5, .7) ? 'cheer' : 'present', color: C.teal, tie: C.navy, face: -1, hold: '', op: eOut(P(t, .5, .6))});
  o += `<g transform="translate(1395,560) rotate(-6)" opacity="${eOut(P(t, .5, .6))}"><rect x="-70" y="-90" width="140" height="180" rx="12" fill="${C.amber}" stroke="${C.ink}" stroke-width="6"/><rect x="-52" y="-66" width="104" height="140" rx="6" fill="#fff"/>${[0,1,2,3].map(i => `<line x1="-34" y1="${-40 + i * 30}" x2="34" y2="${-40 + i * 30}" stroke="#c7ccd6" stroke-width="6" stroke-linecap="round"/>`).join('')}</g>`;
  v.items.forEach((it, i) => {
    const y = 330 + i * 92, s0 = cs(i);
    const op = eOut(P(t, s0, .4)); if (op <= 0) return;
    o += `<g opacity="${op}"><rect x="190" y="${y - 38}" width="54" height="54" rx="12" fill="#fff" stroke="${C.ink}" stroke-width="5"/></g>`;
    o += check(217, y - 11, 38, P(t, at(i, .7), .35), C.green, 9);
    o += text(275, y + 4, String(i + 1) + '.', 44, {hand: true, w: 700, fill: C.teal, op});
    o += writeOn(325, y + 4, it, 44, P(t, s0 + .15, Math.min(1.8, cd(i) * .6)));
  });
  return o;
}

// ============ CHAPTER ============
function sChapter(t) {
  const v = SC.visual, d = SC.dur;
  const wi = eIO(P(t, 0, .45)), wo = eIO(P(t, d - .4, .4));
  const x0 = -1920 * (1 - wi) + 1920 * wo;
  let o = `<rect x="${x0}" y="0" width="1920" height="1080" fill="${C.navy}"/>`;
  o += `<rect x="${x0 - 60}" y="0" width="60" height="1080" fill="${C.teal}"/>`;
  const op = eOut(P(t, .35, .5)) * (1 - eIn(P(t, d - .45, .3)));
  const n = String(v.num).padStart(2, '0');
  let s = text(250, 640, n, 380, {w: 900, fill: 'none'}).replace('fill="none"', `fill="none" stroke="${C.teal}" stroke-width="6"`);
  s += text(850, 450, 'CHAPTER ' + v.num, 36, {w: 800, fill: C.amber, ls: 6});
  const fs = Math.min(86, 86 * 960 / tw(v.title, 86, 'Inter', 850));
  s += text(850, 560, v.title, fs, {w: 850, fill: '#fff'});
  s += `<rect x="850" y="610" width="${eOut(P(t, .6, .7)) * Math.min(960, tw(v.title, fs, 'Inter', 850))}" height="10" rx="5" fill="${C.amber}"/>`;
  const N = (SC.chapters || []).length;
  for (let i = 0; i < N; i++) s += `<rect x="${850 + i * 70}" y="700" width="56" height="10" rx="5" fill="${i + 1 === v.num ? C.teal : 'rgba(255,255,255,.25)'}"/>`;
  o += `<g opacity="${op}" transform="translate(${(1 - eOut(P(t, .35, .6))) * 60},0)">${s}</g>`;
  return o;
}

// ============ OUTRO ============
function sOutro(t) {
  let o = '';
  o += G(t, .2, null, (() => {
    let s = card(820, 200, 940, 300, {r: 30});
    s += text(880, 290, 'GSX Automation', 52, {w: 900});
    const note = SC.visual.note || 'Rules can change: check the latest MoF / FTA notices';
    s += t < cs(1) ? text(880, 340, 'Zoho how-tos for Gulf + Indian businesses', 30, {w: 500, fill: C.mute}) : writeOn(880, 342, note, Math.min(32, fitSize(note, 32, 840, 'Kalam', 700)), P(t, cs(1) + .2, 1.6), {fill: C.coral});
    const clicked = t > at(0, .35);
    const p = eBack(P(t, at(0, .35), .4));
    s += `<g transform="translate(1300,425) scale(${clicked ? .94 + .06 * p : 1})"><rect x="-200" y="-42" width="400" height="84" rx="42" fill="${clicked ? '#e6e8ec' : C.coral}"/>${text(0, 13, clicked ? 'Subscribed ✓' : 'Subscribe', 36, {anchor: 'middle', fill: clicked ? C.ink : '#fff', w: 800})}</g>`;
    const cx = lerp(1700, 1340, eIO(P(t, .8, at(0, .33) - .8))), cy = lerp(700, 440, eIO(P(t, .8, at(0, .33) - .8)));
    if (t < at(0, .6)) s += `<g transform="translate(${cx},${cy})"><path d="M 0 0 L 0 46 L 12 35 L 21 56 L 29 52 L 20 32 L 36 32 Z" fill="#fff" stroke="${C.ink}" stroke-width="4" stroke-linejoin="round"/></g>`;
    if (clicked) { const r = P(t, at(0, .35), .6); s += `<circle cx="1340" cy="440" r="${20 + r * 60}" fill="none" stroke="${C.coral}" stroke-width="5" opacity="${1 - r}"/>`; }
    return s;
  })());
  o += G(t, at(0, .5), null, (() => {
    let s = card(820, 560, 940, 300, {r: 30});
    s += `<rect x="860" y="600" width="380" height="220" rx="18" fill="${C.green}"/>` + text(1050, 700, SC.visual.badge || 'ZATCA', fitSize(SC.visual.badge || 'ZATCA', 64, 340, 'Inter', 900), {anchor: 'middle', fill: '#fff', w: 900}) + text(1050, 760, SC.visual.badge_sub == null ? 'Phase 2' : SC.visual.badge_sub, 40, {anchor: 'middle', fill: '#fff', w: 700});
    s += text(1280, 640, 'NEXT VIDEO', 26, {w: 800, fill: C.coral, ls: 3});
    wrap(SC.visual.next, 40, 440, 'Inter').forEach((l, i) => s += text(1280, 700 + i * 52, l, 40, {w: 800}));
    return s;
  })());
  return o;
}

// ============ PODCAST (HTML layer) ============
let PD = null;
const VP = {x: 60, y: 112, w: 1800, h: 700};
function setupPodcast() {
  const v = SC.visual, H = $('html');
  const screens = [...new Set(v.actions.filter(a => a.screen).map(a => a.screen))];
  let html = `<div class="win" style="left:${VP.x}px;top:${VP.y}px;width:${VP.w}px;height:${VP.h + 46}px"><div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><div class="url">🔒 ${screens[0].split('/')[0]}.zoho.com</div></div>
   <div class="vp" id="vp" style="width:${VP.w}px;height:${VP.h}px">${screens.map((s, i) => `<img id="scr${i}" src="${SC.root}/assets/screens/${SC.screens[s].file}">`).join('')}
   <div id="hl" style="position:absolute;border:4px solid ${C.teal};border-radius:12px;box-shadow:0 0 0 6px rgba(15,157,138,.18);opacity:0"></div>
   <div id="rip" style="position:absolute;border-radius:50%;border:4px solid ${C.sky};opacity:0"></div>
   <div id="dim" style="position:absolute;inset:0;background:rgba(246,242,235,.62);opacity:0"></div>
   <svg id="cur" width="44" height="60" style="position:absolute;left:0;top:0"><path d="M 4 4 L 4 46 L 15 36 L 23 55 L 31 51 L 23 32 L 38 32 Z" fill="#fff" stroke="#1d2433" stroke-width="3.5" stroke-linejoin="round"/></svg></div></div>`;
  html += `<div class="crumbs" id="crumbs" style="left:${VP.x}px;top:${VP.y + VP.h + 64}px">${v.path.map((p, i) => (i ? '<em>›</em>' : '') + `<span>${esc(p)}</span>`).join('')}</div>`;
  html += `<svg id="ov" width="1920" height="1080" style="position:absolute;left:0;top:0"></svg>`;
  H.innerHTML = html;
  // keyframes
  const ks = []; let lastScreen = null;
  v.actions.forEach(a => {
    const tt = cs(a.cue) + (a.at || 0) * cd(a.cue);
    if (a.screen) lastScreen = a.screen;
    if (a.target || a.box) {
      const sc = SC.screens[lastScreen]; const b = a.box || sc.targets[a.target];
      ks.push({t: tt, screen: lastScreen, idx: screens.indexOf(lastScreen), b, z: a.zoom || 1.6, cx: b[0] + b[2] / 2, cy: b[1] + b[3] / 2});
    }
  });
  PD = {screens, ks, overlays: v.actions.filter(a => a.panel || a.status || a.send || a.inbox).map(a => ({...a, t: cs(a.cue) + (a.at || 0) * cd(a.cue)}))};
}
function camAt(t) {
  const {ks} = PD; const sc0 = SC.screens[PD.screens[0]];
  let st = {z: 1, cx: sc0.size[0] / 2, cy: sc0.size[1] / 2, idx: 0};
  for (let i = 0; i < ks.length; i++) {
    const k = ks[i]; if (t < k.t) break;
    const from = (i === 0 || ks[i - 1].idx !== k.idx) ? {z: 1, cx: SC.screens[k.screen].size[0] / 2, cy: SC.screens[k.screen].size[1] / 2} : {z: ks[i - 1].z, cx: ks[i - 1].cx, cy: ks[i - 1].cy};
    const p = eIO(P(t, k.t, 1.2));
    st = {z: lerp(from.z, k.z, p), cx: lerp(from.cx, k.cx, p), cy: lerp(from.cy, k.cy, p), idx: k.idx};
  }
  return st;
}
function xf(st, screen) { // camera -> scale + offset for a screen
  const [iw, ih] = SC.screens[screen].size; const S = VP.w / iw * st.z;
  let ox = VP.w / 2 - st.cx * S, oy = VP.h / 2 - st.cy * S;
  ox = Math.min(0, Math.max(VP.w - iw * S, ox));
  oy = ih * S > VP.h ? Math.min(0, Math.max(VP.h - ih * S, oy)) : (VP.h - ih * S) / 2;
  return {S, ox, oy, map: (x, y) => [ox + x * S, oy + y * S]};
}
function renderPodcast(t) {
  const st = camAt(t), drift = 1 + .015 * Math.sin(t * .25);
  st.z *= drift;
  // screen crossfades
  let active = st.idx;
  PD.screens.forEach((s, i) => {
    const im = $('scr' + i); const f = xf(st, s);
    im.style.transform = `translate(${f.ox}px,${f.oy}px) scale(${f.S})`;
    im.style.width = SC.screens[s].size[0] + 'px';
    let op = i === active ? 1 : 0;
    const k = PD.ks.find(k => k.idx === active && k.t <= t && (PD.ks[PD.ks.indexOf(k) - 1] || {}).idx !== active);
    if (k && t - k.t < .35 && i === active) op = eOut((t - k.t) / .35);
    if (k && t - k.t < .35 && i !== active) op = 1 - eOut((t - k.t) / .35);
    im.style.opacity = op;
  });
  // cursor + highlight
  const f = xf(st, PD.screens[active]);
  let cx = VP.w * .62, cy = VP.h * .8, hlop = 0, hb = null, rip = -1, ripPos = null;
  PD.ks.forEach((k, i) => {
    const prev = i ? PD.ks[i - 1] : null;
    const fk = xf(camAt(t), k.screen);
    const [tx, ty] = fk.map(k.cx, k.cy);
    if (t >= k.t) {
      const p = eIO(P(t, k.t + .2, .9));
      const [px, py] = prev && prev.idx === k.idx ? xf(camAt(t), prev.screen).map(prev.cx, prev.cy) : [VP.w * .62, VP.h * .8];
      cx = lerp(px, tx, p) + Math.sin(p * Math.PI) * -30; cy = lerp(py, ty, p) - Math.sin(p * Math.PI) * 40;
      const tc = k.t + 1.15;
      if (t >= tc) { rip = P(t, tc, .55); ripPos = [tx, ty]; }
      hlop = eOut(P(t, tc, .3)); const [bx, by] = fk.map(k.b[0], k.b[1]); hb = [bx - 6, by - 6, k.b[2] * fk.S + 12, k.b[3] * fk.S + 12];
    }
  });
  const cur = $('cur'); cur.style.transform = `translate(${cx - 4}px,${cy - 4}px)`;
  const press = rip >= 0 && rip < .25 ? .88 : 1; cur.style.transform += ` scale(${press})`;
  const hl = $('hl');
  if (hb) { hl.style.left = hb[0] + 'px'; hl.style.top = hb[1] + 'px'; hl.style.width = hb[2] + 'px'; hl.style.height = hb[3] + 'px'; hl.style.opacity = hlop * (.85 + .15 * Math.sin(t * 5)); } else hl.style.opacity = 0;
  const r = $('rip');
  if (rip >= 0 && rip < 1) { const R = 14 + rip * 46; r.style.left = (ripPos[0] - R) + 'px'; r.style.top = (ripPos[1] - R) + 'px'; r.style.width = r.style.height = 2 * R + 'px'; r.style.opacity = 1 - rip; } else r.style.opacity = 0;
  // breadcrumbs
  const n = SC.visual.path.length;
  document.querySelectorAll('#crumbs span').forEach((sp, i) => { const tt = .3 + i * Math.min(2.2, (SC.dur * .55) / n); sp.className = t > tt ? 'on' : ''; sp.style.opacity = .35 + .65 * eOut(P(t, tt - .3, .4)); });
  // overlays
  let ov = '', dim = 0;
  PD.overlays.forEach((a, ai) => {
    if (t < a.t) return;
    const nx = PD.overlays[ai + 1]; if (nx && t > nx.t + .3) return;
    if (a.panel) { dim = Math.max(dim, eOut(P(t, a.t, .4)));
      const p = eBack(P(t, a.t + .1, .5)), x = 760, y = 260, w = 600, h = 120 + a.panel.items.length * 70;
      let s = card(x, y, w, h, {r: 22}) + text(x + 34, y + 62, a.panel.title, 30, {w: 800});
      a.panel.items.forEach((it, i) => { const tt = a.t + .5 + i * Math.max(.6, (ce(a.cue) - a.t - 1) / a.panel.items.length);
        const on = t > tt; s += `<rect x="${x + 34}" y="${y + 100 + i * 70}" width="38" height="38" rx="10" fill="${on ? C.teal : '#fff'}" stroke="${on ? C.teal : '#c9ced8'}" stroke-width="4"/>` + check(x + 53, y + 119 + i * 70, 22, P(t, tt, .3), '#fff', 6) + text(x + 92, y + 130 + i * 70, it, 28, {w: 650}); });
      ov += `<g transform="translate(${x + w / 2},${y + h / 2}) scale(${p}) translate(${-x - w / 2},${-y - h / 2})">${s}</g>`;
    }
    if (a.send) { dim = Math.max(dim, eOut(P(t, a.t, .4)));
      const y = 440, xs = [230, 560, 900, 1230], lb = ['Invoice', 'Zoho (ASP)', 'Peppol', "Buyer's ASP"], cl = [C.navy, C.teal, C.sky, C.lav];
      xs.forEach((x, i) => { const p = eBack(P(t, a.t + i * .35, .45)); if (p > 0) ov += `<g transform="translate(${x},${y}) scale(${p})">${i === 0 ? `<g transform="scale(.75)">${doc('Send', C.sky)}</g>` : pill(0, 0, lb[i], {anchor: 'middle', fill: cl[i], size: 30})}</g>`;
        if (i) ov += arrow(xs[i - 1] + (i === 1 ? 70 : 110), y, x - 120, y, P(t, a.t + i * .35 - .1, .4), C.ink, 6); });
      const k = eIO(P(t, a.t + 1.4, 1.6)); if (k > 0 && k < 1) ov += `<g transform="translate(${lerp(230, 1230, k)},${y - 90}) scale(.35)">${einv()}</g>`;
      ov += G(t, a.t + 3, null, pill(730, 560, '✓  Pushed', {anchor: 'middle', fill: C.green, size: 30}));
    }
    if (a.status) { dim = Math.max(dim, eOut(P(t, a.t, .4)));
      const cols = ['#8a8f9c', C.amber, C.green, C.red], y = 400; const xs = [250, 640, 1010];
      const gen = a.notes !== undefined;   // generic (any topic): timed on its own line, no UAE extras
      const tms = gen ? [a.t + .3, at(a.cue, .3), at(a.cue, .5), at(a.cue, .72)] : [cs(1) + .1, at(1, .18), at(1, .32), at(1, .55)];
      ov += G(t, a.t, null, card(130, 250, 1240, 420, {r: 24}) + text(170, 315, a.title || 'E-invoice status', 34, {w: 800}));
      a.status.slice(0, 3).forEach((s, i) => { const p = eBack(P(t, tms[i], .45)); if (p > 0) ov += `<g transform="translate(${xs[i]},${y}) scale(${p})">${pill(0, 0, s, {anchor: 'middle', fill: cols[i], size: 28})}</g>`;
        if (i) ov += arrow(xs[i - 1] + 130, y, xs[i] - 140, y, P(t, tms[i] - .1, .35), C.mute, 5); });
      if (!gen) ov += G(t, at(1, .4), null, text(1010, 465, 'UUID  3f9a…c21e', 24, {anchor: 'middle', w: 600, fill: C.mute}));
      const pf = eBack(P(t, tms[3], .45)); if (pf > 0) ov += `<g transform="translate(640,560) scale(${pf})">${pill(0, 0, 'Failed', {anchor: 'middle', fill: cols[3], size: 28})}</g>`;
      ov += writeOn(740, 570, gen ? (a.notes.failed || 'fix the error → push again') : 'fix the error → push again', 32, P(t, tms[3] + .4, 1), {fill: C.red});
      if (!gen) ov += G(t, cs(2), null, pill(1050, 630, 'Pushed = locked → use a credit note', {anchor: 'middle', fill: C.navy, size: 26}));
    }
    if (a.inbox) {
      const p0 = a.t; const vx = VP.x, vy = VP.y + 46;
      for (let i = 0; i < 3; i++) { const tt = p0 + .2 + i * .55; const k = eOut(P(t, tt, .6)); if (k <= 0) continue;
        const y = vy + 170 + i * 92 - (1 - k) * 80;
        ov += `<g opacity="${k}">${card(vx + 380, y, 900, 76, {r: 14})}<g transform="translate(${vx + 430},${y + 38}) scale(.26)">${einv()}</g>${text(vx + 480, y + 48, ['Supplier A  ·  e-invoice', 'Supplier B  ·  e-invoice', 'Supplier C  ·  e-invoice'][i], 28, {w: 650})}${pill(vx + 1120, y + 38, 'DRAFT', {fill: C.amber, size: 22, pad: 16})}</g>`; }
      dim = Math.max(dim, .5 * eOut(P(t, p0, .4)));
    }
  });
  $('dim').style.opacity = dim;
  $('ov').innerHTML = ov;
}

// ============ driver ============
const KIND = {hook: sHook, old_way: sOldWay, five_corner: sFiveCorner, fourteen_days: sFourteen, penalty: sPenalty, celebrate: sCelebrate,
  compare: sCompare, timeline: sTimeline, badge: sBadge, flow: sFlow, formula: sFormula, record: sRecord, checklist: sChecklist, outro: sOutro};
window.setup = function (data) {
  SC = data; $('html').innerHTML = ''; $('svg').innerHTML = '';
  if (SC.type === 'PODCAST') setupPodcast();
  if (SC.type === 'OUTRO') { $('html').innerHTML = `<img id="who" src="${SC.root}/assets/presenter/point_you.png" style="position:absolute;left:120px;bottom:0;height:900px;transform-origin:50% 100%">`; }
  $('chrome').style.display = SC.short ? 'none' : ''; $('cap').style.display = SC.short ? 'none' : '';
  const showChap = SC.type !== 'CHAPTER' && SC.type !== 'HOOK' && SC.chapter > 0;
  $('chap').style.display = showChap ? 'flex' : 'none';
  if (showChap) { $('chap').querySelector('b').textContent = String(SC.chapter).padStart(2, '0'); $('chap').querySelector('span').textContent = SC.chapters[SC.chapter - 1]; }
  const pr = $('prog'); pr.querySelectorAll('s').forEach(x => x.remove());
  (SC.chapterStarts || []).forEach(c => { const s = document.createElement('s'); s.style.left = (100 * c / SC.total) + '%'; pr.appendChild(s); });
  return Promise.all([...document.images].map(i => i.decode().catch(() => 0))).then(() => true);
};
window.render = function (t) {
  _clipId = 0;
  const d = SC.dur, kind = SC.type === 'CHAPTER' ? sChapter : SC.type === 'PODCAST' ? null : KIND[SC.visual.kind];
  const inP = eOut(P(t, 0, .45)), outP = eIn(P(t, d - .32, .32));
  const sceneEl = $('scene');
  if (SC.type === 'CHAPTER') { sceneEl.style.opacity = 1; sceneEl.style.transform = ''; }
  else { sceneEl.style.opacity = (inP * (1 - outP)).toFixed(3); sceneEl.style.transform = `translateY(${((1 - inP) * 22 - outP * 16).toFixed(1)}px)`; }
  if (kind) $('svg').innerHTML = kind(t);
  if (SC.type === 'PODCAST') renderPodcast(t);
  if (SC.type === 'OUTRO') { const w = $('who'); w.style.opacity = eOut(P(t, .2, .6)); w.style.transform = `translateY(${Math.sin(t * 1.1) * 3}px) rotate(${Math.sin(t * .7) * .5}deg)`; }
  // chrome
  const chromeOp = SC.type === 'CHAPTER' ? (1 - eOut(P(t, 0, .4))) + eOut(P(t, d - .4, .4)) : 1;
  $('brand').style.opacity = .85 * clamp(chromeOp); $('chap').style.opacity = clamp(chromeOp);
  $('prog').querySelector('i').style.width = (100 * (SC.start + t) / SC.total) + '%';
  // captions
  const cap = $('cap'); let c = null;
  for (const x of SC.captions) { if (t >= x.s - .05 && t < x.e + .25) c = x; }
  if (c) { if (cap.textContent !== c.text) cap.textContent = c.text; cap.style.opacity = 1; cap.className = SC.type === 'CHAPTER' ? 'dark' : ''; }
  else cap.style.opacity = 0;
  // wait two animation frames so the compositor has fully painted before the screenshot (avoids half-painted frames)
  return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(true))));
};

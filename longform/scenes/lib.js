// Shared drawing library for long-video scenes. Everything is a pure function of time t (deterministic).
const W = 1920, H = 1080;
const C = {ink:'#1d2433', paper:'#f6f2eb', navy:'#13203a', teal:'#0f9d8a', amber:'#f2a33a', coral:'#e4573d', sky:'#3d7fe0',
           mute:'#8a8f9c', line:'#d9d3c7', green:'#1f9d55', red:'#d93b30', white:'#ffffff', board:'#ffffff', lav:'#7a6ff0'};
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, p) => a + (b - a) * p;
const eOut = x => 1 - Math.pow(1 - clamp(x), 3);
const eIn = x => Math.pow(clamp(x), 3);
const eIO = x => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const eBack = x => { x = clamp(x); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const eSpring = x => { x = clamp(x); return 1 - Math.exp(-6 * x) * Math.cos(10 * x); };
const P = (t, s, d) => clamp((t - s) / d);           // progress of t in [s, s+d]
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

// text width (canvas measure with the real font)
const _cv = document.createElement('canvas').getContext('2d');
function tw(text, size, family = 'Inter', weight = 600) { _cv.font = `${weight} ${size}px ${family}`; return _cv.measureText(text).width; }

// ---------- SVG primitives ----------
const STK = `stroke="${C.ink}" stroke-linecap="round" stroke-linejoin="round"`;
function g(inner, tf = '', op = 1) { return op <= 0 ? '' : `<g transform="${tf}" opacity="${op.toFixed(3)}">${inner}</g>`; }
function text(x, y, s, size, o = {}) {
  const fam = o.hand ? 'Kalam' : 'Inter', wt = o.w || (o.hand ? 700 : 700);
  return `<text x="${x}" y="${y}" font-family="${fam}" font-weight="${wt}" font-size="${size}" fill="${o.fill || C.ink}" text-anchor="${o.anchor || 'start'}" ${o.ls ? `letter-spacing="${o.ls}"` : ''} opacity="${o.op == null ? 1 : o.op}">${esc(s)}</text>`;
}
// handwriting reveal: text clipped left->right by progress p
let _clipId = 0;
function writeOn(x, y, s, size, p, o = {}) {
  if (p <= 0) return '';
  const fam = o.hand === false ? 'Inter' : 'Kalam';
  const wdt = tw(s, size, fam, o.w || 700) + 8;
  const id = 'c' + (_clipId++);
  let ax = x; if (o.anchor === 'middle') ax = x - wdt / 2; if (o.anchor === 'end') ax = x - wdt;
  const pen = p < 1 ? `<circle cx="${ax + wdt * eIO(p)}" cy="${y - size * .35}" r="${size * .09}" fill="${o.fill || C.ink}" opacity=".35"/>` : '';
  return `<clipPath id="${id}"><rect x="${ax - 4}" y="${y - size * 1.2}" width="${wdt * eIO(p) + 4}" height="${size * 1.7}"/></clipPath>
    <g clip-path="url(#${id})">${text(x, y, s, size, {...o, hand: o.hand !== false})}</g>${pen}`;
}
// stroke draw-on (pathLength trick)
function draw(d, p, color = C.ink, w = 7, extra = '') {
  if (p <= 0) return '';
  return `<path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - clamp(p)).toFixed(4)}" ${extra}/>`;
}
function check(x, y, s, p, color = C.green, w = 9) { return draw(`M ${x - s * .5} ${y} L ${x - s * .12} ${y + s * .38} L ${x + s * .55} ${y - s * .42}`, p, color, w); }
function cross(x, y, s, p, color = C.red, w = 10) { return draw(`M ${x - s / 2} ${y - s / 2} L ${x + s / 2} ${y + s / 2}`, p * 2, color, w) + draw(`M ${x + s / 2} ${y - s / 2} L ${x - s / 2} ${y + s / 2}`, p * 2 - 1, color, w); }
function shadow(x, y, r, op = .12) { return `<ellipse cx="${x}" cy="${y}" rx="${r}" ry="${r * .18}" fill="#1d2433" opacity="${op}"/>`; }
function card(x, y, w, h, o = {}) {
  return `<rect x="${x}" y="${y + 10}" width="${w}" height="${h}" rx="${o.r || 24}" fill="#1d2433" opacity=".07"/>
          <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${o.r || 24}" fill="${o.fill || '#fff'}" ${o.stroke ? `stroke="${o.stroke}" stroke-width="${o.sw || 4}"` : ''}/>`;
}
function pill(x, y, label, o = {}) {
  const size = o.size || 26, pad = o.pad || 22, w = tw(label, size, 'Inter', 750) + pad * 2, h = size * 1.9;
  const ax = o.anchor === 'middle' ? x - w / 2 : x;
  return `<rect x="${ax}" y="${y - h / 2}" width="${w}" height="${h}" rx="${h / 2}" fill="${o.fill || C.navy}"/>` +
    text(ax + w / 2, y + size * .36, label, size, {anchor: 'middle', fill: o.color || '#fff', w: 750});
}

// ---------- geometric character (circle head, square body, stick limbs, no face) ----------
// pose: stand | walk | carry | point | cheer | worried | shrug | type | run | present
function guy(o) {
  const s = o.s || 1, t = o.t || 0, f = o.face || 1, col = o.color || C.teal;
  const pose = o.pose || 'stand';
  const sp = pose === 'run' ? 13 : 8.5;
  const walking = pose === 'walk' || pose === 'run' || (pose === 'carry' && o.walk);
  const ph = t * sp;
  const bob = walking ? -Math.abs(Math.sin(ph)) * 7 : Math.sin(t * 2.2) * 1.6;
  const jump = pose === 'cheer' ? -Math.abs(Math.sin(t * 6)) * 18 : 0;
  const hipY = -92 + bob + jump;
  const legA = walking ? Math.sin(ph) * (pose === 'run' ? 34 : 25) : 0;
  let out = shadow(0, 2, 62);
  const leg = (dx, a) => { const r = a * Math.PI / 180; const kx = dx + Math.sin(r) * 46, ky = hipY + Math.cos(r) * 46;
    const fx = kx + Math.sin(r * .4) * 46 * (walking ? 1 : 0), fy = Math.min(0, ky + 46);
    return `<path d="M ${dx} ${hipY} L ${kx} ${ky} L ${fx + 10 * f} ${fy}" fill="none" ${STK} stroke-width="11"/>`; };
  out += leg(-16, legA) + leg(16, -legA);
  const bodyTop = hipY - 118, tilt = pose === 'worried' ? -4 : pose === 'run' ? 8 * f : (walking ? 3 * f : 0);
  // arms: angles from straight down, + = forward (direction f)
  let A = [[18, 30], [-18, -10]];
  if (walking) { A = [[-legA * 1.1, 25 - legA * .4], [legA * 1.1, 25 + legA * .4]]; }
  if (pose === 'carry') A = [[62, 105], [55, 100]];
  if (pose === 'point') A = [[100 + Math.sin(t * 3) * 3, 105], [-12, 10]];
  if (pose === 'present') A = [[70, 130 + Math.sin(t * 2.5) * 6], [-15, 10]];
  if (pose === 'cheer') A = [[160 + Math.sin(t * 6) * 8, 170], [-160 - Math.sin(t * 6) * 8, -170]];
  if (pose === 'worried') A = [[150, 230], [-150, -230]];
  if (pose === 'shrug') A = [[60, -40], [-60, 40]];
  if (pose === 'type') A = [[70 + Math.sin(t * 18) * 6, 120], [62 + Math.sin(t * 18 + 1.5) * 6, 118]];
  const arm = (sx, a1, a2, back) => { const r1 = a1 * Math.PI / 180 * f, r2 = a2 * Math.PI / 180 * f;
    const ex = sx + Math.sin(r1) * 48, ey = bodyTop + 26 + Math.cos(r1) * 48, hx = ex + Math.sin(r2) * 44, hy = ey + Math.cos(r2) * 44;
    return {d: `<path d="M ${sx} ${bodyTop + 26} L ${ex} ${ey} L ${hx} ${hy}" fill="none" ${STK} stroke-width="10" opacity="${back ? .9 : 1}"/>`, hx, hy}; };
  const back = arm(-30 * f, A[1][0], A[1][1], true), front = arm(30 * f, A[0][0], A[0][1]);
  let body = back.d;
  body += `<rect x="-48" y="${bodyTop}" width="96" height="120" rx="18" fill="${col}" ${STK} stroke-width="7"/>`;
  body += `<rect x="-48" y="${bodyTop + 78}" width="96" height="10" fill="#000" opacity=".08"/>`; // belt shade
  if (o.tie) body += `<path d="M 0 ${bodyTop + 4} l -9 14 l 9 46 l 9 -46 z" fill="${o.tie}" ${STK} stroke-width="4"/>`;
  const hy = bodyTop - 44 + (pose === 'worried' ? 4 : 0);
  body += `<circle cx="0" cy="${hy}" r="40" fill="#fff" ${STK} stroke-width="7"/>`;
  body += `<path d="M -22 ${hy - 22} q 14 -12 32 -6" fill="none" stroke="#fff" stroke-width="0"/>`;
  body += `<path d="M ${-26 * f} ${hy - 18} a 30 30 0 0 1 ${22 * f} -14" fill="none" stroke="${C.ink}" stroke-width="4" opacity=".18" stroke-linecap="round"/>`;
  if (o.hair) body += `<path d="M -38 ${hy - 6} a 40 40 0 0 1 76 0 q -18 -16 -38 -12 q -22 -2 -38 12 z" fill="${o.hair}" ${STK} stroke-width="5"/>`;
  body += front.d;
  if (o.hold) body += `<g transform="translate(${(front.hx + back.hx) / 2 + 6 * f},${Math.min(front.hy, back.hy) - 10})">${o.hold}</g>`;
  if (pose === 'worried') { const d = (t * 1.3) % 1; body += `<path d="M ${50 * f} ${hy - 30 + d * 34} q 9 15 0 22 q -9 -7 0 -22" fill="${C.sky}" opacity="${(1 - d).toFixed(2)}"/>`; }
  out += `<g transform="rotate(${tilt} 0 ${hipY})">${body}</g>`;
  const x = o.x || 0, y = o.y || 0;
  return `<g transform="translate(${x},${y}) scale(${s})" opacity="${o.op == null ? 1 : o.op}">${out}</g>`;
}

// ---------- props ----------
function doc(label = 'PDF', tagCol = C.red, o = {}) {   // invoice paper, centred at 0,0 (w 120 h 150)
  const w = o.w || 120, h = o.h || 150;
  let s = `<path d="M ${-w / 2} ${-h / 2} h ${w - 30} l 30 30 v ${h - 30} h ${-w} z" fill="#fff" ${STK} stroke-width="6"/>
    <path d="M ${w / 2 - 30} ${-h / 2} v 30 h 30" fill="#eef0f3" ${STK} stroke-width="5"/>`;
  for (let i = 0; i < 4; i++) s += `<line x1="${-w / 2 + 18}" y1="${-h / 2 + 48 + i * 20}" x2="${w / 2 - 22 - (i % 2) * 22}" y2="${-h / 2 + 48 + i * 20}" stroke="${i ? '#c7ccd6' : C.ink}" stroke-width="6" stroke-linecap="round"/>`;
  if (label) s += `<rect x="${-w / 2 - 12}" y="${h / 2 - 46}" width="${tw(label, 22, 'Inter', 800) + 22}" height="34" rx="8" fill="${tagCol}"/>` + text(-w / 2 - 1, h / 2 - 21, label, 22, {fill: '#fff', w: 800});
  return s;
}
function einv(o = {}) { // structured e-invoice: doc + code brackets + green tag
  return doc('e-invoice', C.green, o) + `<text x="18" y="-24" font-family="Inter" font-weight="800" font-size="30" fill="${C.teal}" text-anchor="middle">&lt;/&gt;</text>`;
}
function envelope(s = 1) { return `<g transform="scale(${s})"><rect x="-60" y="-40" width="120" height="80" rx="10" fill="#fff" ${STK} stroke-width="6"/><path d="M -56 -34 L 0 8 L 56 -34" fill="none" ${STK} stroke-width="6"/></g>`; }
function office(x, y, label, col = '#dfe8f3', w = 230, h = 280) {
  let s = `<g transform="translate(${x},${y})">` + shadow(w / 2, h + 4, w * .62, .1) + `<rect x="0" y="0" width="${w}" height="${h}" rx="12" fill="#fff" ${STK} stroke-width="7"/>`;
  for (let r = 0; r < 3; r++) for (let c = 0; c < 2; c++) s += `<rect x="${w * .16 + c * w * .4}" y="${30 + r * 64}" width="${w * .28}" height="40" rx="6" fill="${col}" ${STK} stroke-width="5"/>`;
  s += `<rect x="${w / 2 - 30}" y="${h - 76}" width="60" height="76" rx="6" fill="${C.amber}" ${STK} stroke-width="6"/>`;
  if (label) s += text(w / 2, -22, label, 34, {anchor: 'middle', hand: true});
  return s + '</g>';
}
function gov(x, y, label = 'FTA', s = 1) {
  let o = `<g transform="translate(${x},${y}) scale(${s})">` + shadow(0, 4, 170, .1);
  o += `<path d="M -170 -190 L 0 -270 L 170 -190 Z" fill="#fff" ${STK} stroke-width="7"/>`;
  o += `<rect x="-160" y="-190" width="320" height="22" fill="#e9edf3" ${STK} stroke-width="6"/>`;
  for (let i = 0; i < 5; i++) o += `<rect x="${-138 + i * 64}" y="-160" width="24" height="140" rx="5" fill="#fff" ${STK} stroke-width="6"/>`;
  o += `<rect x="-175" y="-22" width="350" height="22" rx="4" fill="#e9edf3" ${STK} stroke-width="6"/>`;
  o += `<line x1="0" y1="-270" x2="0" y2="-330" ${STK} stroke-width="6"/><path d="M 0 -330 h 46 v 28 h -46" fill="${C.teal}" ${STK} stroke-width="5"/>`;
  if (label) o += text(0, -205, label, 34, {anchor: 'middle', w: 800});
  return o + '</g>';
}
function server(x, y, label, col = C.sky, s = 1, active = 0) {
  let o = `<g transform="translate(${x},${y}) scale(${s})">` + shadow(0, 100, 110, .1);
  for (let i = 0; i < 3; i++) {
    o += `<rect x="-95" y="${-90 + i * 62}" width="190" height="54" rx="12" fill="#fff" ${STK} stroke-width="6"/>`;
    o += `<circle cx="-62" cy="${-63 + i * 62}" r="9" fill="${(active > 0 && (Math.floor(active * 8) + i) % 2) ? C.green : col}"/>`;
    o += `<line x1="-30" y1="${-63 + i * 62}" x2="60" y2="${-63 + i * 62}" stroke="#c7ccd6" stroke-width="7" stroke-linecap="round"/>`;
  }
  if (label) o += text(0, 140, label, 30, {anchor: 'middle', w: 800});
  return o + '</g>';
}
function laptop(x, y, s = 1, screenCol = '#dbe7f7') {
  return `<g transform="translate(${x},${y}) scale(${s})"><rect x="-80" y="-110" width="160" height="104" rx="10" fill="${screenCol}" ${STK} stroke-width="6"/><path d="M -105 -4 h 210 l -14 18 h -182 z" fill="#fff" ${STK} stroke-width="6"/></g>`;
}
function calendarPage(x, y, top, big, sub, s = 1, col = C.coral) {
  return `<g transform="translate(${x},${y}) scale(${s})">` + shadow(0, 150, 150, .1) +
    `<rect x="-150" y="-140" width="300" height="290" rx="26" fill="#fff" ${STK} stroke-width="7"/>
     <path d="M -150 -80 v -34 a 26 26 0 0 1 26 -26 h 248 a 26 26 0 0 1 26 26 v 34 z" fill="${col}" ${STK} stroke-width="7"/>
     <circle cx="-80" cy="-150" r="10" fill="#fff" ${STK} stroke-width="6"/><circle cx="80" cy="-150" r="10" fill="#fff" ${STK} stroke-width="6"/>` +
    text(0, -96, top, 34, {anchor: 'middle', fill: '#fff', w: 800, ls: 2}) + text(0, 50, big, 140, {anchor: 'middle', w: 800}) +
    text(0, 112, sub, 38, {anchor: 'middle', w: 700, fill: C.mute}) + '</g>';
}
function clock(x, y, t, s = 1, speed = 1) {
  const a = t * 200 * speed;
  return `<g transform="translate(${x},${y}) scale(${s})"><circle r="60" fill="#fff" ${STK} stroke-width="7"/>
    ${[0, 1, 2, 3].map(i => `<line x1="0" y1="-48" x2="0" y2="-40" ${STK} stroke-width="6" transform="rotate(${i * 90})"/>`).join('')}
    <line x1="0" y1="0" x2="0" y2="-40" ${STK} stroke-width="7" transform="rotate(${a})"/>
    <line x1="0" y1="0" x2="26" y2="0" stroke="${C.coral}" stroke-width="7" stroke-linecap="round" transform="rotate(${a / 12})"/><circle r="6" fill="${C.ink}"/></g>`;
}
function stamp(x, y, label, p, col = C.red, rot = -12, size = 64) {
  if (p <= 0) return '';
  const sc = p < 1 ? lerp(2.4, 1, eIn(p)) : 1, op = clamp(p * 3);
  const w = tw(label, size, 'Inter', 900) + 60;
  return `<g transform="translate(${x},${y}) rotate(${rot}) scale(${sc})" opacity="${op}">
    <rect x="${-w / 2}" y="${-size * .85}" width="${w}" height="${size * 1.6}" rx="14" fill="none" stroke="${col}" stroke-width="9"/>
    <rect x="${-w / 2 + 10}" y="${-size * .85 + 10}" width="${w - 20}" height="${size * 1.6 - 20}" rx="8" fill="none" stroke="${col}" stroke-width="3"/>
    ${text(0, size * .36, label, size, {anchor: 'middle', fill: col, w: 900, ls: 3})}</g>`;
}
function coin(x, y, s = 1, r = 0) { return `<g transform="translate(${x},${y}) rotate(${r}) scale(${s})"><ellipse rx="30" ry="30" fill="${C.amber}" ${STK} stroke-width="5"/><text y="10" font-family="Inter" font-weight="900" font-size="28" text-anchor="middle" fill="${C.ink}">د.إ</text></g>`; }
function arrow(x1, y1, x2, y2, p, col = C.ink, w = 7, dash = false) {
  if (p <= 0) return '';
  const ex = lerp(x1, x2, eOut(p)), ey = lerp(y1, y2, eOut(p)), a = Math.atan2(y2 - y1, x2 - x1);
  const hd = 20;
  return `<line x1="${x1}" y1="${y1}" x2="${ex}" y2="${ey}" stroke="${col}" stroke-width="${w}" stroke-linecap="round" ${dash ? 'stroke-dasharray="2 18"' : ''}/>` +
    (p > .15 ? `<path d="M ${ex - hd * Math.cos(a - .5)} ${ey - hd * Math.sin(a - .5)} L ${ex} ${ey} L ${ex - hd * Math.cos(a + .5)} ${ey - hd * Math.sin(a + .5)}" fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>` : '');
}
function confetti(t, n = 70, seed = 1, t0 = 0) {
  let o = ''; const cols = [C.teal, C.amber, C.coral, C.sky, C.lav];
  for (let i = 0; i < n; i++) {
    const tt = t - t0 - rnd(i + seed) * .6; if (tt < 0) continue;
    const x = 200 + rnd(i * 3 + seed) * 1520 + Math.sin(tt * 2 + i) * 30, y = -40 + tt * (220 + rnd(i * 7) * 220);
    if (y > 1100) continue;
    o += `<rect x="${x}" y="${y}" width="16" height="9" rx="2" fill="${cols[i % 5]}" transform="rotate(${tt * 260 + i * 40} ${x + 8} ${y + 4})"/>`;
  }
  return o;
}
// whiteboard panel
function board(x = 120, y = 120, w = 1680, h = 760) {
  return `<rect x="${x}" y="${y + 14}" width="${w}" height="${h}" rx="30" fill="#1d2433" opacity=".07"/>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="30" fill="#fff"/>
    <rect x="${x + 2}" y="${y + 2}" width="${w - 4}" height="${h - 4}" rx="28" fill="none" stroke="#ece6dc" stroke-width="3"/>`;
}
function underline(x, y, w, p, col = C.amber) { return draw(`M ${x} ${y} q ${w * .5} -10 ${w} 2`, p, col, 9); }
function ring(x, y, rx, ry, p, col = C.coral) { return draw(`M ${x + rx} ${y} a ${rx} ${ry} 0 1 1 -2 -6`, p, col, 7); }

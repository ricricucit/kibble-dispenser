// Live 3D assembly of the kibble dispenser, built from hardware/assembly/assembly.json.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { builders } from './primitives.js';

const DEG = Math.PI / 180;
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const darkScheme = window.matchMedia('(prefers-color-scheme: dark)');
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const HOME = { az: -116 * DEG, el: 23 * DEG };

function cssColour(el, name, fallback) {
  const v = getComputedStyle(el).getPropertyValue(name).trim();
  return new THREE.Color(v || fallback);
}

export class Viewer extends EventTarget {
  constructor({ stage, canvas, overlay, data, base = '' }) {
    super();
    this.stage = stage;
    this.canvas = canvas;
    this.overlay = overlay;
    this.data = data;
    this.base = base;
    this.L = data.layout;
    [this.sx, this.sy] = data.shaft_axis_xy;
    this.openDir = this.L.disc_v3.open_dir_deg ?? 180;
    this.state = { explode: 0, section: false, servo: 0, isolated: null, callouts: true };
    this.items = [];
    this.insets = { left: 0, right: 0, top: 0, bottom: 0 };
    this.clipPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -this.sy);   // keeps y >= shaft axis
    this.clipMats = [];
    this.lineMats = [];
    this.hatchMats = [];
    this.anims = new Set();
    this.dirty = true;
    this.hovered = null;
    this._initRenderer();
    this._initScene();
    this._initControls();
    this._initPointer();
    this._buildContext();
    this._initKibble();
    this._initCallouts();
    this._resize();
    this.frame({ animate: false, home: true });
    this._observe();
    this._loop = this._loop.bind(this);
    this._start();
  }

  /* ---------- setup ---------- */
  _initRenderer() {
    const r = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    r.setClearColor(0x000000, 0);
    r.localClippingEnabled = true;
    r.shadowMap.enabled = true;
    r.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer = r;
    this.hatch = { value: 6 * r.getPixelRatio() };
  }

  _initScene() {
    const scene = new THREE.Scene();
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    scene.environment = pmrem.fromScene(new RoomEnvironment(this.renderer), 0.04).texture;
    pmrem.dispose();
    const key = new THREE.DirectionalLight(0xffffff, 1.7);
    key.position.set(-160, -260, 520);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    Object.assign(key.shadow.camera, { left: -420, right: 420, top: 420, bottom: -420, near: 10, far: 1600 });
    key.shadow.bias = -0.0004;
    key.shadow.radius = 4;
    scene.add(key, key.target);
    this.key = key;
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f94, 0.6));
    this.ground = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.ShadowMaterial({ opacity: 0.16 }));
    this.ground.receiveShadow = true;
    scene.add(this.ground);
    this.camera = new THREE.PerspectiveCamera(30, 1, 5, 12000);
    this.camera.up.set(0, 0, 1);
    this.scene = scene;
    this._sectionFrame();
    this._readTheme();
  }

  _initControls() {
    const c = new OrbitControls(this.camera, this.canvas);
    c.enableDamping = !reducedMotion.matches;
    c.dampingFactor = 0.09;
    c.screenSpacePanning = true;
    c.minDistance = 60;
    c.maxDistance = 4000;
    c.rotateSpeed = 0.8;
    c.addEventListener('change', () => { this.dirty = true; });
    c.addEventListener('start', () => this.dispatchEvent(new Event('interact')));
    c.listenToKeyEvents(this.stage);
    this.controls = c;
  }

  _readTheme() {
    const el = document.documentElement;
    this.inkColour = cssColour(el, '--ink', '#16232b');
    this.accentColour = cssColour(el, '--orange', '#ee6a1f');
    for (const m of this.lineMats) m.color.copy(this.inkColour);
    if (this.sectionLine) this.sectionLine.material.color.copy(this.accentColour);
    this.ground.material.opacity = darkScheme.matches ? 0.35 : 0.16;
    this.dirty = true;
  }

  /* ---------- materials ---------- */
  _clip(m, item) {
    if (item.clip) { this.clipMats.push(m); m.clippingPlanes = this.state.section ? [this.clipPlane] : null; }
    return m;
  }

  _capMaterial(colour, item) {
    const base = new THREE.Color(colour);
    const hsl = {}; base.getHSL(hsl);
    const fill = base.clone().lerp(new THREE.Color('#ffffff'), hsl.l < 0.25 ? 0.18 : 0.12);
    const line = hsl.l < 0.25 ? base.clone().lerp(new THREE.Color('#ffffff'), 0.55) : base.clone().multiplyScalar(0.45);
    const m = new THREE.MeshBasicMaterial({ color: fill, side: THREE.BackSide });
    const uniforms = { uHatch: this.hatch, uLine: { value: line } };
    m.onBeforeCompile = (s) => {
      Object.assign(s.uniforms, uniforms);
      s.fragmentShader = 'uniform float uHatch;\nuniform vec3 uLine;\n' + s.fragmentShader.replace(
        '#include <dithering_fragment>',
        `#include <dithering_fragment>
        float hv = mod(gl_FragCoord.x + gl_FragCoord.y, uHatch);
        gl_FragColor.rgb = mix(gl_FragColor.rgb, uLine, 1.0 - smoothstep(0.9, 1.9, hv));`);
    };
    m.customProgramCacheKey = () => 'hatch-cap';
    return this._clip(m, item);
  }

  _edges(group, geo, item, { dashed = false, opacity = 0.5, angle = 28 } = {}) {
    const g = new THREE.EdgesGeometry(geo, angle);
    const m = dashed
      ? new THREE.LineDashedMaterial({ color: this.inkColour, dashSize: 4, gapSize: 3, transparent: true, opacity, depthWrite: false })
      : new THREE.LineBasicMaterial({ color: this.inkColour, transparent: true, opacity, depthWrite: false });
    this.lineMats.push(m);
    const lines = new THREE.LineSegments(g, this._clip(m, item));
    if (dashed) lines.computeLineDistances();
    lines.renderOrder = 3;
    group.add(lines);
    return lines;
  }

  _kit(item) {
    return {
      solid: (group, geo, colour, opts = {}) => {
        const front = this._clip(new THREE.MeshStandardMaterial({
          color: colour, roughness: opts.roughness ?? 0.42, metalness: opts.metalness ?? 0,
          envMapIntensity: 0.75, side: opts.cap === false ? THREE.DoubleSide : THREE.FrontSide,
        }), item);
        front.clipShadows = true;
        const mesh = new THREE.Mesh(geo, front);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.userData.item = item;
        group.add(mesh);
        if (!opts.decor) item.meshes.push(mesh);   // decor (cables) is not used for picking or framing
        item.fronts.push(front);
        if (opts.cap !== false) group.add(new THREE.Mesh(geo, this._capMaterial(colour, item)));
        if (opts.edges !== false && opts.cap !== false) this._edges(group, geo, item, { opacity: opts.edgeOpacity ?? 0.38 });
        return mesh;
      },
      ghost: (group, geo, colour, opacity, opts = {}) => {
        const m = this._clip(new THREE.MeshStandardMaterial({
          color: colour, roughness: 0.35, metalness: 0, transparent: true, opacity,
          depthWrite: false, side: THREE.DoubleSide, envMapIntensity: 0.6,
        }), item);
        const mesh = new THREE.Mesh(geo, m);
        mesh.renderOrder = 2;
        mesh.userData.item = item;
        group.add(mesh);
        item.meshes.push(mesh);
        item.fronts.push(m);
        this._edges(group, geo, item, { dashed: !!opts.dashed, opacity: opts.dashed ? 0.55 : 0.32 });
        return mesh;
      },
      outline: (group, geo) => this._edges(group, geo, item, { opacity: 0.5 }),
    };
  }

  /* ---------- parts ---------- */
  _newItem(src, kind) {
    const item = {
      id: src.id, name: src.name, bom: src.bom, kind, src,
      ghost: kind === 'context' && (src.opacity ?? 1) < 1,
      clip: src.id !== 'scivolo_v1',   // keep the chute whole in the section view
      explode: new THREE.Vector3().fromArray(src.explode || [0, 0, 0]),
      root: new THREE.Group(), fixed: null, pivot: null, meshes: [], fronts: [], loaded: kind === 'context',
    };
    item.root.name = src.id;
    this.scene.add(item.root);
    this.items.push(item);
    return item;
  }

  _buildContext() {
    for (const src of this.data.context || []) {
      const b = builders[src.kind];
      if (!b) { console.warn('No shape for', src.id); continue; }
      const item = this._newItem(src, 'context');
      const { moving, fixed } = b(src, this.L, this._kit(item));
      item.root.add(moving);
      if (fixed) { item.fixed = fixed; this.scene.add(fixed); }
    }
  }

  async loadParts() {
    const parts = this.data.parts || [];
    const loader = new STLLoader();
    let done = 0;
    const total = parts.length;
    this.dispatchEvent(new CustomEvent('progress', { detail: { done, total } }));
    const failed = [];
    await Promise.all(parts.map(async (src) => {
      const item = this._newItem(src, 'printed');
      try {
        const res = await fetch(this.base + src.file);
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
        const geo = loader.parse(await res.arrayBuffer());
        geo.computeBoundingBox();
        let holder = item.root;
        if (src.frame === 'axis') {
          const axis = new THREE.Group();
          axis.position.set(this.sx, this.sy, 0);
          item.root.add(axis);
          holder = axis;
          if (src.spins) item.pivot = axis;
        }
        this._kit(item).solid(holder, geo, src.colour, { roughness: 0.38, edgeOpacity: 0.3 });
        item.loaded = true;
      } catch (err) {
        console.warn(`Could not load ${src.file}:`, err);
        failed.push(src.file);
      }
      done += 1;
      this.dispatchEvent(new CustomEvent('progress', { detail: { done, total } }));
    }));
    this.items.sort((a, b) => (a.bom ?? 99) - (b.bom ?? 99));
    this._applyAll();
    this._buildCallouts();
    this.frame({ animate: false, home: true });
    this.dispatchEvent(new CustomEvent('ready', { detail: { failed } }));
  }

  item(id) { return this.items.find((i) => i.id === id); }

  /* ---------- state ---------- */
  _emit() { this.dispatchEvent(new CustomEvent('state', { detail: { ...this.state } })); }

  _applyAll() {
    this._applyExplode();
    this._applyServo();
    this._applyVisibility();
    this._applySection();
  }

  _applyExplode() {
    const t = this.state.explode;
    for (const it of this.items) it.root.position.copy(it.explode).multiplyScalar(t);
    const box = this.item('box');
    const z0 = this.L.box.outer_z[0] + (box ? box.explode.z * t : 0);
    this.ground.position.z = z0 - 0.6;
    this.key.target.position.set(-40, -40, z0);
    this.kibble.visible = this.kibble.userData.active && t < 0.01 && !this.state.isolated;
    this._updateSectionFrame();
    this.dirty = true;
  }

  _applyServo() {
    const a = (this.openDir - 270 + this.state.servo) * DEG;
    for (const it of this.items) if (it.pivot) it.pivot.rotation.z = a;
    this.dirty = true;
  }

  _applyVisibility() {
    const iso = this.state.isolated;
    for (const it of this.items) {
      const v = !iso || it.id === iso;
      it.root.visible = v;
      if (it.fixed) it.fixed.visible = v;
    }
    this.kibble.visible = this.kibble.userData.active && this.state.explode < 0.01 && !iso;
    this._updateSectionFrame();
    this.dirty = true;
  }

  _applySection() {
    const on = this.state.section;
    for (const m of this.clipMats) { m.clippingPlanes = on ? [this.clipPlane] : null; m.needsUpdate = true; }
    this.sectionLine.visible = on;
    this._updateSectionFrame();
    this.dirty = true;
  }

  setExplode(t, { animate = false, refit = false } = {}) {
    t = Math.min(1, Math.max(0, t));
    if (refit) this.frame({ explode: t });
    if (animate && !reducedMotion.matches) {
      const from = this.state.explode;
      return this._animate('explode', 650, (k) => { this.state.explode = from + (t - from) * k; this._applyExplode(); this._emit(); });
    }
    this.state.explode = t;
    this._applyExplode();
    this._emit();
    return Promise.resolve();
  }

  setServo(deg, { animate = false, duration = 900 } = {}) {
    deg = Math.min(180, Math.max(0, deg));
    if (animate && !reducedMotion.matches) {
      const from = this.state.servo;
      return this._animate('servo', duration, (k) => { this.state.servo = from + (deg - from) * k; this._applyServo(); this._emit(); });
    }
    this.state.servo = deg;
    this._applyServo();
    this._emit();
    return Promise.resolve();
  }

  setSection(on) { this.state.section = !!on; this._applySection(); this._emit(); }

  setCallouts(on) { this.state.callouts = !!on; this.overlay.hidden = !on; this.dirty = true; this._emit(); }

  isolate(id) {
    const it = id ? this.item(id) : null;
    this.state.isolated = it ? it.id : null;
    this._setHover(null);
    this._applyVisibility();
    this._emit();
    this.frame();
  }

  reset() {
    this.anims.clear();
    this.state = { ...this.state, explode: 0, section: false, servo: 0, isolated: null };
    this.kibble.userData.active = false;
    this._applyAll();
    this._emit();
    this.frame({ home: true });
  }

  focus(ids) { this.frame({ ids, margin: 1.8 }); }

  setInsets(ins) { this.insets = { ...this.insets, ...ins }; this._resize(); }

  /* ---------- camera ---------- */
  _bounds(explode = this.state.explode, ids = null) {
    const box = new THREE.Box3();
    const saved = this.state.explode;
    if (explode !== saved) { this.state.explode = explode; this._applyExplode(); }
    this.scene.updateMatrixWorld(true);
    for (const it of this.items) {
      if (!it.root.visible || (ids && !ids.includes(it.id))) continue;
      for (const m of it.meshes) box.expandByObject(m);
    }
    if (explode !== saved) { this.state.explode = saved; this._applyExplode(); this.scene.updateMatrixWorld(true); }
    if (box.isEmpty()) box.setFromCenterAndSize(new THREE.Vector3(this.sx, this.sy, 0), new THREE.Vector3(200, 200, 200));
    return box;
  }

  frame({ animate = true, home = false, explode, ids = null, margin = 1.06 } = {}) {
    const box = this._bounds(explode, ids);
    const c = box.getCenter(new THREE.Vector3());
    let dir;
    if (home) margin = Math.min(margin, 0.94);
    if (home) dir = new THREE.Vector3(Math.cos(HOME.el) * Math.cos(HOME.az), Math.cos(HOME.el) * Math.sin(HOME.az), Math.sin(HOME.el));
    else dir = this.camera.position.clone().sub(this.controls.target).normalize();
    // exact fit of the 8 box corners in the free part of the canvas
    const up = new THREE.Vector3(0, 0, 1);
    const right = new THREE.Vector3().crossVectors(up, dir).normalize();
    if (right.lengthSq() < 1e-6) right.set(1, 0, 0);
    const camUp = new THREE.Vector3().crossVectors(dir, right).normalize();
    const { w, h } = this._free();
    const tanV = Math.tan(this.camera.fov * DEG / 2) * (h / Math.max(1, this.H));
    const tanH = tanV * (w / Math.max(1, h));
    let dist = 0;
    const p = new THREE.Vector3();
    for (let i = 0; i < 8; i++) {
      p.set(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z).sub(c);
      const depth = p.dot(dir);
      dist = Math.max(dist, Math.abs(p.dot(right)) / tanH + depth, Math.abs(p.dot(camUp)) / tanV + depth);
    }
    dist = Math.max(dist * margin, this.controls.minDistance * 1.2);
    const pos = c.clone().addScaledVector(dir, dist);
    this.controls.maxDistance = Math.max(4000, dist * 3);
    if (!animate || reducedMotion.matches) {
      this.camera.position.copy(pos);
      this.controls.target.copy(c);
      this.controls.update();
      this.dirty = true;
      return;
    }
    const p0 = this.camera.position.clone(), t0 = this.controls.target.clone();
    this._animate('camera', 700, (k) => {
      this.camera.position.lerpVectors(p0, pos, k);
      this.controls.target.lerpVectors(t0, c, k);
      this.controls.update();
    });
  }

  _free() {
    const i = this.insets;
    return { w: Math.max(80, this.W - i.left - i.right), h: Math.max(80, this.H - i.top - i.bottom) };
  }

  _resize() {
    const r = this.canvas.parentElement.getBoundingClientRect();
    this.W = Math.max(1, Math.round(r.width));
    this.H = Math.max(1, Math.round(r.height));
    this.renderer.setSize(this.W, this.H, false);
    this.camera.aspect = this.W / this.H;
    const i = this.insets;
    // shift the projection centre into the free part of the canvas (between the overlay panels)
    this.camera.setViewOffset(this.W, this.H, -(i.left - i.right) / 2, -(i.top - i.bottom) / 2, this.W, this.H);
    this.camera.updateProjectionMatrix();
    this.dirty = true;
  }

  /* ---------- section plane outline ---------- */
  _sectionFrame() {
    const g = new THREE.BufferGeometry().setFromPoints([0, 1, 2, 3, 4].map(() => new THREE.Vector3()));
    const m = new THREE.LineDashedMaterial({ color: 0xee6a1f, dashSize: 8, gapSize: 5, transparent: true, opacity: 0.9, depthWrite: false });
    this.sectionLine = new THREE.Line(g, m);
    this.sectionLine.visible = false;
    this.sectionLine.renderOrder = 4;
    this.scene.add(this.sectionLine);
  }

  _updateSectionFrame() {
    if (!this.sectionLine || !this.sectionLine.visible || !this.items.length) return;
    const b = this._boundsNow();
    const y = this.sy - 0.2, m = 14;
    const pts = [[b.min.x - m, b.min.z - m], [b.max.x + m, b.min.z - m], [b.max.x + m, b.max.z + m], [b.min.x - m, b.max.z + m], [b.min.x - m, b.min.z - m]];
    const pos = this.sectionLine.geometry.attributes.position;
    pts.forEach(([x, z], k) => pos.setXYZ(k, x, y, z));
    pos.needsUpdate = true;
    this.sectionLine.geometry.computeBoundingSphere();
    this.sectionLine.computeLineDistances();
  }

  _boundsNow() {
    const box = new THREE.Box3();
    this.scene.updateMatrixWorld(true);
    for (const it of this.items) if (it.root.visible && it.clip) for (const m of it.meshes) box.expandByObject(m);
    return box.isEmpty() ? new THREE.Box3(new THREE.Vector3(-1, -1, -1), new THREE.Vector3(1, 1, 1)) : box;
  }

  /* ---------- kibble run ---------- */
  _initKibble() {
    const g = new THREE.Group();
    g.visible = false;
    g.userData.active = false;
    const geo = new THREE.SphereGeometry(4.2, 14, 10);
    geo.scale(1, 0.85, 0.6);
    const mat = new THREE.MeshStandardMaterial({ color: 0x9a5b2a, roughness: 0.8 });
    this.kibblePieces = [];
    for (let i = 0; i < 9; i++) {
      const m = new THREE.Mesh(geo, mat);
      m.castShadow = true;
      m.visible = false;
      m.rotation.set(Math.random() * 3, Math.random() * 3, Math.random() * 3);
      g.add(m);
      this.kibblePieces.push({ m, jx: (Math.random() - 0.5) * 12, jy: (Math.random() - 0.5) * 12, delay: i * 0.07 });
    }
    this.kibble = g;
    this.scene.add(g);
    // path: through the disc opening at 180°, onto the bowl floor, along the chute floor and out
    const a = this.openDir * DEG, r = 26;
    const ox = this.sx + Math.cos(a) * r, oy = this.sy + Math.sin(a) * r;
    const chute = (this.L.chute.path || []).map((p) => new THREE.Vector3(...p));
    const pts = [new THREE.Vector3(ox, oy, 48), new THREE.Vector3(ox, oy, 7), ...chute];
    if (chute.length) { const last = chute[chute.length - 1]; pts.push(last.clone().add(new THREE.Vector3(0, -14, -46))); }
    this.kibblePath = new THREE.CatmullRomCurve3(pts, false, 'centripetal');
  }

  async dispense() {
    if (this.busy) return;
    this.busy = true;
    this.dispatchEvent(new Event('busy'));
    try {
      if (this.state.isolated) this.isolate(null);
      if (this.state.explode > 0) await this.setExplode(0, { animate: true, refit: true });
      if (reducedMotion.matches) { await this.setServo(this.state.servo > 90 ? 0 : 180); return; }
      await this.setServo(180, { animate: true, duration: 800 });
      this.kibble.userData.active = true;
      this.kibble.visible = true;
      await this._animate('kibble', 1900, (k) => {
        const T = k * 1.9;
        for (const p of this.kibblePieces) {
          const u = Math.min(1, Math.max(0, (T - p.delay) / 1.25));
          p.m.visible = u > 0 && u < 1;
          const q = this.kibblePath.getPointAt(Math.pow(u, 1.35));
          p.m.position.set(q.x + p.jx * (1 - u * 0.7), q.y + p.jy * 0.4, q.z + 3);
          p.m.rotation.x += 0.12;
        }
      }, (t) => t);
      this.kibble.userData.active = false;
      this.kibble.visible = false;
      await this.setServo(0, { animate: true, duration: 800 });
    } finally {
      this.busy = false;
      this.dispatchEvent(new Event('idle'));
    }
  }

  /* ---------- animation ---------- */
  _animate(name, ms, fn, curve = ease) {
    for (const a of this.anims) if (a.name === name) { this.anims.delete(a); a.resolve(); }
    return new Promise((resolve) => {
      const t0 = performance.now();
      this.anims.add({ name, resolve, step: (now) => { const k = Math.min(1, (now - t0) / ms); fn(curve(k)); return k < 1; } });
      this._start();
    });
  }

  _observe() {
    this.visible = true;
    new ResizeObserver(() => this._resize()).observe(this.canvas.parentElement);
    new IntersectionObserver(([e]) => { this.visible = e.isIntersecting; if (this.visible) this._start(); }).observe(this.stage);
    document.addEventListener('visibilitychange', () => { if (!document.hidden) this._start(); });
    darkScheme.addEventListener('change', () => this._readTheme());
    reducedMotion.addEventListener('change', () => { this.controls.enableDamping = !reducedMotion.matches; });
  }

  _start() { if (!this.raf) this.raf = requestAnimationFrame(this._loop); }

  _loop(now) {
    this.raf = 0;
    if (document.hidden || !this.visible) return;
    let changed = this.controls.update();
    for (const a of [...this.anims]) {
      changed = true;
      if (!a.step(now)) { this.anims.delete(a); a.resolve(); }
    }
    if (changed || this.dirty) {
      this.dirty = false;
      this.renderer.render(this.scene, this.camera);
      this._updateCallouts();
    }
    this.raf = requestAnimationFrame(this._loop);
  }

  /* ---------- picking and hover ---------- */
  _initPointer() {
    const ray = new THREE.Raycaster();
    const ndc = new THREE.Vector2();
    let down = null, pending = null;
    const pick = (e) => {
      const r = this.canvas.getBoundingClientRect();
      ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(ndc, this.camera);
      const meshes = this.items.filter((i) => i.root.visible).flatMap((i) => i.meshes);
      let ghost = null;
      for (const h of ray.intersectObjects(meshes, false)) {
        const it = h.object.userData.item;
        if (this.state.section && it.clip && h.point.y < this.sy - 0.05) continue;
        if (!it.ghost) return it;
        ghost = ghost || it;
      }
      return ghost;
    };
    this.canvas.addEventListener('pointerdown', (e) => { down = { x: e.clientX, y: e.clientY, t: performance.now() }; });
    this.canvas.addEventListener('pointerup', (e) => {
      if (!down) return;
      const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y);
      if (moved < 5 && performance.now() - down.t < 600) {
        const it = pick(e);
        this.dispatchEvent(new CustomEvent('pick', { detail: { id: it ? it.id : null } }));
      }
      down = null;
    });
    this.canvas.addEventListener('pointermove', (e) => {
      if (e.pointerType !== 'mouse' || e.buttons) { if (this.hovered) this._setHover(null); return; }
      if (pending) { pending = e; return; }
      pending = e;
      requestAnimationFrame(() => {
        const ev = pending; pending = null;
        const it = pick(ev);
        this._setHover(it);
        const r = this.stage.getBoundingClientRect();
        this.dispatchEvent(new CustomEvent('hover', { detail: { id: it ? it.id : null, name: it ? it.name : '', x: ev.clientX - r.left, y: ev.clientY - r.top } }));
      });
    });
    this.canvas.addEventListener('pointerleave', () => {
      this._setHover(null);
      this.dispatchEvent(new CustomEvent('hover', { detail: { id: null } }));
    });
  }

  _setHover(it) {
    if (this.hovered === it) return;
    if (this.hovered) for (const m of this.hovered.fronts) m.emissive.setHex(0x000000);
    this.hovered = it;
    if (it) for (const m of it.fronts) m.emissive.setHex(0x5c2a06);
    this.canvas.style.cursor = it ? 'pointer' : '';
    this.dirty = true;
  }

  /* ---------- BOM balloons ---------- */
  _initCallouts() {
    this.overlay.innerHTML = '<svg class="leaders" aria-hidden="true"><defs><marker id="leader-dot" viewBox="0 0 6 6" '
      + 'refX="3" refY="3" markerWidth="6" markerHeight="6" markerUnits="userSpaceOnUse"><circle cx="3" cy="3" r="2.4"/></marker></defs></svg>';
    this.leaderSvg = this.overlay.firstChild;
    this.balloons = [];
  }

  _buildCallouts() {
    this.overlay.querySelectorAll('.balloon').forEach((b) => b.remove());
    this.balloons = this.items.map((it) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'balloon';
      b.tabIndex = -1;
      b.textContent = it.bom;
      b.title = it.name;
      b.setAttribute('aria-hidden', 'true');
      b.addEventListener('click', () => this.dispatchEvent(new CustomEvent('pick', { detail: { id: it.id } })));
      this.overlay.append(b);
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      line.setAttribute('marker-end', 'url(#leader-dot)');
      this.leaderSvg.append(line);
      return { it, b, line, side: 0, fixedSide: false };
    });
    this.dirty = true;
  }

  _updateCallouts() {
    if (!this.state.callouts || !this.balloons.length) return;
    const W = this.W, H = this.H, ins = this.insets;
    const v = new THREE.Vector3();
    const proj = (x, y, z) => { v.set(x, y, z).project(this.camera); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H, v.z]; };
    let minX = Infinity, maxX = -Infinity;
    const rows = [];
    for (const bl of this.balloons) {
      const it = bl.it;
      const box = new THREE.Box3();
      if (it.root.visible) for (const m of it.meshes) box.expandByObject(m);
      if (box.isEmpty()) { bl.b.hidden = true; bl.line.setAttribute('d', ''); continue; }
      if (this.state.section && it.clip) box.min.y = Math.max(box.min.y, this.sy);
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, behind = false;
      for (let i = 0; i < 8; i++) {
        const [px, py, pz] = proj(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z);
        if (pz > 1) behind = true;
        x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py);
      }
      if (behind) { bl.b.hidden = true; bl.line.setAttribute('d', ''); continue; }
      minX = Math.min(minX, x0); maxX = Math.max(maxX, x1);
      rows.push({ bl, x0, x1, ay: (y0 + y1) / 2 });
    }
    // parts left of the model's centre get a balloon in the left column, and so on;
    // parts near the centre keep their side (or balance the columns the first time)
    const mx = (minX + maxX) / 2, mw = Math.max(1, maxX - minX);
    let nl = 0, nr = 0;
    rows.sort((a, b) => a.ay - b.ay);
    for (const r of rows) {
      const d = ((r.x0 + r.x1) / 2 - mx) / mw;
      if (d < -0.14) r.bl.side = -1; else if (d > 0.14) r.bl.side = 1; else if (!r.bl.fixedSide) r.bl.side = 0;
      if (r.bl.side < 0) nl++; else if (r.bl.side > 0) nr++;
    }
    for (const r of rows) {
      if (!r.bl.side) { r.bl.side = nl <= nr ? -1 : 1; if (r.bl.side < 0) nl++; else nr++; }
      r.bl.fixedSide = true;
      r.ax = r.bl.side < 0 ? r.x0 + (r.x1 - r.x0) * 0.22 : r.x1 - (r.x1 - r.x0) * 0.22;
    }
    const pad = 22, gap = 34;
    const colL = Math.max(ins.left + pad, minX - 46), colR = Math.min(W - ins.right - pad, maxX + 46);
    for (const side of [-1, 1]) {
      const col = rows.filter((r) => r.bl.side === side).sort((a, b) => a.ay - b.ay);
      const top = ins.top + pad, bottom = H - ins.bottom - pad;
      col.forEach((r, i) => { r.by = Math.max(r.ay, i ? col[i - 1].by + gap : top); });
      for (let i = col.length - 1; i >= 0; i--) col[i].by = Math.min(col[i].by, i < col.length - 1 ? col[i + 1].by - gap : bottom);
      for (const r of col) {
        const bx = side < 0 ? colL : colR;
        r.bl.b.hidden = false;
        r.bl.b.style.transform = `translate(${bx.toFixed(1)}px, ${r.by.toFixed(1)}px) translate(-50%, -50%)`;
        const ex = bx - side * 13;
        r.bl.line.setAttribute('d', `M${ex.toFixed(1)} ${r.by.toFixed(1)}L${r.ax.toFixed(1)} ${r.ay.toFixed(1)}`);
      }
    }
    this.leaderSvg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  }
}

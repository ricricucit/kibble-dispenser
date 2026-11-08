// Simple shapes for the parts that are bought, reused or not designed yet.
// All numbers come from assembly.json "layout" (Z-up, mm, Z=0 = top face of the lid).
import * as THREE from 'three';

const TAU = Math.PI * 2;
const DEG = Math.PI / 180;

export function boxGeo(x0, x1, y0, y1, z0, z1) {
  const g = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0);
  g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  return g;
}

// Cylinder or frustum along +Z. rTop is the radius at z1.
export function cylGeo(rBottom, rTop, z0, z1, seg = 64, open = false) {
  const g = new THREE.CylinderGeometry(rTop, rBottom, z1 - z0, seg, 1, open);
  g.rotateX(Math.PI / 2);
  g.translate(0, 0, (z0 + z1) / 2);
  return g;
}

function extrude(shape, z0, z1, curveSegments = 64) {
  const g = new THREE.ExtrudeGeometry(shape, { depth: z1 - z0, bevelEnabled: false, curveSegments });
  g.translate(0, 0, z0);
  return g;
}

// Closed annular sector between radii r0 and r1, from angle a0 to a1 (radians, counter-clockwise).
function sectorShape(cx, cy, r0, r1, a0, a1) {
  const s = new THREE.Shape();
  s.moveTo(cx + Math.cos(a0) * r1, cy + Math.sin(a0) * r1);
  s.absarc(cx, cy, r1, a0, a1, false);
  s.lineTo(cx + Math.cos(a1) * r0, cy + Math.sin(a1) * r0);
  s.absarc(cx, cy, r0, a1, a0, true);
  s.closePath();
  return s;
}

function ringShape(cx, cy, r0, r1) {
  const s = new THREE.Shape();
  s.absarc(cx, cy, r1, 0, TAU, false);
  const h = new THREE.Path();
  h.absarc(cx, cy, r0, 0, TAU, true);
  s.holes.push(h);
  return s;
}

// kit = { solid(group, geo, colour, opts), ghost(group, geo, colour, opacity, opts) }
// Each builder returns { moving, fixed }: "fixed" stays put in the exploded view.
export const builders = {
  box(item, L, kit) {
    const B = L.box, [sx, sy] = L.shaft_axis_xy;
    const [x0, x1] = B.outer_x, [y0, y1] = B.outer_y, [zb, zt] = B.outer_z;
    const w = B.wall, sk = B.lid_skirt, lt = B.lid_plate_t ?? w, zs = zt - sk;
    const moving = new THREE.Group(), fixed = new THREE.Group();
    const c = item.colour, o = item.opacity;
    // base: floor and four walls, open at the top
    kit.ghost(moving, boxGeo(x0, x1, y0, y1, zb, zb + w), c, o);
    kit.ghost(moving, boxGeo(x0, x0 + w, y0, y1, zb + w, zs), c, o);
    kit.ghost(moving, boxGeo(x1 - w, x1, y0, y1, zb + w, zs), c, o);
    kit.ghost(moving, boxGeo(x0 + w, x1 - w, y0, y0 + w, zb + w, zs), c, o);
    kit.ghost(moving, boxGeo(x0 + w, x1 - w, y1 - w, y1, zb + w, zs), c, o);
    kit.outline(moving, boxGeo(x0, x1, y0, y1, zb, zs));
    // lid: plate with the bushing hole, plus the skirt
    const plate = new THREE.Shape();
    plate.moveTo(x0, y0); plate.lineTo(x1, y0); plate.lineTo(x1, y1); plate.lineTo(x0, y1); plate.closePath();
    const hole = new THREE.Path();
    hole.absarc(sx, sy, (L.bushing.collar_d ?? 21.5) / 2 + 0.75, 0, TAU, true);
    plate.holes.push(hole);
    kit.ghost(fixed, extrude(plate, zt - lt, zt), c, o * 1.3);
    kit.ghost(fixed, boxGeo(x0, x0 + w, y0, y1, zs, zt - lt), c, o);
    kit.ghost(fixed, boxGeo(x1 - w, x1, y0, y1, zs, zt - lt), c, o);
    kit.ghost(fixed, boxGeo(x0 + w, x1 - w, y0, y0 + w, zs, zt - lt), c, o);
    kit.ghost(fixed, boxGeo(x0 + w, x1 - w, y1 - w, y1, zs, zt - lt), c, o);
    kit.outline(fixed, boxGeo(x0, x1, y0, y1, zs, zt));
    return { moving, fixed };
  },

  bowl(item, L, kit) {
    const C = L.camera, S = L.spout, [sx, sy] = L.shaft_axis_xy;
    const g = new THREE.Group(), c = item.colour, o = item.opacity;
    const [f0, f1] = C.floor_z, ri = C.inner_r, ro = C.outer_r, zt = C.rim_top_z;
    const a0 = S.start_deg * DEG, a1 = S.end_deg * DEG;
    // floor with the shaft hole
    kit.ghost(g, extrude(ringShape(sx, sy, C.floor_hole_d / 2, ro), f0, f1, 96), c, o);
    // wall, open towards the spout below its top edge
    kit.ghost(g, extrude(sectorShape(sx, sy, ri, ro, a1, a0 + TAU), f1, zt, 96), c, o);
    kit.ghost(g, extrude(sectorShape(sx, sy, ri, ro, a0, a1), S.top_z, zt, 48), c, o);
    // tangential spout: outer wall spirals out to meet the chute flange at end_deg
    const [ix, iy] = L.chute.inlet_center;
    const rEnd = Math.hypot(ix - sx, iy - sy) + S.width_outer / 2;   // outside of the chute duct at its inlet
    const rOut = (a) => ro + (a - a0) / (a1 - a0) * (rEnd - ro);
    const pts = (r, a) => new THREE.Vector2(sx + Math.cos(a) * r, sy + Math.sin(a) * r);
    const n = 40, wall = S.wall;
    const outer = new THREE.Shape(), floor = new THREE.Shape();
    for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; const p = pts(rOut(a), a); i ? outer.lineTo(p.x, p.y) : outer.moveTo(p.x, p.y); }
    for (let i = n; i >= 0; i--) { const a = a0 + (a1 - a0) * i / n; const p = pts(rOut(a) + wall, a); outer.lineTo(p.x, p.y); }
    outer.closePath();
    kit.ghost(g, extrude(outer, f0, S.top_z), c, o);
    for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; const p = pts(rOut(a) + wall, a); i ? floor.lineTo(p.x, p.y) : floor.moveTo(p.x, p.y); }
    floor.absarc(sx, sy, ri, a1, a0, true);
    floor.closePath();
    kit.ghost(g, extrude(floor, f0, f1), c, o);
    // screw ears on the rim
    const er = C.ears_r, ne = C.ears_n;
    for (let k = 0; k < ne; k++) {
      const a = (k + 0.5) * TAU / ne;
      const e = cylGeo(5.5, 5.5, zt - 6, zt, 24);
      e.translate(sx + Math.cos(a) * er, sy + Math.sin(a) * er, 0);
      kit.ghost(g, e, c, o);
    }
    return { moving: g };
  },

  servo(item, L, kit) {
    const S = L.servo, [bx, by] = S.body_xyz, [cx, cy] = S.center_xy;
    const g = new THREE.Group();
    const zb = S.body_bottom_z, zt = S.body_top_z, ztab = S.tab_underside_z, tl = S.tab_len_x, tip = S.spline_tip_z;
    const ax = cx + S.shaft_offset_x_from_center;
    kit.solid(g, boxGeo(cx - bx / 2, cx + bx / 2, cy - by / 2, cy + by / 2, zb, ztab - 0.01), item.colour);
    kit.solid(g, boxGeo(cx - bx / 2 + 0.4, cx + bx / 2 - 0.4, cy - by / 2 + 0.4, cy + by / 2 - 0.4, ztab, zt), '#202328');
    const tab = boxGeo(cx - tl / 2, cx + tl / 2, cy - by / 2 + 0.6, cy + by / 2 - 0.6, ztab, ztab + 2.5);
    kit.solid(g, tab, '#202328');
    for (const sxn of [-1, 1]) {   // mounting holes hint
      const h = cylGeo(2.2, 2.2, ztab - 0.2, ztab + 2.7, 16);
      h.translate(cx + sxn * (tl / 2 - 3.5), cy, 0);
      kit.solid(g, h, '#0f1114');
    }
    kit.solid(g, cylGeo(7, 7, zt, zt + 1.6, 40).translate(ax, cy, 0), '#202328');
    kit.solid(g, cylGeo(2.95, 2.95, zt + 1.6, tip, 25).translate(ax, cy, 0), '#c9a343', { metalness: 0.6, roughness: 0.35 });
    // three-wire lead
    const lead = new THREE.CatmullRomCurve3([
      new THREE.Vector3(cx + bx / 2, cy, zb + 6), new THREE.Vector3(cx + bx / 2 + 14, cy, zb + 4),
      new THREE.Vector3(cx + bx / 2 + 40, cy + 20, zb - 6), new THREE.Vector3(cx + bx / 2 + 70, cy + 50, zb - 20),
    ]);
    kit.solid(g, new THREE.TubeGeometry(lead, 40, 1.6, 8, false), '#3b3f45', { cap: false, decor: true });
    return { moving: g };
  },

  hopper(item, L, kit) {
    const H = L.hopper, [sx, sy] = L.shaft_axis_xy, z0 = L.ripiano.seat_z;
    const g = new THREE.Group(), c = item.colour, o = item.opacity;
    const zp = z0 + H.plate_t;
    kit.ghost(g, extrude(ringShape(sx, sy, H.throat_r, H.plate_r), z0, zp, 96), c, o, { dashed: true });
    kit.ghost(g, cylGeo(H.throat_r, H.funnel_top_r, zp, zp + H.funnel_h, 72, true).translate(sx, sy, 0), c, o, { dashed: true });
    return { moving: g };
  },

  container(item, L, kit) {
    const H = L.hopper, K = L.container, [sx, sy] = L.shaft_axis_xy;
    const z0 = L.ripiano.seat_z + H.plate_t + H.funnel_h + K.bottom_gap;
    const g = new THREE.Group(), c = item.colour, o = item.opacity;
    kit.ghost(g, cylGeo(K.r_bottom, K.r_top, z0, z0 + K.h, 72, true).translate(sx, sy, 0), c, o, { dashed: true });
    const lid = new THREE.CircleGeometry(K.r_top, 72);
    lid.translate(sx, sy, z0 + K.h);
    kit.ghost(g, lid, c, o * 0.6, { dashed: true });
    return { moving: g };
  },

  board(item, L, kit) {
    const E = L.esp32, B = L.box, g = new THREE.Group();
    const [bw, bd, bt] = E.board_xyz, [cx, cy] = E.center;
    const floor = B.outer_z[0] + B.wall, z0 = floor + E.standoff;
    kit.solid(g, boxGeo(cx - bw / 2, cx + bw / 2, cy - bd / 2, cy + bd / 2, z0, z0 + bt), item.colour);
    kit.solid(g, boxGeo(cx - bw / 2 + 3, cx - bw / 2 + 21, cy - 9, cy + 9, z0 + bt, z0 + bt + 3.2), '#b9bec4', { metalness: 0.7, roughness: 0.3 });
    kit.solid(g, boxGeo(cx + bw / 2 - 7, cx + bw / 2 + 1, cy - 4.5, cy + 4.5, z0 + bt, z0 + bt + 3.2), '#9aa0a6', { metalness: 0.6, roughness: 0.35 });
    for (const [dx, dy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
      kit.solid(g, cylGeo(2.2, 2.2, floor, z0, 12).translate(cx + dx * (bw / 2 - 3), cy + dy * (bd / 2 - 3), 0), '#c9a343', { metalness: 0.5, roughness: 0.4 });
    }
    // cable gland on the +X wall and the 12 V lead to the board
    const [gx, gy, gz] = E.gland_xyz, r = E.gland_d / 2;
    const gland = new THREE.CylinderGeometry(r, r, 14, 6);
    gland.rotateZ(Math.PI / 2);
    gland.translate(gx + 4, gy, gz);
    kit.solid(g, gland, '#3a3e44', { decor: true });
    const cable = new THREE.CatmullRomCurve3([
      new THREE.Vector3(gx + 60, gy, gz - 30), new THREE.Vector3(gx + 22, gy, gz - 2), new THREE.Vector3(gx - 6, gy, gz),
      new THREE.Vector3(gx - 34, gy - 4, z0 + 12), new THREE.Vector3(cx + bw / 2 + 4, cy, z0 + 3),
    ]);
    kit.solid(g, new THREE.TubeGeometry(cable, 48, 2.6, 10, false), '#2a2d31', { cap: false, decor: true });
    return { moving: g };
  },
};

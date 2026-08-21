
fn main() {
    let a: Vec<String> = std::env::args().skip(1).collect();
    let trace_path = &a[0];
    let reach: i64 = a[1].parse().unwrap();
    let third = a.contains(&"--third".to_string());
    let sky = a.contains(&"--sky".to_string());
    let castle_path = a.iter().position(|s| s == "--castle").map(|i| a[i + 1].clone());
    let (cw, ch) = (1280i32, 720i32);
    let t = load_trace(trace_path).expect("trace");
    let castle: Vec<Prism> = match castle_path { Some(p) => load_castle(&p).expect("castle"),
                                                 None => Vec::new() };
    let mut buf = vec![0u32; (cw * ch) as usize];
    let mut zbuf = vec![0i32; (cw * ch) as usize];
    let mut fx_cam = Fx::new();
    let mut cam = Cam { q: Q4 { w: ONE, x: 0, y: 0, z: 0 }, pitch_acc: 0, px: 0, py: 0 };
    let ladder = if reach > LOD_R0 { lod_schedule(reach, ch as i64 * 2) } else { Vec::new() };
    let cache_cap = if ladder.is_empty() { 0 } else { derived_cap(&ladder) };
    let mut lodw = LodWorld::new(&ladder, cache_cap);
    let mut world = World::new();
    if !ladder.is_empty() {
        let (pfx, pfy) = if third {
            let qc0 = qconj(cam.q);
            let by0 = fx_cam.vrotate(qc0, V3 { x: 0, y: ONE, z: 0 });
            let (fwx, fwy) = (by0.x >> 16, by0.y >> 16);
            let n2 = fwx * fwx + fwy * fwy;
            let (f16x, f16y) = if n2 == 0 { (0, 1 << 16) } else {
                let n = isqrt64(n2).max(1); (fwx * 65536 / n, fwy * 65536 / n) };
            (cam.px - (f16x * AV_BOOM8 >> 16), cam.py - (f16y * AV_BOOM8 >> 16))
        } else { (cam.px, cam.py) };
        lodw.prefill(floordiv(pfx >> 8, TILE), floordiv(pfy >> 8, TILE), &ladder);
    }
    let mut av_state: usize = 0;
    let mut av_start: u32 = 0;
    let mut av_m: [i64; 9] = [0; 9];
    let total = t.rows.len() as u32;
    for frame in 0..total {
        let (keys, dx, dy) = t.rows[frame as usize];
        step_cam(&mut fx_cam, &mut cam, keys, dx, dy);
        let rcam = if third {
            let qc = qconj(cam.q);
            let bxv = fx_cam.vrotate(qc, V3 { x: ONE, y: 0, z: 0 });
            let byv = fx_cam.vrotate(qc, V3 { x: 0, y: ONE, z: 0 });
            let bzv = fx_cam.vrotate(qc, V3 { x: 0, y: 0, z: ONE });
            let m3 = [bxv.x >> 16, byv.x >> 16, bzv.x >> 16,
                      bxv.y >> 16, byv.y >> 16, bzv.y >> 16,
                      bxv.z >> 16, byv.z >> 16, bzv.z >> 16];
            let (fwx, fwy) = (m3[3], m3[4]);
            let n2 = fwx * fwx + fwy * fwy;
            let (f16x, f16y) = if n2 == 0 { (0, 1 << 16) } else {
                let n = isqrt64(n2).max(1); (fwx * 65536 / n, fwy * 65536 / n) };
            let moving = keys & 0xF != 0;
            if moving && av_state == 0 {
                let (ns, moved) = step_canonical(av_state, 0);
                if moved { av_state = ns; av_start = frame; }
            } else if !moving && av_state == 1 {
                let (ns, moved) = step_canonical(av_state, 2);
                if moved { av_state = ns; av_start = frame; }
            }
            av_m = m3;
            Cam { q: cam.q, pitch_acc: cam.pitch_acc,
                  px: cam.px - (f16x * AV_BOOM8 >> 16),
                  py: cam.py - (f16y * AV_BOOM8 >> 16) }
        } else { Cam { q: cam.q, pitch_acc: cam.pitch_acc, px: cam.px, py: cam.py } };
        if ladder.is_empty() {
            raster_world(&mut fx_cam, &mut buf, &mut zbuf, cw, ch, &rcam, &mut world);
        } else {
            raster_rings(&mut fx_cam, &mut buf, &mut zbuf, cw, ch, &rcam, &mut lodw, &ladder);
        }
        if !castle.is_empty() && !ladder.is_empty() {
            let qcc = qconj(rcam.q);
            let cbx = fx_cam.vrotate(qcc, V3 { x: ONE, y: 0, z: 0 });
            let cby = fx_cam.vrotate(qcc, V3 { x: 0, y: ONE, z: 0 });
            let cbz = fx_cam.vrotate(qcc, V3 { x: 0, y: 0, z: ONE });
            let cm = [cbx.x >> 16, cby.x >> 16, cbz.x >> 16,
                      cbx.y >> 16, cby.y >> 16, cbz.y >> 16,
                      cbx.z >> 16, cby.z >> 16, cbz.z >> 16];
            let ctx = floordiv(rcam.px >> 8, TILE);
            let cty = floordiv(rcam.py >> 8, TILE);
            let (crx8, cry8) = (rcam.px - ((ctx * TILE) << 8), rcam.py - ((cty * TILE) << 8));
            let (cu, cv) = (crx8 / TILE, cry8 / TILE);
            let (c00, c10) = (lodw.h(ctx, cty, 1) << 8, lodw.h(ctx + 1, cty, 1) << 8);
            let (c01, c11) = (lodw.h(ctx, cty + 1, 1) << 8, lodw.h(ctx + 1, cty + 1, 1) << 8);
            let cx0 = c00 + (c10 - c00) * cu / 256;
            let cx1 = c01 + (c11 - c01) * cu / 256;
            let ceye = cx0 + (cx1 - cx0) * cv / 256 + (3 << 8);
            let rr = ladder[ladder.len() - 1].2;
            draw_castle(&mut buf, &mut zbuf, cw, ch, &cm, (rcam.px, rcam.py, ceye),
                        &castle, rr * TILE * 256);
        }
        if third && !ladder.is_empty() {
            let t_q32 = fx_cam.rdiv((frame - av_start) as i128 * ONE as i128, 120);
            let (joints, _g8) = avatar_joints(&mut fx_cam, &mut lodw, &cam, &av_m,
                                              av_state, t_q32);
            let etx = floordiv(rcam.px >> 8, TILE);
            let ety = floordiv(rcam.py >> 8, TILE);
            let (erx8, ery8) = (rcam.px - ((etx * TILE) << 8), rcam.py - ((ety * TILE) << 8));
            let (eu, ev) = (erx8 / TILE, ery8 / TILE);
            let (e00, e10) = (lodw.h(etx, ety, 1) << 8, lodw.h(etx + 1, ety, 1) << 8);
            let (e01, e11) = (lodw.h(etx, ety + 1, 1) << 8, lodw.h(etx + 1, ety + 1, 1) << 8);
            let ex0 = e00 + (e10 - e00) * eu / 256;
            let ex1 = e01 + (e11 - e01) * eu / 256;
            let eye8 = ex0 + (ex1 - ex0) * ev / 256 + (3 << 8);
            draw_avatar(&mut buf, &mut zbuf, cw, ch, &av_m,
                        (rcam.px, rcam.py, eye8), &joints);
        }
        if sky { star_sky(&mut fx_cam, &mut buf, &mut zbuf, cw, ch, &rcam); }
        // THE OBJECT, beside the digest, every frame — not every sixtieth.
        println!("{} {:016x} {} {} {} {} {} {} {} {} {}",
                 frame, fnv64(&buf, 0), cam.px, cam.py,
                 cam.q.w, cam.q.x, cam.q.y, cam.q.z, cam.pitch_acc,
                 av_state, frame - av_start);
    }
}

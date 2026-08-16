// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
// harness_capcost.rs — the replay harness MAIN that produced the capcost schedule record
// (URDRCPC1). NOT a standalone program: the authoring container assembles it as
//   #![allow(dead_code)]  +  the fpsdemo.rs core slice (the lines between the
//   "// ---- exact integer helpers" and "// ---- the entry door" markers)  +  this main,
// then compiles with rustc -O. Mode "run" speaks the demo's OWN access schedule — ladder
// derived from reach, prefill from the spawn tile BEFORE the walk (v1.7's prefill-before-
// timer convention), then the committed trace — which is what makes its FIFO recompute and
// eviction counts comparable to the demo's. Mode "raw" preserves the old fill-on-first-
// rebase schedule as the committed negative control: its counts must DIFFER at every shared
// regime-B point, or schedule-dependence is unproven. Digest chains are printed on the same
// sixty-frame cadence as the demo and must equal the committed oracles under EVERY cap and
// BOTH schedules — values are schedule-independent; costs are not.

fn main() {
    let argv: Vec<String> = std::env::args().skip(1).collect();
    let mode = argv[0].clone();               // "run" = demo schedule (prefill first); "raw" = no prefill
    let text = std::fs::read_to_string(&argv[1]).unwrap();
    let reach: i64 = argv[2].parse().unwrap();
    let cap: usize = if argv.len() > 3 { argv[3].parse().unwrap() } else { 0 };
    let mut trace: Vec<(u32, i64, i64)> = Vec::new();
    for ln in text.lines() {
        if ln.starts_with('#') || ln.trim().is_empty() { continue }
        let p: Vec<&str> = ln.split_whitespace().collect();
        trace.push((p[0].parse().unwrap(), p[1].parse().unwrap(), p[2].parse().unwrap()));
    }
    let (cw, ch) = (1280i32, 720i32);
    let mut buf = vec![0u32; (cw * ch) as usize];
    let mut zbuf = vec![0i32; (cw * ch) as usize];
    let mut fx_cam = Fx::new();
    let mut world = World::new();
    let ladder = if reach > LOD_R0 { lod_schedule(reach, ch as i64 * 2) } else { Vec::new() };
    let mut lodw = LodWorld::new(&ladder, cap);
    let mut cam = Cam { q: Q4 { w: ONE, x: 0, y: 0, z: 0 }, pitch_acc: 0, px: 0, py: 0 };
    // THE DEMO'S ACCESS SCHEDULE: prefill from the spawn tile BEFORE the walk, exactly as the
    // entry door does it (v1.7's prefill-before-timer convention). "raw" preserves the old
    // fill-on-first-rebase schedule as the negative control.
    let prefill_tiles: u64 = if mode == "run" && !ladder.is_empty() {
        lodw.prefill(floordiv(cam.px >> 8, TILE), floordiv(cam.py >> 8, TILE), &ladder)
    } else { 0 };
    let total = trace.len() as u32;
    for frame in 0..total {
        let (keys, dx, dy) = trace[frame as usize];
        step_cam(&mut fx_cam, &mut cam, keys, dx, dy);
        if ladder.is_empty() {
            raster_world(&mut fx_cam, &mut buf, &mut zbuf, cw, ch, &cam, &mut world);
        } else {
            raster_rings(&mut fx_cam, &mut buf, &mut zbuf, cw, ch, &cam, &mut lodw, &ladder);
        }
        if frame % 60 == 59 || frame + 1 == total {
            println!("digest frame {} fnv64 {:016x}", frame, fnv64(&buf, 0));
        }
    }
    eprintln!("schedule {} | reach {} | prefill_tiles {} | cap {} | occupancy {} | recomputes {} | evictions {}",
              mode, reach, prefill_tiles, cap, lodw.cache.len(), lodw.recomputes, lodw.evictions);
}

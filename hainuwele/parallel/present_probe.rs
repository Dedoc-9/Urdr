// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// present_probe.rs — THE §3 INSTRUMENT: a real window, a real present loop, QPC timestamps at
// every sealframe instant software can reach — and, from v0.2, THE COST QUESTION (URDRPRS1).
//
// v0 HISTORY. Three segments of sealframe's partition read NOT_MEASURED with the note "the layer-3
// renderer does not exist"; the standing law forbids latency work without a measured target. v0
// was the smallest instrument that could produce one, and its first named-host run caught ITSELF:
// 176 of 723 deadlines missed with half a millisecond of work — Sleep(1) under Windows' default
// ~15.6 ms timer resolution overshoots a 120 Hz slot whole.
//
// v0.1 repaired what that run found: winmm timeBeginPeriod(1) requested and its grant LOGGED,
// lateness recorded as a MAGNITUDE (late-by percentiles) rather than a bare count (L44), and the
// protocol stating that a run with an empty click table is not complete. Its named-host run
// produced twenty click chains, now committed at spec/attest/present_probe-allyx-v01.txt and
// graduated through sealframe's own door (probelog, URDRPBL1). Verdict on pacing: the MEDIAN is
// repaired (late p50 = 0) and the TAIL is not (135 of 2054 frames over 1 ms late, p99 a full
// slot) — the tail is now the measured target the DXGI pivot exists to attack, LATER.
//
// v0.2 — THE P2 CONTRACT. Not "find a resolution that looks fast": measure the renderer enough
// that resolution becomes an EVIDENCE-DERIVED decision.
//
//   * THE WORKLOAD IS REAL: an integer 3D terrain — 33x33 heightfield, ~2k triangles, yaw-orbit
//     camera, z-buffered edge-function rasterization, flat shading — all i64 arithmetic, no
//     float anywhere. It is THIS PROBE'S renderer and its cost is labeled as such; it is not
//     raster3d and does not claim raster3d's conformance. (Not perspective-correct in depth
//     interpolation — the COST SHAPE is what is under measurement, and that term is per-pixel
//     either way.)
//   * RESOLUTION IS THE TREATMENT AXIS, and it may not be a proxy for elapsed time (URDRCNF1):
//     cells run as interleaved SEGMENTS, each (cell, pass) pair visited once per pass with the
//     order rotated between passes, so no cell owns an era of the run. Between-pass spread is the
//     variance ruler (URDRRPT1) — the analysis rung must use it, not within-pass iteration noise.
//   * THE FUNCTIONAL FORM IS A PREDICTION, NOT AN ASSUMPTION. The a-priori model is
//     T_raster(W,H) ~ T_fixed + W*H*T_pixel. The log records per-(cell,pass) bands and the
//     repo-side analysis decides whether the relationship is affine, piecewise, or something
//     else — the TPI lesson: let the measurement rule.
//   * CONDITIONS ARE OPERATOR DECLARATIONS, required at the door (the strict-door refusal in
//     probelog is this instrument's specification): a --host run REFUSES without --power and
//     --scheduler, and both enter the log header, so a v0.2 record can pass
//     `require_conditions=True` where the v0.1 record could not.
//   * THE PLANT IS LOCALIZED (the `deeper` lesson: a grouped verdict, not a pooled one):
//     --defect stalls ONE cell (the middle one) by 5 ms per frame, and the self-check passes
//     only if the per-cell aggregation SEES it in that cell and not in the others.
//
// STILL, AND ALWAYS: wall-clock class, DELIBERATELY UNGATED (the bench.py precedent); std-only
// raw Win32 FFI, no cargo (the urdr_render_rs precedent); integer ns; lower-middle percentiles
// (repeat's convention); an entry door that refuses unknown flags and flag-swallowing (URDRENT1);
// a log without --host says so and cannot graduate anything (sealframe-honesty).
//
// RUN PROTOCOL (PowerShell, repo root, rustc >= 1.58, RED FIRST):
//   rustc -O --edition 2021 -o present_probe.exe hainuwele\parallel\present_probe.rs
//   .\present_probe.exe --defect                       # must print DEFECT CAUGHT in the MIDDLE
//                                                      # cell only, exit 0 (~40 s)
//   .\present_probe.exe --host "ROG-Ally-X-Z2-Extreme" --power "Turbo-35W-AC" `
//                       --scheduler "Win11-GameMode-UltimatePerf" --hz 120
//   # click ~20 times spread across the run; ESC ends early (partial segments stay honest: each
//   # row carries its own n). log: present_probe_log.txt — run TWICE, keep both.
//
// GRADE (honest, D5): the file is DECLARED; every number it will print is NOT_MEASURED until the
// named host runs it. v0.2's renderer is new code, authored in a container with no Windows link
// target: type-checked here, SPECULATIVE at link and runtime until the red-first protocol is
// green on the Ally X — the same birth-state v0 had, and v0's protocol found real defects twice.

#![allow(non_snake_case, non_camel_case_types, dead_code)]

use std::sync::atomic::{AtomicI64, AtomicU32, Ordering};

// ---- Win32 FFI, hand-declared (no crates) ----------------------------------------------------
type HANDLE = usize;
type WNDPROC = extern "system" fn(HANDLE, u32, usize, isize) -> isize;

#[repr(C)]
struct WNDCLASSW {
    style: u32,
    lpfnWndProc: WNDPROC,
    cbClsExtra: i32,
    cbWndExtra: i32,
    hInstance: HANDLE,
    hIcon: HANDLE,
    hCursor: HANDLE,
    hbrBackground: HANDLE,
    lpszMenuName: *const u16,
    lpszClassName: *const u16,
}
#[repr(C)]
struct POINT { x: i32, y: i32 }
#[repr(C)]
struct MSG { hwnd: HANDLE, message: u32, wParam: usize, lParam: isize, time: u32, pt: POINT }
#[repr(C)]
struct RECT { left: i32, top: i32, right: i32, bottom: i32 }
#[repr(C)]
struct BITMAPINFOHEADER {
    biSize: u32, biWidth: i32, biHeight: i32, biPlanes: u16, biBitCount: u16,
    biCompression: u32, biSizeImage: u32, biXPelsPerMeter: i32, biYPelsPerMeter: i32,
    biClrUsed: u32, biClrImportant: u32,
}
#[repr(C)]
struct BITMAPINFO { bmiHeader: BITMAPINFOHEADER, bmiColors: [u32; 3] }

#[link(name = "user32")]
extern "system" {
    fn RegisterClassW(c: *const WNDCLASSW) -> u16;
    fn CreateWindowExW(ex: u32, cls: *const u16, name: *const u16, style: u32,
                       x: i32, y: i32, w: i32, h: i32,
                       parent: HANDLE, menu: HANDLE, inst: HANDLE, param: usize) -> HANDLE;
    fn DefWindowProcW(h: HANDLE, m: u32, w: usize, l: isize) -> isize;
    fn PeekMessageW(m: *mut MSG, h: HANDLE, lo: u32, hi: u32, remove: u32) -> i32;
    fn TranslateMessage(m: *const MSG) -> i32;
    fn DispatchMessageW(m: *const MSG) -> isize;
    fn PostQuitMessage(code: i32);
    fn DestroyWindow(h: HANDLE) -> i32;
    fn GetDC(h: HANDLE) -> HANDLE;
    fn ShowWindow(h: HANDLE, cmd: i32) -> i32;
    fn GetClientRect(h: HANDLE, r: *mut RECT) -> i32;
    fn LoadCursorW(inst: HANDLE, name: usize) -> HANDLE;
}
#[link(name = "gdi32")]
extern "system" {
    fn StretchDIBits(dc: HANDLE, xd: i32, yd: i32, wd: i32, hd: i32,
                     xs: i32, ys: i32, ws: i32, hs: i32,
                     bits: *const u8, bmi: *const BITMAPINFO, usage: u32, rop: u32) -> i32;
    fn GdiFlush() -> i32;
}
#[link(name = "winmm")]
extern "system" {
    fn timeBeginPeriod(ms: u32) -> u32;
    fn timeEndPeriod(ms: u32) -> u32;
}
#[link(name = "kernel32")]
extern "system" {
    fn QueryPerformanceCounter(v: *mut i64) -> i32;
    fn QueryPerformanceFrequency(v: *mut i64) -> i32;
    fn Sleep(ms: u32);
    fn GetModuleHandleW(n: *const u16) -> HANDLE;
}

const WM_DESTROY: u32 = 0x0002;
const WM_CLOSE: u32 = 0x0010;
const WM_QUIT: u32 = 0x0012;
const WM_KEYDOWN: u32 = 0x0100;
const WM_LBUTTONDOWN: u32 = 0x0201;
const VK_ESCAPE: usize = 0x1B;
const PM_REMOVE: u32 = 1;
const SRCCOPY: u32 = 0x00CC0020;
const DIB_RGB_COLORS: u32 = 0;
const CS_OWNDC: u32 = 0x0020;
const WS_OVERLAPPEDWINDOW: u32 = 0x00CF0000;
const WS_VISIBLE: u32 = 0x1000_0000;
const SW_SHOW: i32 = 5;
const IDC_ARROW: usize = 32512;

// ---- the instants a WndProc can reach --------------------------------------------------------
static CLICK_QPC: AtomicI64 = AtomicI64::new(0);
static DROPPED_CLICKS: AtomicU32 = AtomicU32::new(0);
static QUIT: AtomicU32 = AtomicU32::new(0);

fn qpc() -> i64 { let mut v = 0i64; unsafe { QueryPerformanceCounter(&mut v) }; v }

extern "system" fn wndproc(h: HANDLE, m: u32, wp: usize, lp: isize) -> isize {
    match m {
        WM_LBUTTONDOWN => {
            let t = qpc();
            if CLICK_QPC.compare_exchange(0, t, Ordering::SeqCst, Ordering::SeqCst).is_err() {
                DROPPED_CLICKS.fetch_add(1, Ordering::SeqCst);
            }
            0
        }
        WM_KEYDOWN if wp == VK_ESCAPE => { unsafe { DestroyWindow(h) }; 0 }
        WM_CLOSE => { unsafe { DestroyWindow(h) }; 0 }
        WM_DESTROY => { QUIT.store(1, Ordering::SeqCst); unsafe { PostQuitMessage(0) }; 0 }
        _ => unsafe { DefWindowProcW(h, m, wp, lp) },
    }
}

fn wstr(s: &str) -> Vec<u16> { s.encode_utf16().chain(std::iter::once(0)).collect() }

// ---- exact integer helpers -------------------------------------------------------------------
fn ticks_to_ns(t: i64, freq: i64) -> i64 { ((t as i128) * 1_000_000_000i128 / (freq as i128)) as i64 }

/// Percentile by rank, LOWER MIDDLE — repeat.py's integer convention.
fn pct(sorted: &[i64], p: usize) -> i64 {
    if sorted.is_empty() { return -1 }
    sorted[(sorted.len() - 1) * p / 100]
}

// ---- integer trig: Q12 quarter-wave sine table, 256-step circle -------------------------------
const SIN_Q12: [i64; 65] = [
    0, 101, 201, 301, 401, 501, 601, 700, 799, 897, 995, 1092, 1189, 1285, 1380, 1474,
    1567, 1660, 1751, 1842, 1931, 2019, 2106, 2191, 2276, 2359, 2440, 2520, 2598, 2675,
    2751, 2824, 2896, 2967, 3035, 3102, 3166, 3229, 3290, 3349, 3406, 3461, 3513, 3564,
    3612, 3659, 3703, 3745, 3784, 3822, 3857, 3889, 3920, 3948, 3973, 3996, 4017, 4036,
    4052, 4065, 4076, 4085, 4091, 4095, 4096,
];

fn sinq(a: i64) -> i64 {
    let a = ((a % 256) + 256) % 256;
    match a {
        0..=64 => SIN_Q12[a as usize],
        65..=128 => SIN_Q12[(128 - a) as usize],
        129..=192 => -SIN_Q12[(a - 128) as usize],
        _ => -SIN_Q12[(256 - a) as usize],
    }
}

fn cosq(a: i64) -> i64 { sinq(a + 64) }

// ---- the terrain: a 33x33 integer heightfield, built once ------------------------------------
const GRID: i64 = 33;
// pitch 35 degrees, Q12: cos ~ 3355, sin ~ 2350 (DECLARED framing constants).
const CP: i64 = 3355;
const SP: i64 = 2350;
const EYE_D: i64 = 64;
const NEAR: i64 = 12;

fn height(x: i64, y: i64) -> i64 {
    // two integer waves plus a hash ripple — bumpy, deterministic, float-free.
    (sinq(x * 11) * 7 + sinq(y * 13) * 5) / 4096 + ((x * 73_856_093 ^ y * 19_349_663) >> 13 & 3)
}

struct Scene {
    verts: Vec<(i64, i64, i64)>,          // world (X, Y, Z), centered and spread
    tris: Vec<(usize, usize, usize, u32)>,
}

fn build_scene() -> Scene {
    let mut verts = Vec::new();
    for y in 0..GRID {
        for x in 0..GRID {
            verts.push(((x - GRID / 2) * 3, (y - GRID / 2) * 3, height(x, y)));
        }
    }
    let idx = |x: i64, y: i64| (y * GRID + x) as usize;
    let mut tris = Vec::new();
    for y in 0..GRID - 1 {
        for x in 0..GRID - 1 {
            let (a, b, c, d) = (idx(x, y), idx(x + 1, y), idx(x, y + 1), idx(x + 1, y + 1));
            let h4 = verts[a].2 + verts[b].2 + verts[c].2 + verts[d].2;
            let checker = ((x ^ y) & 1) as i64 * 16;
            let g = (96 + h4 * 6 + checker).clamp(0, 255) as u32;
            let color = ((g / 3 + 30) << 16) | (g << 8) | (g / 4 + 20);
            tris.push((a, b, c, color));
            tris.push((b, d, c, color.wrapping_add(0x00050505)));
        }
    }
    Scene { verts, tris }
}

// ---- the renderer under measurement -----------------------------------------------------------
/// Transform + z-buffered edge-function fill, ALL integer. Returns nothing; the caller times it.
fn raster_scene(buf: &mut [u32], zbuf: &mut [i32], w: i32, h: i32, scene: &Scene, yaw: i64,
                flash: bool) {
    if flash { for p in buf.iter_mut().take((w * h) as usize) { *p = 0x00FF_FFFF } return }
    // clear: sky gradient above, haze below (per-row fills are part of the per-pixel cost, and
    // belong in the model — a clear is W*H work like any other fill).
    let horizon = h * 2 / 5;
    for y in 0..h {
        let c: u32 = if y < horizon {
            let t = (y * 200 / horizon.max(1)) as u32;
            (30 << 16) | ((70 + t / 3) << 8) | (130 + t / 2).min(255)
        } else {
            0x0030_3038
        };
        let row = (y * w) as usize;
        for x in 0..w as usize { buf[row + x] = c }
    }
    for z in zbuf.iter_mut().take((w * h) as usize) { *z = i32::MAX }

    let (s, c) = (sinq(yaw), cosq(yaw));
    let f = h as i64 * 2;
    let (cx, cy) = (w as i64 / 2, h as i64 * 3 / 5);
    let mut screen: Vec<(i64, i64, i64)> = Vec::with_capacity(scene.verts.len());
    for &(x0, y0, z0) in &scene.verts {
        let x1 = (x0 * c - y0 * s) / 4096;
        let y1 = (x0 * s + y0 * c) / 4096;
        let y2 = (y1 * CP + z0 * SP) / 4096 + EYE_D;
        let z2 = (z0 * CP - y1 * SP) / 4096;
        if y2 < NEAR { screen.push((i64::MIN, 0, 0)); continue }
        screen.push((cx + x1 * f / y2, cy - z2 * f / y2, y2));
    }
    for &(ia, ib, ic, color) in &scene.tris {
        let (a, b, cc) = (screen[ia], screen[ib], screen[ic]);
        if a.0 == i64::MIN || b.0 == i64::MIN || cc.0 == i64::MIN { continue }
        let area = (b.0 - a.0) * (cc.1 - a.1) - (b.1 - a.1) * (cc.0 - a.0);
        if area <= 0 { continue }
        let x_lo = a.0.min(b.0).min(cc.0).max(0);
        let x_hi = a.0.max(b.0).max(cc.0).min(w as i64 - 1);
        let y_lo = a.1.min(b.1).min(cc.1).max(0);
        let y_hi = a.1.max(b.1).max(cc.1).min(h as i64 - 1);
        if x_lo > x_hi || y_lo > y_hi { continue }
        for py in y_lo..=y_hi {
            let row = (py * w as i64) as usize;
            for px in x_lo..=x_hi {
                let w0 = (b.0 - a.0) * (py - a.1) - (b.1 - a.1) * (px - a.0);
                let w1 = (cc.0 - b.0) * (py - b.1) - (cc.1 - b.1) * (px - b.0);
                let w2 = (a.0 - cc.0) * (py - cc.1) - (a.1 - cc.1) * (px - cc.0);
                if w0 >= 0 && w1 >= 0 && w2 >= 0 {
                    let d = ((w1 * a.2 + w2 * b.2 + w0 * cc.2) / area) as i32;
                    let i = row + px as usize;
                    if d < zbuf[i] { zbuf[i] = d; buf[i] = color }
                }
            }
        }
    }
    // crosshair — the eye's check that the world is really turning.
    let (chx, chy) = (w / 2, h / 2);
    for dd in -8i32..9 {
        if chx + dd >= 0 && chx + dd < w { buf[(chy * w + chx + dd) as usize] = 0x00FF_FFFF }
        if chy + dd >= 0 && chy + dd < h { buf[((chy + dd) * w + chx) as usize] = 0x00FF_FFFF }
    }
}

// ---- the entry door --------------------------------------------------------------------------
struct Args {
    host: String, power: String, scheduler: String, hz: i64, seg: u32, passes: u32,
    cells: Vec<(i32, i32)>, defect: bool, out: String,
}

fn parse_cells(spec: &str) -> Result<Vec<(i32, i32)>, String> {
    let mut out = Vec::new();
    for part in spec.split(',') {
        let (w, h) = part.split_once('x').ok_or(format!("cell {part:?} is not WxH"))?;
        let (w, h): (i32, i32) = (w.parse().map_err(|_| "cell width: not an integer")?,
                                  h.parse().map_err(|_| "cell height: not an integer")?);
        if !(64..=4096).contains(&w) || !(64..=4096).contains(&h) {
            return Err(format!("cell {w}x{h} out of [64,4096]"));
        }
        out.push((w, h));
    }
    if out.len() < 2 { return Err("need at least 2 cells to measure a slope".into()) }
    Ok(out)
}

fn parse_argv() -> Result<Args, String> {
    let mut a = Args { host: "-".into(), power: "-".into(), scheduler: "-".into(), hz: 120,
                       seg: 120, passes: 6, cells: parse_cells("640x360,960x540,1280x720")?,
                       defect: false, out: "present_probe_log.txt".into() };
    let argv: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;
    while i < argv.len() {
        let flag = argv[i].as_str();
        let value = |i: &mut usize| -> Result<String, String> {
            *i += 1;
            let v = argv.get(*i).ok_or(format!("{flag} needs a value"))?;
            if v.starts_with("--") { return Err(format!("{flag} swallowed the flag {v}")); }
            Ok(v.clone())
        };
        match flag {
            "--host" => a.host = value(&mut i)?,
            "--power" => a.power = value(&mut i)?,
            "--scheduler" => a.scheduler = value(&mut i)?,
            "--hz" => a.hz = value(&mut i)?.parse().map_err(|_| "--hz: not an integer")?,
            "--seg" => a.seg = value(&mut i)?.parse().map_err(|_| "--seg: not an integer")?,
            "--passes" => a.passes = value(&mut i)?.parse().map_err(|_| "--passes: not an integer")?,
            "--cells" => a.cells = parse_cells(&value(&mut i)?)?,
            "--out" => a.out = value(&mut i)?,
            "--defect" => a.defect = true,
            other => return Err(format!("unknown flag {other} — this door refuses")),
        }
        i += 1;
    }
    if a.hz < 1 || a.hz > 1000 { return Err("--hz out of [1,1000]".into()) }
    if a.seg < 10 { return Err("--seg under 10 frames cannot carry a band".into()) }
    if a.host != "-" && (a.power == "-" || a.scheduler == "-") {
        return Err("a named-host run without --power and --scheduler cannot pass the strict \
                    door (probelog pinned that refusal as this instrument's specification) — \
                    declare them, e.g. --power Turbo-35W-AC --scheduler Win11-GameMode-UltimatePerf".into());
    }
    Ok(a)
}

fn main() {
    let args = match parse_argv() {
        Ok(a) => a,
        Err(e) => { eprintln!("PRESENT-REFUSE: {e}"); std::process::exit(2) }
    };
    let mut freq = 0i64;
    unsafe { QueryPerformanceFrequency(&mut freq) };
    assert!(freq > 0, "QPC frequency unavailable");
    let timer_1ms_granted = unsafe { timeBeginPeriod(1) } == 0;

    let inst = unsafe { GetModuleHandleW(std::ptr::null()) };
    let cls = wstr("URDR_PRESENT_PROBE");
    let wc = WNDCLASSW {
        style: CS_OWNDC, lpfnWndProc: wndproc, cbClsExtra: 0, cbWndExtra: 0, hInstance: inst,
        hIcon: 0, hCursor: unsafe { LoadCursorW(0, IDC_ARROW) }, hbrBackground: 0,
        lpszMenuName: std::ptr::null(), lpszClassName: cls.as_ptr(),
    };
    assert!(unsafe { RegisterClassW(&wc) } != 0, "RegisterClassW failed");
    let title = wstr("urdr present probe v0.2 — click to flash, ESC to end");
    let hwnd = unsafe {
        CreateWindowExW(0, cls.as_ptr(), title.as_ptr(), WS_OVERLAPPEDWINDOW | WS_VISIBLE,
                        100, 100, 1296, 768, 0, 0, inst, 0)
    };
    assert!(hwnd != 0, "CreateWindowExW failed");
    unsafe { ShowWindow(hwnd, SW_SHOW) };
    let dc = unsafe { GetDC(hwnd) };
    let mut rc = RECT { left: 0, top: 0, right: 0, bottom: 0 };
    unsafe { GetClientRect(hwnd, &mut rc) };
    let (win_w, win_h) = (rc.right - rc.left, rc.bottom - rc.top);
    assert!(win_w > 0 && win_h > 0, "empty client area");

    let scene = build_scene();
    let ncells = args.cells.len();
    let (max_w, max_h) = args.cells.iter().fold((0, 0), |(mw, mh), &(w, h)| (mw.max(w), mh.max(h)));
    let mut buf = vec![0u32; (max_w * max_h) as usize];
    let mut zbuf = vec![0i32; (max_w * max_h) as usize];

    let frame_ns: i64 = 1_000_000_000 / args.hz;
    let ticks_per_frame = frame_ns * freq / 1_000_000_000;
    let n_segments = ncells as u32 * args.passes;
    let total_frames = n_segments * args.seg;

    // per (cell, pass): raster_ns samples; per cell: late count. Chains carry the active cell.
    let mut seg_raster: Vec<Vec<i64>> = (0..n_segments).map(|_| Vec::new()).collect();
    let mut cell_late = vec![0u32; ncells];
    let mut late_ns: Vec<i64> = Vec::with_capacity(total_frames as usize);
    let mut clicks: Vec<(i64, i64, i64, i64, i64, usize)> = Vec::new();
    let mut flash_left: u32 = 0;
    let mut deadline = qpc() + ticks_per_frame;
    let defect_cell = ncells / 2;

    let mut frame: u32 = 0;
    while frame < total_frames && QUIT.load(Ordering::SeqCst) == 0 {
        // THE SCHEDULE: segment -> (pass, slot); the cell order ROTATES by pass so the resolution
        // axis is not a proxy for elapsed time (URDRCNF1).
        let seg_idx = frame / args.seg;
        let pass = seg_idx / ncells as u32;
        let slot = seg_idx % ncells as u32;
        let cell = ((slot + pass) % ncells as u32) as usize;
        let (cw, ch) = args.cells[cell];

        let mut msg = MSG { hwnd: 0, message: 0, wParam: 0, lParam: 0, time: 0,
                            pt: POINT { x: 0, y: 0 } };
        unsafe {
            while PeekMessageW(&mut msg, 0, 0, 0, PM_REMOVE) != 0 {
                if msg.message == WM_QUIT { QUIT.store(1, Ordering::SeqCst); break }
                TranslateMessage(&msg);
                DispatchMessageW(&msg);
            }
        }
        let click = CLICK_QPC.swap(0, Ordering::SeqCst);
        let t_input = if click != 0 && flash_left == 0 { click } else { 0 };
        if t_input != 0 { flash_left = 8 }
        let flash = flash_left > 0;

        let t0 = qpc();
        let yaw = (frame as i64) % 256;                        // the sim tick: the world turns
        let t_tick = qpc();
        let _view = (yaw, cell, flash);                        // the view export: cell params
        let t_view = qpc();
        if args.defect && cell == defect_cell { unsafe { Sleep(5) } }   // THE LOCALIZED PLANT
        raster_scene(&mut buf, &mut zbuf, cw, ch, &scene, yaw, flash);
        let t_pixels = qpc();
        let bmi = BITMAPINFO {
            bmiHeader: BITMAPINFOHEADER {
                biSize: std::mem::size_of::<BITMAPINFOHEADER>() as u32,
                biWidth: cw, biHeight: -ch, biPlanes: 1, biBitCount: 32, biCompression: 0,
                biSizeImage: 0, biXPelsPerMeter: 0, biYPelsPerMeter: 0,
                biClrUsed: 0, biClrImportant: 0,
            },
            bmiColors: [0; 3],
        };
        unsafe {
            StretchDIBits(dc, 0, 0, win_w, win_h, 0, 0, cw, ch, buf.as_ptr() as *const u8,
                          &bmi, DIB_RGB_COLORS, SRCCOPY);
            GdiFlush();
        }
        let t_present = qpc();
        if flash_left > 0 { flash_left -= 1 }

        seg_raster[seg_idx as usize].push(ticks_to_ns(t_pixels - t_view, freq));
        if t_input != 0 {
            clicks.push((ticks_to_ns(t0 - t_input, freq), ticks_to_ns(t_tick - t0, freq),
                         ticks_to_ns(t_view - t_tick, freq), ticks_to_ns(t_pixels - t_view, freq),
                         ticks_to_ns(t_present - t_pixels, freq), cell));
        }
        loop {
            let now = qpc();
            if now >= deadline {
                let late = ticks_to_ns(now - deadline, freq);
                late_ns.push(late);
                if late > 1_000_000 { cell_late[cell] += 1 }
                break;
            }
            if ticks_to_ns(deadline - now, freq) > 4_000_000 { unsafe { Sleep(1) } }
        }
        deadline += ticks_per_frame;
        frame += 1;
    }
    unsafe { timeEndPeriod(1) };

    late_ns.sort_unstable();
    let (l50, l95, l99) = (pct(&late_ns, 50), pct(&late_ns, 95), pct(&late_ns, 99));
    let late_over = late_ns.iter().filter(|&&l| l > 1_000_000).count();

    let cell_names: Vec<String> = args.cells.iter().map(|&(w, h)| format!("{w}x{h}")).collect();
    let mut log = String::new();
    log.push_str(&format!(
        "present_probe v0.2 | host {} | power {} | scheduler {} | hz {} | window {}x{} | qpf {}\n",
        args.host, args.power, args.scheduler, args.hz, win_w, win_h, freq));
    log.push_str(&format!("timer_1ms_granted {}\n", timer_1ms_granted));
    log.push_str(&format!("cells {} | passes {} | seg {}\n", cell_names.join(","), args.passes,
                          args.seg));
    log.push_str(&format!("frames {} | late_over_1ms {} | dropped_clicks {}\n",
                          late_ns.len(), late_over, DROPPED_CLICKS.load(Ordering::SeqCst)));
    log.push_str(&format!("late_ns p50 {} p95 {} p99 {}\n", l50, l95, l99));
    for seg_idx in 0..n_segments as usize {
        let pass = seg_idx / ncells;
        let slot = seg_idx % ncells;
        let cell = (slot + pass) % ncells;
        let mut v = seg_raster[seg_idx].clone();
        if v.is_empty() { continue }                           // ESC before this segment ran
        v.sort_unstable();
        log.push_str(&format!("cell {} pass {} n {} raster_ns {} {} {} late {}\n",
                              cell_names[cell], pass, v.len(), v[0], pct(&v, 50),
                              v[v.len() - 1], cell_late[cell]));
    }
    log.push_str("click chains (ns): input_wait authority_tick view_export frame_render \
                  present_queue total cell\n");
    for &(a, b, c, d, e, cell) in &clicks {
        log.push_str(&format!("{} {} {} {} {} {} {}\n", a, b, c, d, e, a + b + c + d + e,
                              cell_names[cell]));
    }
    if args.host == "-" {
        log.push_str("NOTE: no --host given — this log is NOT_MEASURED by sealframe-honesty; \
                      rerun with --host, --power and --scheduler\n");
    }
    std::fs::write(&args.out, &log).expect("log write failed");
    print!("{log}");

    if args.defect {
        // RED-FIRST, LOCALIZED: the planted 5 ms must appear in the MIDDLE cell's aggregate and
        // in no other — a pooled check would pass with the stall smeared anywhere (URDRDPR1).
        let mut med_by_cell: Vec<Vec<i64>> = (0..ncells).map(|_| Vec::new()).collect();
        for seg_idx in 0..n_segments as usize {
            let pass = seg_idx / ncells;
            let cell = (seg_idx % ncells + pass) % ncells;
            let mut v = seg_raster[seg_idx].clone();
            if v.is_empty() { continue }
            v.sort_unstable();
            med_by_cell[cell].push(pct(&v, 50));
        }
        let agg: Vec<i64> = med_by_cell.iter()
            .map(|m| if m.is_empty() { -1 } else {
                let mut s = m.clone(); s.sort_unstable(); pct(&s, 50) })
            .collect();
        let target = agg[defect_cell];
        let others = agg.iter().enumerate().filter(|&(i, _)| i != defect_cell)
            .map(|(_, &v)| v).max().unwrap_or(-1);
        if target > others + 4_000_000 {
            println!("DEFECT CAUGHT in cell {} only: med {} ns vs max other {} ns",
                     cell_names[defect_cell], target, others);
        } else {
            println!("DEFECT MISSED: cell {} med {} ns vs max other {} ns — the per-cell \
                      aggregation cannot see a localized 5 ms; do not trust it",
                     cell_names[defect_cell], target, others);
            std::process::exit(1);
        }
    }
}

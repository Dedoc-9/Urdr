// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// fpsdemo.rs — P3.1: THE PLAYABLE SKELETON, CARRYING THE TREE'S REPLAY DNA (URDRFPD1, v0).
//
// P3's contract, as given: feed the real fp-chain / textured view into the loop WHILE PRESERVING
// THE EMPIRICALLY ESTABLISHED RESOLUTION BUDGET. The budget came from pixelcost's six committed
// records; this binary is where it gets spent, and the spending is measured with the same
// instrumentation that established it (per-segment raster_ns / present_ns bands).
//
// THE DESIGN COMMITMENT, INHERITED FROM THE TREE: A WORKLOAD THAT DEPENDS ON PLAYER INPUT IS NOT
// REPRODUCIBLE UNLESS THE INPUTS ARE RECORDS. So:
//   --play               interactive: WASD + mouse-look over an unbounded integer heightfield,
//                        720p 1:1 centered (the measured MARGINAL-at-120 operating point is the
//                        default; --res and --hz choose another), and EVERY frame's input
//                        (key bits, mouse dx, dy) is RECORDED to a trace file.
//   --replay <trace>     the same loop driven by the recorded inputs instead of the devices.
//                        The math is integer-only end to end, so a replay is BYTE-IDENTICAL:
//                        the framebuffer is digested every 60 frames (fnv64 — named honestly: a
//                        divergence detector, NOT a cryptographic pin; committed records keep
//                        sha256 on the repo side) and the digest chain prints with the cost rows.
//                        Two replays of one trace must print identical chains — on this machine
//                        and across hosts, because nothing in the loop reads a float or a clock
//                        to decide a pixel.
//   --defect             replay mode, red-first: after frame 600 every frame's framebuffer is
//                        COPIED, one byte of the copy is flipped, and both are digested — the
//                        clean and planted chains must MATCH before the plant and DIVERGE at it,
//                        in one run, no baseline needed. An instrument that cannot see one
//                        flipped byte has no business certifying byte-identity (L23).
//
// WHAT v0 IS NOT, SAID PLAINLY. The camera is yaw + a horizon-shift pitch approximation, not the
// gated fp-chain: fpquat/fppose/fpclip land in P3.2 as ports verified against their committed
// conformance vectors, and "textured" here means world-anchored checker + height shading, not
// sampled textures. The terrain is the probe's hash heightfield made unbounded (the grid窗口
// follows the camera), not the URDRHF1 canon — that port is also P3.2. Nothing here claims
// conformance to any gated module yet; this rung's claims are the REPLAY properties and the
// BUDGET measurement, and only those.
//
// RUN PROTOCOL (PowerShell, repo root, rustc >= 1.58, RED FIRST):
//   rustc -O --edition 2021 -o fpsdemo.exe hainuwele\parallel\fpsdemo.rs
//   .\fpsdemo.exe --play --frames 1800                 # ~15 s: walk around; trace written
//   .\fpsdemo.exe --replay fpsdemo_trace.txt           # digest chain + cost rows
//   .\fpsdemo.exe --replay fpsdemo_trace.txt           # AGAIN — chains must be IDENTICAL
//   .\fpsdemo.exe --replay fpsdemo_trace.txt --defect  # must print DIVERGED AT the plant, exit 0
//   # then a named cost run of the recorded trace:
//   .\fpsdemo.exe --replay fpsdemo_trace.txt --host "ROG-Ally-X-Z2-Extreme" `
//                  --power "Turbo-35W-AC" --scheduler "Win11-GameMode-UltimatePerf"
//
// GRADE (honest, D5): the file is DECLARED; every number and every digest is NOT_MEASURED until
// the named host runs it. Authored blind, type-checked only (no Windows link target here) —
// SPECULATIVE at link and runtime, the probe's own birth-state, and its protocol found real
// defects five times. declared != verified.

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
    fn GetSystemMetrics(index: i32) -> i32;
    fn GetCursorPos(p: *mut POINT) -> i32;
    fn SetCursorPos(x: i32, y: i32) -> i32;
    fn ShowCursor(show: i32) -> i32;
}
#[link(name = "gdi32")]
extern "system" {
    fn StretchDIBits(dc: HANDLE, xd: i32, yd: i32, wd: i32, hd: i32,
                     xs: i32, ys: i32, ws: i32, hs: i32,
                     bits: *const u8, bmi: *const BITMAPINFO, usage: u32, rop: u32) -> i32;
    fn GdiFlush() -> i32;
    fn PatBlt(dc: HANDLE, x: i32, y: i32, w: i32, h: i32, rop: u32) -> i32;
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
const WM_KEYUP: u32 = 0x0101;
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
const WS_POPUP: u32 = 0x8000_0000;
const SM_CXSCREEN: i32 = 0;
const SM_CYSCREEN: i32 = 1;
const BLACKNESS: u32 = 0x0000_0042;

// ---- the instants a WndProc can reach --------------------------------------------------------
static CLICK_QPC: AtomicI64 = AtomicI64::new(0);
static DROPPED_CLICKS: AtomicU32 = AtomicU32::new(0);
static QUIT: AtomicU32 = AtomicU32::new(0);
static KEYS: AtomicU32 = AtomicU32::new(0);        // bit 0..3 = W A S D (live input, --play only)

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
        WM_KEYDOWN => {
            let bit = match wp { 0x57 => 1u32, 0x41 => 2, 0x53 => 4, 0x44 => 8, _ => 0 };
            if bit != 0 { KEYS.fetch_or(bit, Ordering::SeqCst); }
            0
        }
        WM_KEYUP => {
            let bit = match wp { 0x57 => 1u32, 0x41 => 2, 0x53 => 4, 0x44 => 8, _ => 0 };
            if bit != 0 { KEYS.fetch_and(!bit, Ordering::SeqCst); }
            0
        }
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

// ---- the world: an unbounded integer heightfield (the grid window follows the camera) ---------
const CP: i64 = 3355;              // pitch-shear reference; v0 pitch is a horizon shift
const EYE_D: i64 = 64;
const NEAR: i64 = 12;
const TILE: i64 = 3;               // world units per tile edge
const VIEW: i64 = 20;              // tiles visible in each direction from the camera tile

fn height(x: i64, y: i64) -> i64 {
    (sinq(x * 11) * 7 + sinq(y * 13) * 5) / 4096 + ((x * 73_856_093 ^ y * 19_349_663) >> 13 & 3)
}

// ---- fnv64: a DIVERGENCE DETECTOR, honestly named — not cryptographic, not an attestation ------
fn fnv64(data: &[u32], seed: u64) -> u64 {
    let mut h = 0xcbf29ce484222325u64 ^ seed;
    for &px in data {
        for b in px.to_le_bytes() {
            h ^= b as u64;
            h = h.wrapping_mul(0x100000001b3);
        }
    }
    h
}

// ---- the camera and its inputs ----------------------------------------------------------------
#[derive(Clone, Copy)]
struct Cam {
    px: i64,        // world position, Q8
    py: i64,        // world position, Q8
    yaw: i64,       // 0..4095 — a 256-step circle in 1/16 steps
    pitch: i64,     // horizon shift in pixels (v0 approximation; fpquat lands in P3.2)
}

fn step_cam(cam: &mut Cam, keys: u32, dx: i64, dy: i64) {
    cam.yaw = ((cam.yaw + dx * 3) % 4096 + 4096) % 4096;
    cam.pitch = (cam.pitch - dy * 2).clamp(-220, 220);
    let (s, c) = (sinq(cam.yaw / 16), cosq(cam.yaw / 16));
    let sp = 40i64;                                        // Q8 world units per frame
    let (mut mx, mut my) = (0i64, 0i64);
    if keys & 1 != 0 { mx += s * sp / 4096; my += c * sp / 4096 }   // W: forward
    if keys & 4 != 0 { mx -= s * sp / 4096; my -= c * sp / 4096 }   // S: back
    if keys & 2 != 0 { mx -= c * sp / 4096; my += s * sp / 4096 }   // A: strafe left
    if keys & 8 != 0 { mx += c * sp / 4096; my -= s * sp / 4096 }   // D: strafe right
    cam.px += mx;
    cam.py += my;
}

// ---- the renderer: camera-relative windowed grid, z-buffered, world-anchored checker ----------
fn raster_world(buf: &mut [u32], zbuf: &mut [i32], w: i32, h: i32, cam: &Cam) {
    let horizon = (h * 2 / 5 + cam.pitch as i32).clamp(0, h - 1);
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

    let (s, c) = (sinq(cam.yaw / 16), cosq(cam.yaw / 16));
    let f = h as i64 * 2;
    let (cx, cy) = (w as i64 / 2, h as i64 * 3 / 5 + cam.pitch);
    let (tx0, ty0) = (cam.px >> 8, cam.py >> 8);           // camera tile (world units)
    let cam_tile_x = tx0 / TILE;
    let cam_tile_y = ty0 / TILE;
    let eye_z = height(cam_tile_x, cam_tile_y) + 6;        // height-follow: feet on the terrain

    // transform the (2*VIEW+1)^2 window of vertices around the camera tile
    let side = (2 * VIEW + 1) as usize;
    let mut screen: Vec<(i64, i64, i64)> = Vec::with_capacity(side * side);
    for gy in -VIEW..=VIEW {
        for gx in -VIEW..=VIEW {
            let (wx, wy) = (cam_tile_x + gx, cam_tile_y + gy);
            let x0 = wx * TILE - (cam.px >> 8);
            let y0 = wy * TILE - (cam.py >> 8);
            let z0 = height(wx, wy) - eye_z;
            let x1 = (x0 * c - y0 * s) / 4096;
            let y1 = (x0 * s + y0 * c) / 4096;
            let d = y1 + EYE_D;
            if d < NEAR { screen.push((i64::MIN, 0, 0)); continue }
            screen.push((cx + x1 * f / d, cy - (z0 * CP / 4096) * f / d, d));
        }
    }
    let idx = |gx: i64, gy: i64| ((gy + VIEW) * (2 * VIEW + 1) + gx + VIEW) as usize;
    for gy in -VIEW..VIEW {
        for gx in -VIEW..VIEW {
            let (wx, wy) = (cam_tile_x + gx, cam_tile_y + gy);
            let h4 = height(wx, wy) + height(wx + 1, wy) + height(wx, wy + 1)
                + height(wx + 1, wy + 1);
            let checker = (((wx ^ wy) & 1) * 18) as u32;   // WORLD-anchored: movement is visible
            let g = (92 + h4 * 6) as u32 + checker;
            let g = g.min(255);
            let color = ((g / 3 + 28) << 16) | (g << 8) | (g / 4 + 18);
            let quad = [(idx(gx, gy), idx(gx + 1, gy), idx(gx, gy + 1), color),
                        (idx(gx + 1, gy), idx(gx + 1, gy + 1), idx(gx, gy + 1),
                         color.wrapping_add(0x00040404))];
            for &(ia, ib, ic, col) in &quad {
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
                            if d < zbuf[i] { zbuf[i] = d; buf[i] = col }
                        }
                    }
                }
            }
        }
    }
    let (chx, chy) = (w / 2, h / 2);
    for dd in -8i32..9 {
        if chx + dd >= 0 && chx + dd < w { buf[(chy * w + chx + dd) as usize] = 0x00FF_FFFF }
        if chy + dd >= 0 && chy + dd < h { buf[((chy + dd) * w + chx) as usize] = 0x00FF_FFFF }
    }
}

// ---- the entry door ---------------------------------------------------------------------------
struct Args {
    host: String, power: String, scheduler: String, hz: i64, frames: u32,
    res: (i32, i32), play: bool, replay: String, defect: bool, trace_out: String, out: String,
}

fn parse_argv() -> Result<Args, String> {
    let mut a = Args { host: "-".into(), power: "-".into(), scheduler: "-".into(), hz: 120,
                       frames: 1800, res: (1280, 720), play: false, replay: String::new(),
                       defect: false, trace_out: "fpsdemo_trace.txt".into(),
                       out: "fpsdemo_log.txt".into() };
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
            "--frames" => a.frames = value(&mut i)?.parse().map_err(|_| "--frames: not an integer")?,
            "--res" => {
                let v = value(&mut i)?;
                let (w, h) = v.split_once('x').ok_or("--res wants WxH")?;
                a.res = (w.parse().map_err(|_| "--res width")?,
                         h.parse().map_err(|_| "--res height")?);
            }
            "--play" => a.play = true,
            "--replay" => a.replay = value(&mut i)?,
            "--defect" => a.defect = true,
            "--trace-out" => a.trace_out = value(&mut i)?,
            "--out" => a.out = value(&mut i)?,
            other => return Err(format!("unknown flag {other} — this door refuses")),
        }
        i += 1;
    }
    if a.play == !a.replay.is_empty() {
        // both set, or neither: exactly one mode must be chosen
        return Err("choose exactly one of --play or --replay <trace>".into());
    }
    if a.defect && a.play {
        return Err("--defect is a REPLAY check: the plant needs a recorded workload".into());
    }
    if a.host != "-" && (a.power == "-" || a.scheduler == "-") {
        return Err("a named-host run without --power and --scheduler cannot pass the strict \
                    door — declare them".into());
    }
    Ok(a)
}

fn load_trace(path: &str) -> Result<Vec<(u32, i64, i64)>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("trace {path}: {e}"))?;
    let mut out = Vec::new();
    for (ln_no, ln) in text.lines().enumerate() {
        if ln.starts_with('#') || ln.trim().is_empty() { continue }
        let p: Vec<&str> = ln.split_whitespace().collect();
        if p.len() != 3 { return Err(format!("trace line {}: wants `keys dx dy`", ln_no + 1)) }
        out.push((p[0].parse().map_err(|_| "keys")?,
                  p[1].parse().map_err(|_| "dx")?,
                  p[2].parse().map_err(|_| "dy")?));
    }
    if out.is_empty() { return Err("trace is empty — nothing to replay".into()) }
    Ok(out)
}

fn main() {
    let args = match parse_argv() {
        Ok(a) => a,
        Err(e) => { eprintln!("FPSDEMO-REFUSE: {e}"); std::process::exit(2) }
    };
    let trace_in = if args.replay.is_empty() { Vec::new() }
                   else { match load_trace(&args.replay) {
                       Ok(t) => t,
                       Err(e) => { eprintln!("FPSDEMO-REFUSE: {e}"); std::process::exit(2) } } };
    let total_frames = if args.play { args.frames } else { trace_in.len() as u32 };

    let mut freq = 0i64;
    unsafe { QueryPerformanceFrequency(&mut freq) };
    assert!(freq > 0, "QPC frequency unavailable");
    let timer_1ms_granted = unsafe { timeBeginPeriod(1) } == 0;

    let inst = unsafe { GetModuleHandleW(std::ptr::null()) };
    let cls = wstr("URDR_FPSDEMO");
    let wc = WNDCLASSW {
        style: CS_OWNDC, lpfnWndProc: wndproc, cbClsExtra: 0, cbWndExtra: 0, hInstance: inst,
        hIcon: 0, hCursor: unsafe { LoadCursorW(0, IDC_ARROW) }, hbrBackground: 0,
        lpszMenuName: std::ptr::null(), lpszClassName: cls.as_ptr(),
    };
    assert!(unsafe { RegisterClassW(&wc) } != 0, "RegisterClassW failed");
    let title = wstr("urdr fpsdemo v0 — WASD + mouse, ESC to end");
    let (scr_w, scr_h) = unsafe { (GetSystemMetrics(SM_CXSCREEN), GetSystemMetrics(SM_CYSCREEN)) };
    let (cw, ch) = args.res;
    if cw > scr_w || ch > scr_h {
        eprintln!("FPSDEMO-REFUSE: {cw}x{ch} exceeds the {scr_w}x{scr_h} screen — a clipped 1:1 \
                   blit measures a different operation");
        std::process::exit(2);
    }
    let hwnd = unsafe {
        CreateWindowExW(0, cls.as_ptr(), title.as_ptr(), WS_POPUP | WS_VISIBLE,
                        0, 0, scr_w, scr_h, 0, 0, inst, 0)
    };
    assert!(hwnd != 0, "CreateWindowExW failed");
    unsafe { ShowWindow(hwnd, SW_SHOW) };
    let dc = unsafe { GetDC(hwnd) };
    unsafe { PatBlt(dc, 0, 0, scr_w, scr_h, BLACKNESS); }
    if args.play { unsafe { ShowCursor(0); } }

    let mut buf = vec![0u32; (cw * ch) as usize];
    let mut buf_planted = if args.defect { vec![0u32; (cw * ch) as usize] } else { Vec::new() };
    let mut zbuf = vec![0i32; (cw * ch) as usize];
    let bmi = BITMAPINFO {
        bmiHeader: BITMAPINFOHEADER {
            biSize: std::mem::size_of::<BITMAPINFOHEADER>() as u32,
            biWidth: cw, biHeight: -ch, biPlanes: 1, biBitCount: 32, biCompression: 0,
            biSizeImage: 0, biXPelsPerMeter: 0, biYPelsPerMeter: 0,
            biClrUsed: 0, biClrImportant: 0,
        },
        bmiColors: [0; 3],
    };

    let frame_ns: i64 = 1_000_000_000 / args.hz;
    let ticks_per_frame = frame_ns * freq / 1_000_000_000;
    let seg: u32 = 120;
    let n_segments = (total_frames + seg - 1) / seg;
    let mut seg_raster: Vec<Vec<i64>> = (0..n_segments).map(|_| Vec::new()).collect();
    let mut seg_present: Vec<Vec<i64>> = (0..n_segments).map(|_| Vec::new()).collect();
    let mut seg_late = vec![0u32; n_segments as usize];
    let mut late_ns: Vec<i64> = Vec::with_capacity(total_frames as usize);
    let mut trace_rec: Vec<(u32, i64, i64)> = Vec::new();
    let mut digests: Vec<(u32, u64)> = Vec::new();
    let mut digests_planted: Vec<(u32, u64)> = Vec::new();
    const PLANT_FRAME: u32 = 600;

    let mut cam = Cam { px: 0, py: 0, yaw: 0, pitch: 0 };
    let (center_x, center_y) = (scr_w / 2, scr_h / 2);
    if args.play { unsafe { SetCursorPos(center_x, center_y); } }
    let mut deadline = qpc() + ticks_per_frame;

    let mut frame: u32 = 0;
    while frame < total_frames && QUIT.load(Ordering::SeqCst) == 0 {
        let seg_idx = (frame / seg) as usize;
        let mut msg = MSG { hwnd: 0, message: 0, wParam: 0, lParam: 0, time: 0,
                            pt: POINT { x: 0, y: 0 } };
        unsafe {
            while PeekMessageW(&mut msg, 0, 0, 0, PM_REMOVE) != 0 {
                if msg.message == WM_QUIT { QUIT.store(1, Ordering::SeqCst); break }
                TranslateMessage(&msg);
                DispatchMessageW(&msg);
            }
        }
        // THE INPUT: live devices in --play (and RECORDED), the trace in --replay.
        let (keys, dx, dy) = if args.play {
            let mut pt = POINT { x: 0, y: 0 };
            unsafe { GetCursorPos(&mut pt); SetCursorPos(center_x, center_y); }
            let k = KEYS.load(Ordering::SeqCst);
            let (mdx, mdy) = ((pt.x - center_x) as i64, (pt.y - center_y) as i64);
            trace_rec.push((k, mdx, mdy));
            (k, mdx, mdy)
        } else {
            trace_in[frame as usize]
        };

        let _t0 = qpc();
        step_cam(&mut cam, keys, dx, dy);                  // the sim tick
        let _t_tick = qpc();
        let _view = (cam.px, cam.py, cam.yaw, cam.pitch);  // the view export
        let t_view = qpc();
        raster_world(&mut buf, &mut zbuf, cw, ch, &cam);
        let t_pixels = qpc();
        unsafe {
            StretchDIBits(dc, (scr_w - cw) / 2, (scr_h - ch) / 2, cw, ch,
                          0, 0, cw, ch, buf.as_ptr() as *const u8,
                          &bmi, DIB_RGB_COLORS, SRCCOPY);
            GdiFlush();
        }
        let t_present = qpc();

        seg_raster[seg_idx].push(ticks_to_ns(t_pixels - t_view, freq));
        seg_present[seg_idx].push(ticks_to_ns(t_present - t_pixels, freq));

        // THE DIGEST CHAIN (replay only): byte-identity, checked not hoped. In defect mode a COPY
        // carries one flipped byte from PLANT_FRAME on — clean and planted chains must match
        // before the plant and diverge at it, in ONE run, no baseline needed.
        if !args.replay.is_empty() {
            if args.defect {
                buf_planted.copy_from_slice(&buf);
                if frame >= PLANT_FRAME { buf_planted[0] ^= 1 }
            }
            if frame % 60 == 59 || frame + 1 == total_frames {
                digests.push((frame, fnv64(&buf, 0)));
                if args.defect { digests_planted.push((frame, fnv64(&buf_planted, 0))); }
            }
        }

        loop {
            let now = qpc();
            if now >= deadline {
                let late = ticks_to_ns(now - deadline, freq);
                late_ns.push(late);
                if late > 1_000_000 { seg_late[seg_idx] += 1 }
                break;
            }
            if ticks_to_ns(deadline - now, freq) > 4_000_000 { unsafe { Sleep(1) } }
        }
        deadline += ticks_per_frame;
        frame += 1;
    }
    unsafe { timeEndPeriod(1) };
    if args.play { unsafe { ShowCursor(1); } }

    if args.play {
        let mut t = String::from("# fpsdemo v0 input trace: keys dx dy (one line per frame)\n");
        for (k, dx, dy) in &trace_rec {
            t.push_str(&format!("{} {} {}\n", k, dx, dy));
        }
        std::fs::write(&args.trace_out, &t).expect("trace write failed");
    }

    late_ns.sort_unstable();
    let (l50, l95, l99) = (pct(&late_ns, 50), pct(&late_ns, 95), pct(&late_ns, 99));
    let late_over = late_ns.iter().filter(|&&l| l > 1_000_000).count();
    let mut log = String::new();
    log.push_str(&format!(
        "fpsdemo v0 | host {} | power {} | scheduler {} | hz {} | res {}x{} | mode {} | qpf {}\n",
        args.host, args.power, args.scheduler, args.hz, cw, ch,
        if args.play { "play" } else { "replay" }, freq));
    log.push_str(&format!("timer_1ms_granted {}\n", timer_1ms_granted));
    log.push_str(&format!("frames {} | late_over_1ms {} | seg {}\n", late_ns.len(), late_over, seg));
    log.push_str(&format!("late_ns p50 {} p95 {} p99 {}\n", l50, l95, l99));
    for si in 0..n_segments as usize {
        let mut v = seg_raster[si].clone();
        if v.is_empty() { continue }
        v.sort_unstable();
        let mut pv = seg_present[si].clone();
        pv.sort_unstable();
        log.push_str(&format!(
            "seg {} n {} raster_ns {} {} {} present_ns {} {} {} late {}\n",
            si, v.len(), v[0], pct(&v, 50), v[v.len() - 1],
            pv[0], pct(&pv, 50), pv[pv.len() - 1], seg_late[si]));
    }
    for (fr, d) in &digests {
        log.push_str(&format!("digest frame {} fnv64 {:016x}\n", fr, d));
    }
    if args.play {
        log.push_str(&format!("trace {} frames -> {}\n", trace_rec.len(), args.trace_out));
    }
    if args.host == "-" {
        log.push_str("NOTE: no --host given — cost rows here are NOT_MEASURED; digests are \
                      host-independent and stand\n");
    }
    std::fs::write(&args.out, &log).expect("log write failed");
    print!("{log}");

    if args.defect {
        let mut matched_before = true;
        let mut diverged_at: Option<u32> = None;
        for (i, &(fr, d)) in digests.iter().enumerate() {
            let (_pf, pd) = digests_planted[i];
            if fr < PLANT_FRAME {
                if d != pd { matched_before = false }
            } else if d != pd {
                diverged_at.get_or_insert(fr);
            }
        }
        match (matched_before, diverged_at) {
            (true, Some(fr)) => {
                println!("DEFECT CAUGHT: clean and planted chains matched before frame {} and \
                          DIVERGED AT frame {}", PLANT_FRAME, fr);
            }
            _ => {
                println!("DEFECT MISSED: matched_before={} diverged_at={:?} — a digest that \
                          cannot see one flipped byte certifies nothing", matched_before,
                         diverged_at);
                std::process::exit(1);
            }
        }
    }
}

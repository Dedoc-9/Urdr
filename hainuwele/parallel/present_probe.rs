// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// present_probe.rs — THE FIRST §3 INSTRUMENT: a real window, a real present loop, and QPC
// timestamps at every sealframe instant the software can reach (URDRPRS1, probe v0.1).
//
// WHY THIS FILE EXISTS. sealframe's SEGMENTS partition tiles input_actuation -> photon across
// seven instants, and today three segments read NOT_MEASURED with the note "the layer-3 renderer
// does not exist": frame_render, present_queue, input_to_photon. The tree's standing law forbids
// latency optimization without a measured latency target, so nothing about the FPS demo may be
// "optimized" until this instrument has run ONCE on the named host and produced a §3 log. This is
// that instrument, and deliberately nothing more.
//
// WHAT IT IS NOT. Not the demo, not the renderer, not gated, and not deterministic — it reads a
// wall clock, so it lives in the same class as bench.py: DELIBERATELY UNGATED, wall-clock
// MEASURED-on-named-host only, and it CAN rot. The repo-side admission door for its log comes
// AFTER a log exists (measure before deciding, L44: carry the denominator).
//
// THE HOUSE RULES IT KEEPS ANYWAY:
//   * std-only, no cargo, no crates — raw Win32 FFI, the urdr_render_rs precedent;
//   * integer arithmetic only — every duration is i64 nanoseconds, percentile = lower middle
//     (repeat.py's convention), no float anywhere;
//   * the entry point REFUSES unknown flags and flag-swallowing (entry, URDRENT1);
//   * red-first: --defect plants a 50 ms stall in the raster stage and the run exits 0 ONLY if
//     the instrument's own numbers catch it — an instrument that cannot see a planted 50 ms has
//     no business reporting 5 (L23);
//   * a log without --host carries "host -" and the repo side must grade it NOT_MEASURED —
//     an anonymous log cannot graduate a MEASURED claim (sealframe-honesty).
//
// THE SEGMENT CHAIN, per frame (sealframe instant names):
//   input_visible   QPC taken inside WndProc at WM_LBUTTONDOWN dispatch (the first instant
//                   software can see; actuation -> visible stays external-capture: film the
//                   button and the white flash with a 120/240fps phone camera, Blur Busters
//                   method — the flash below exists exactly for that camera)
//   tick_done       after the sim update
//   view_exported   after the draw-list build
//   pixels_done     after the software raster into the DIB
//   present_queued  after StretchDIBits + GdiFlush return
// On every click the probe flashes the full frame white for 8 frames and logs the 5-segment
// chain for that click in ns. photon itself is the camera's to measure, never QPC's.
//
// RUN PROTOCOL (PowerShell, repo root, rustc >= 1.58, RED FIRST):
//   rustc -O --edition 2021 -o present_probe.exe hainuwele\parallel\present_probe.rs
//   .\present_probe.exe --defect --frames 240         # must print DEFECT CAUGHT, exit 0 (~12 s)
//   .\present_probe.exe --host "ROG-Ally-X-Z2-Extreme" --hz 120 --frames 3600
//   # click ~20 times spread over the run; ESC or frame budget ends it; log: present_probe_log.txt
//   # A RUN WITH AN EMPTY CLICK TABLE IS NOT COMPLETE — the segment chain needs clicks
//   # run it TWICE and keep both logs — run-to-run spread is data, not noise (repeat, URDRRPT1)
//
// v0.1 (same day) — THE INSTRUMENT'S FIRST CATCH WAS ITSELF. The named host's first run showed
// frame work of p50 0.50 ms in an 8.33 ms slot and STILL missed 176 of 723 deadlines — a pacing
// defect, not a work defect: Sleep(1) at Windows' default ~15.6 ms timer resolution overshoots the
// whole slot. v0.1 requests 1 ms resolution (winmm timeBeginPeriod), LOGS whether it was granted,
// widens the spin window, and replaces the binary missed count with late-by percentiles, because a
// count without a magnitude hides exactly this defect (L44). ALSO LEARNED: a run with an empty
// click table measures only the frame loop — the run is NOT COMPLETE until click chains are
// non-empty, so the protocol below says so in its own line.
//
// GRADE (honest, D5): the FILE existing is DECLARED. Every number it will print is NOT_MEASURED
// until the named host runs it — this was authored on a Linux container with no Windows, no
// display and no rustc target for it, so like urdr_render_rs at birth it is SPECULATIVE until
// the red-first protocol above is green on the Ally X. declared != verified.

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
    fn SetWindowTextW(h: HANDLE, t: *const u16) -> i32;
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
static CLICK_QPC: AtomicI64 = AtomicI64::new(0);   // latest un-consumed WM_LBUTTONDOWN, QPC ticks
static DROPPED_CLICKS: AtomicU32 = AtomicU32::new(0);
static QUIT: AtomicU32 = AtomicU32::new(0);

fn qpc() -> i64 { let mut v = 0i64; unsafe { QueryPerformanceCounter(&mut v) }; v }

extern "system" fn wndproc(h: HANDLE, m: u32, wp: usize, lp: isize) -> isize {
    match m {
        WM_LBUTTONDOWN => {
            // THE input_visible INSTANT: the earliest moment software can stamp this click.
            let t = qpc();
            if CLICK_QPC.compare_exchange(0, t, Ordering::SeqCst, Ordering::SeqCst).is_err() {
                DROPPED_CLICKS.fetch_add(1, Ordering::SeqCst);   // counted, never silently lost (L44)
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

/// Percentile by rank, LOWER MIDDLE — repeat.py's integer convention. No interpolation, no float.
fn pct(sorted: &[i64], p: usize) -> i64 {
    if sorted.is_empty() { return -1 }
    sorted[(sorted.len() - 1) * p / 100]
}

// ---- the entry door: refuses, like every door in this tree (URDRENT1) ------------------------
struct Args { host: String, hz: i64, frames: u32, defect: bool, out: String }

fn parse_argv() -> Result<Args, String> {
    let mut a = Args { host: "-".into(), hz: 120, frames: 3600, defect: false,
                       out: "present_probe_log.txt".into() };
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
            "--hz" => a.hz = value(&mut i)?.parse().map_err(|_| "--hz: not an integer")?,
            "--frames" => a.frames = value(&mut i)?.parse().map_err(|_| "--frames: not an integer")?,
            "--out" => a.out = value(&mut i)?,
            "--defect" => a.defect = true,
            other => return Err(format!("unknown flag {other} — this door refuses")),
        }
        i += 1;
    }
    if a.hz < 1 || a.hz > 1000 { return Err("--hz out of [1,1000]".into()) }
    Ok(a)
}

// ---- the raster: cheap, integer, game-shaped enough to pace like a frame ---------------------
fn raster(buf: &mut [u32], w: i32, h: i32, tick: u32, flash: bool, defect: bool) {
    if defect { unsafe { Sleep(50) } }                 // THE PLANT: 50 ms the numbers must catch
    if flash { for p in buf.iter_mut() { *p = 0x00FF_FFFF } return }
    let horizon = h * 2 / 5;
    for y in 0..h {
        let base: u32 = if y < horizon {
            let t = (y * 255 / horizon.max(1)) as u32;           // sky gradient
            (40 << 16) | ((60 + t / 3) << 8) | (120 + t / 2).min(255)
        } else {
            let d = y - horizon;                                  // ground: fake-perspective bands
            let band = if d > 0 && (h - horizon) / d % 2 == 0 { 70 } else { 45 };
            (band << 16) | ((band + 20) << 8) | band
        };
        let row = (y * w) as usize;
        for x in 0..w { buf[row + x as usize] = base }
    }
    let bar_x = ((tick as i32 * 7) % (w.max(1))).max(0);          // the strafe target
    for y in horizon - 60..horizon + 20 {
        if y < 0 || y >= h { continue }
        for x in bar_x..(bar_x + 24).min(w) {
            buf[(y * w + x) as usize] = 0x00E0_4030;
        }
    }
    let (cx, cy) = (w / 2, h / 2);                                // crosshair
    for d in -8i32..9 {
        if cx + d >= 0 && cx + d < w { buf[(cy * w + cx + d) as usize] = 0x00FF_FFFF }
        if cy + d >= 0 && cy + d < h { buf[((cy + d) * w + cx) as usize] = 0x00FF_FFFF }
    }
}

fn main() {
    let args = match parse_argv() {
        Ok(a) => a,
        Err(e) => { eprintln!("PRESENT-REFUSE: {e}"); std::process::exit(2) }
    };
    let mut freq = 0i64;
    unsafe { QueryPerformanceFrequency(&mut freq) };
    assert!(freq > 0, "QPC frequency unavailable");
    // v0.1: Sleep(1) under the default ~15.6 ms timer resolution overshoots a 120 Hz slot whole.
    let timer_1ms_granted = unsafe { timeBeginPeriod(1) } == 0;

    let inst = unsafe { GetModuleHandleW(std::ptr::null()) };
    let cls = wstr("URDR_PRESENT_PROBE");
    let wc = WNDCLASSW {
        style: CS_OWNDC, lpfnWndProc: wndproc, cbClsExtra: 0, cbWndExtra: 0, hInstance: inst,
        hIcon: 0, hCursor: unsafe { LoadCursorW(0, IDC_ARROW) }, hbrBackground: 0,
        lpszMenuName: std::ptr::null(), lpszClassName: cls.as_ptr(),
    };
    assert!(unsafe { RegisterClassW(&wc) } != 0, "RegisterClassW failed");
    let title = wstr("urdr present probe — click to flash, ESC to end");
    let hwnd = unsafe {
        CreateWindowExW(0, cls.as_ptr(), title.as_ptr(), WS_OVERLAPPEDWINDOW | WS_VISIBLE,
                        100, 100, 1296, 768, 0, 0, inst, 0)
    };
    assert!(hwnd != 0, "CreateWindowExW failed");
    unsafe { ShowWindow(hwnd, SW_SHOW) };
    let dc = unsafe { GetDC(hwnd) };
    let mut rc = RECT { left: 0, top: 0, right: 0, bottom: 0 };
    unsafe { GetClientRect(hwnd, &mut rc) };
    let (w, h) = (rc.right - rc.left, rc.bottom - rc.top);
    assert!(w > 0 && h > 0, "empty client area");
    let mut buf = vec![0u32; (w * h) as usize];
    let bmi = BITMAPINFO {
        bmiHeader: BITMAPINFOHEADER {
            biSize: std::mem::size_of::<BITMAPINFOHEADER>() as u32,
            biWidth: w, biHeight: -h, biPlanes: 1, biBitCount: 32, biCompression: 0,
            biSizeImage: 0, biXPelsPerMeter: 0, biYPelsPerMeter: 0, biClrUsed: 0, biClrImportant: 0,
        },
        bmiColors: [0; 3],
    };

    let frame_ns: i64 = 1_000_000_000 / args.hz;
    let mut frame_totals: Vec<i64> = Vec::with_capacity(args.frames as usize);
    let mut clicks: Vec<(i64, i64, i64, i64, i64)> = Vec::new();   // the 5-segment chain, ns
    let mut late_ns: Vec<i64> = Vec::with_capacity(args.frames as usize);
    let mut flash_left: u32 = 0;
    let mut deadline = qpc() + frame_ns * freq / 1_000_000_000;

    let mut tick: u32 = 0;
    while tick < args.frames && QUIT.load(Ordering::SeqCst) == 0 {
        let mut msg = MSG { hwnd: 0, message: 0, wParam: 0, lParam: 0, time: 0,
                            pt: POINT { x: 0, y: 0 } };
        unsafe {
            while PeekMessageW(&mut msg, 0, 0, 0, PM_REMOVE) != 0 {
                if msg.message == WM_QUIT { QUIT.store(1, Ordering::SeqCst); break }
                TranslateMessage(&msg);
                DispatchMessageW(&msg);
            }
        }
        let click = CLICK_QPC.swap(0, Ordering::SeqCst);           // consume exactly one
        let t_input = if click != 0 && flash_left == 0 { click } else { 0 };
        if t_input != 0 { flash_left = 8 }
        let flash = flash_left > 0;

        let t0 = qpc();                                            // frame start
        tick = tick.wrapping_add(1);                               // the sim: trivial by design
        let t_tick = qpc();                                        // tick_done
        let _drawlist = (tick, flash);                             // the view export: trivial
        let t_view = qpc();                                        // view_exported
        raster(&mut buf, w, h, tick, flash, args.defect);
        let t_pixels = qpc();                                      // pixels_done
        unsafe {
            StretchDIBits(dc, 0, 0, w, h, 0, 0, w, h, buf.as_ptr() as *const u8,
                          &bmi, DIB_RGB_COLORS, SRCCOPY);
            GdiFlush();
        }
        let t_present = qpc();                                     // present_queued
        if flash_left > 0 { flash_left -= 1 }

        if t_input != 0 {
            clicks.push((ticks_to_ns(t0 - t_input, freq),          // input_visible -> frame start
                         ticks_to_ns(t_tick - t0, freq),           // authority_tick
                         ticks_to_ns(t_view - t_tick, freq),       // view_export
                         ticks_to_ns(t_pixels - t_view, freq),     // frame_render
                         ticks_to_ns(t_present - t_pixels, freq)));// present_queue
        }
        frame_totals.push(ticks_to_ns(t_present - t0, freq));

        // pacing: coarse sleep only while >4 ms remain (1 ms granted resolution makes Sleep(1)
        // ~1-2 ms), then spin; the overshoot is RECORDED as a magnitude, never a bare count (L44)
        loop {
            let now = qpc();
            if now >= deadline { late_ns.push(ticks_to_ns(now - deadline, freq)); break }
            if ticks_to_ns(deadline - now, freq) > 4_000_000 { unsafe { Sleep(1) } }
        }
        deadline += frame_ns * freq / 1_000_000_000;
    }

    unsafe { timeEndPeriod(1) };
    frame_totals.sort_unstable();
    let (p50, p95, p99) = (pct(&frame_totals, 50), pct(&frame_totals, 95), pct(&frame_totals, 99));
    let missed = late_ns.iter().filter(|&&l| l > 1_000_000).count();
    late_ns.sort_unstable();
    let (l50, l95, l99) = (pct(&late_ns, 50), pct(&late_ns, 95), pct(&late_ns, 99));

    let mut log = String::new();
    log.push_str(&format!("present_probe v0.1 | host {} | hz {} | {}x{} | qpf {}\n",
                          args.host, args.hz, w, h, freq));
    log.push_str(&format!("timer_1ms_granted {}\n", timer_1ms_granted));
    log.push_str(&format!("frames {} | late_over_1ms {} | dropped_clicks {}\n",
                          frame_totals.len(), missed, DROPPED_CLICKS.load(Ordering::SeqCst)));
    log.push_str(&format!("late_ns p50 {} p95 {} p99 {}\n", l50, l95, l99));
    log.push_str(&format!("frame_total_ns p50 {} p95 {} p99 {} | budget_ns {}\n", p50, p95, p99, frame_ns));
    log.push_str("click chains (ns): input_wait authority_tick view_export frame_render present_queue total\n");
    for (a, b, c, d, e) in &clicks {
        log.push_str(&format!("{} {} {} {} {} {}\n", a, b, c, d, e, a + b + c + d + e));
    }
    if args.host == "-" {
        log.push_str("NOTE: no --host given — this log is NOT_MEASURED by sealframe-honesty; rerun with --host\n");
    }
    std::fs::write(&args.out, &log).expect("log write failed");
    print!("{log}");

    if args.defect {
        // RED-FIRST: exit 0 iff the planted 50 ms is VISIBLE in this instrument's own numbers.
        if p50 > 40_000_000 { println!("DEFECT CAUGHT: p50 {} ns > 40ms with planted 50ms stall", p50); }
        else { println!("DEFECT MISSED: p50 {} ns — the instrument cannot see 50ms; do not trust it", p50);
               std::process::exit(1) }
    }
}

// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// fpsdemo.rs — THE CONFORMANCE CAMERA AND THE CANON TERRAIN (URDRFPD1, v1.6).
//
// v1.6 — P3.4 OPENS: THE FIRST FIDELITY SPEND, CHOSEN BY PICTURES AND PRICED BEFORE PURCHASE.
// Candidate 1 (height bands + integer lambert sun) was rendered against the COMMITTED real-walk
// workload in the headless harness before this file changed: the band anchors come from a
// measured height histogram, not taste; the lighting is a per-triangle integer normal against a
// fixed sun; everything is VIEW-layer (the canon heights and certified camera untouched — the
// selfcheck door still holds them to the placements' goldens at every launch). Its price on the
// identical committed workload measured statistically ZERO on the authoring container; the
// honest number is the host A/B this protocol runs: the committed v1.5 named log is the BEFORE,
// this build's named replay of the SAME walk_real trace is the AFTER. Digest chains change with
// the pixels (version-bound, as always); the committed v1.1-v1.5 chain records remain valid
// records OF THAT RENDER PATH, and the v1.6 expected chain for walk_real ships in the delivery
// notes, produced cross-OS before this file reached the host.
//
// v1.5 — THE END KEY THAT STARTS THE PROGRAM. The first attempted real walk lasted ONE frame:
// v1.4 added Enter to the end-run set, and Enter is the key that launches the program from a
// shell — still physically down at frame 0's poll, so the run ended at birth, caught by the
// activity line (frames 1 | keyed 0). The law: LAUNCH-TIME INPUT STATE MUST NOT LEAK INTO THE
// RUN. End keys and end buttons are now ARMED by an observed release — ending requires a press
// that BEGAN after launch. Movement keys need no arming (holding W at launch is a walk, not a
// command). Render path untouched; all pinned chains stand.
//
// v1.4 — THE LOOK ARRIVED; THE WALK GETS ITS LAST ALIAS. The v1.3 run was the input arc's
// first partial success and its most precise measurement: pad_connected TRUE, padded 0,
// moused 1386. Read together: the vendor layer holds the PHYSICAL sticks and emits DESKTOP
// vocabulary — the right stick became the mouse (that is the 1386, and the operator's pan
// replayed cross-OS 30/30 as trace #3), while the XInput device it exposes reads idle. In
// that same desktop scheme the LEFT stick emits ARROW KEYS — the one vocabulary the demo did
// not poll. v1.4 aliases arrows onto WASD bits and Enter onto the end-run set, so the walk
// arrives on whatever the machine speaks: WASD or arrows, mouse or stick-mouse, pad if the
// native channel ever wakes. All of it lands in the same trace bits; replay is unchanged.
//
// v1.3 — THE THIRD DEATH IDENTIFIED THE MACHINE. Three recordings, one matrix: v0 (no foreground
// attempt) came back moused 800; v1.1 and v1.2 (foreground attempted, then verifiably TAKEN —
// focus_foreground true) came back moused 0, keyed 0, and no Esc ever landed. Polling was not
// the missing piece; the DEVICE was. The named host is a ROG Ally X — a HANDHELD: its sticks
// emulate a mouse only while the desktop is foreground, and the vendor layer swaps them to
// GAMEPAD mode the moment a fullscreen app takes focus. v1.2's one verified success — taking
// the foreground — is exactly what unplugged the operator's only pointing device. The keyboard
// was never dead; it was never there. v1.3 reads the machine's NATIVE channel: XInput, loaded
// at runtime (absence is a reported condition, not a link failure), polled beside the keyboard
// and mouse every frame — left stick walks, right stick looks, B or Start ends the run — and
// every channel merges into the SAME trace vocabulary (keys dx dy), so replay neither knows nor
// cares which device recorded. The activity line grows `padded`; the conditions line grows
// `xinput_loaded | pad_connected`. The render path is UNTOUCHED: both pinned cross-OS chains
// (v0-trace 8d4c25e0../ae4493b9.., all-zero e224235741921d0f) stand.
//
// v1.2 — THE KEYBOARD DIED TWICE, AND THE SECOND DEATH REFUTED THE FIRST REPAIR. v1.1's
// SetForegroundWindow fix was reasoned from documentation; the host measured it: the v1.2-era
// recording came back `keyed 0 | moused 0` — the instrument's own activity line, doing its job
// on its first outing. The durable diagnosis was the ASYMMETRY: the mouse survived v1 because
// GetCursorPos POLLS global state, focus-free; the keyboard died because WM_KEYDOWN is QUEUED
// and only a focused window receives it — and Windows is entitled to refuse a console-spawned
// process the foreground. v1.2 stops depending on what Windows may refuse: WASD and Esc are
// POLLED via GetAsyncKeyState (the keyboard's GetCursorPos), the window is TOPMOST so the
// operator sees what they steer, and focus becomes a REPORTED CONDITION (`focus_foreground`
// beside `timer_1ms_granted`) instead of a dependency. The render path is UNTOUCHED: the
// pinned v0-trace chain (8d4c25e0.. / ae4493b9..) and the all-zero-trace constant
// (e224235741921d0f) remain the cross-OS conformance references — both were reproduced on the
// authoring container from the operator's own v1.1 run before this repair was written.
//
// CROSS-OS DETERMINISM IS NOW MEASURED, NOT DECLARED: the operator's Windows build and the
// authoring container's Linux build printed identical digest chains on two different traces
// (30 checkpoints on the v0 recording, 30 on the all-zero walk) — 60 checkpoints, two OSes,
// two compilers' codegen, zero divergence. That is the integer-only pipeline earning its keep.
//
// v1.1 — WHAT FIRST HOST CONTACT FOUND, AND WHAT A HEADLESS REPLAY OF IT FIXED. The operator's
// v1 run came back green on every claim v1 made — door, chains, plant — and wrong on the one
// surface v1 could not check: the picture. The screenshots showed a thin green-and-magenta
// ribbon floating in sky. The v1 trace bytes were then replayed HEADLESSLY on the authoring
// container (the math slice compiles anywhere; only the Win32 shell is host-bound), the 30-digest
// chain matched the operator's run bit for bit — so the replayed frames ARE the operator's
// frames — and the defects fell out as measurements, not guesses:
//
//   * THE FLOOR WAS BACKFACE-CULLED. `area > 0` kept one winding; ground below eye level winds
//     the other way in screen space (y grows downward), so the demo culled the entire floor of
//     its own world. The ribbon was the set of far faces steep enough to survive. Terrain the
//     camera walks on is two-sided now.
//   * THE MAGENTA WAS A BYTE CARRY. wrapping_add(0x040404) on a packed color with a saturated
//     green byte carried into red (255+4 = 0x103): every second triangle collapsed to magenta.
//     And 92+h4*6 pinned everything above half height to one flat 255, erasing the relief the
//     canon computes. Colors are per-channel now, full range, depth-fogged toward the sky band.
//   * THE KEYBOARD NEVER ARRIVED. The v1 trace: 1800 frames, 0 keyed, 800 moused, no Esc exit —
//     mouse-look POLLS the global cursor and works unfocused; WM_KEYDOWN rides the message
//     queue, and a WS_POPUP window from a console process does not take focus from the console.
//     v1.1 takes focus explicitly and the --play summary prints keyed/moused counts, so an
//     input channel that went missing is a LINE IN THE LOG, not a mystery in a file.
//   * A WALK NOBODY HAD TAKEN WAS ALREADY BROKEN. A synthetic walk trace through the headless
//     harness showed the render path truncating the camera to INTEGER world units (a moving view
//     snapped once per ~7 frames) and the eye stepping discretely at tile edges. Deltas are Q8
//     end to end now, the eye stands on bilinearly interpolated ground, and the near clip is 2
//     units (v1's 12-unit clip deleted the four nearest rings of ground).
//   * THE FILL IS PAID FOR HONESTLY. Two-sided terrain rasterizes real coverage; the pixel loop
//     dropped its per-pixel multiplies (incremental edge functions) and its per-pixel division
//     (exact quotient/remainder stepping) — both proved BIT-IDENTICAL against the closed form
//     on the full v1-trace chain before adoption. ~2.9x on the authoring container.
//   * A RECORD IS NOT A SCRATCH PATH. v1's default --trace-out was the exact filename of the
//     operator's only recorded workload; one bare `--play` would have replaced it. --play now
//     REFUSES an existing trace path.
//
// v1 (unchanged below):
// v0 established the replay properties on the named host: thirty digest checkpoints identical
// across three replays of one recorded walk, the planted byte caught in one run, and the moving
// workload inside the measured 720p envelope. v1 changes what the pixels ARE:
//
//   * THE CAMERA IS THE CERTIFIED MATH. The Q32.32 quaternion substrate below — Fx, rdiv with
//     round-to-nearest ties-away, the i64 refuse ceiling, qmul/qnormalize/vrotate/rsqrt — is
//     LIFTED VERBATIM from tools/frontfps/fpquat_rs (URDRFPQ1, third placement), and the demo
//     runs that placement's 66-row battery AT EVERY LAUNCH, comparing bit-for-bit against the
//     same GOLDEN the gate pins. Mouse-look is real rotation now (yaw in the world frame, pitch
//     in the local frame, small-angle increments renormalized each frame; the horizon-shift
//     approximation is gone), and WASD walks the rotated ground plane.
//   * THE TERRAIN IS THE CANON. The URDRHF1 machinery — seeded SHA lattice, Q16 quintic fade,
//     floor-division value noise — is LIFTED VERBATIM from tools/terrain/heightfield_rs, and the
//     demo reproduces all three pinned canon scenes (island / blank / mountains) at launch,
//     digest-for-digest. The world is the canon "mountains" parameter set sampled over UNBOUNDED
//     coordinates: the one edit is floored divmod in noise16, identical on the canon domain —
//     and the selfcheck reproducing the canon digests through the edited function IS the proof.
//     Heights arrive through a cache; first-visit tiles cost SHA evaluations, and that cost is
//     REAL streaming cost the rows will show.
//   * A LAUNCH THAT FAILS ITS SELFCHECK REFUSES TO RUN. Conformance is the door, not a comment.
//
// Vertical scale (canon heights 0..420 -> world units /24) and mouse sensitivity are DECLARED
// view/input constants; they touch presentation, never the certified kernels. fppose/fpclip
// integration and the committed workload-record rung are P3.2b.
//
// RUN PROTOCOL (PowerShell, repo root, rustc >= 1.58, RED FIRST). The v0 trace is an EVIDENCE
// ARTIFACT — leave fpsdemo_trace.txt where it is; --play refuses to overwrite it, and the first
// replay below is the CROSS-OS CHECK: the expected chain for the old trace under this build was
// produced on the authoring container and is pinned in the delivery notes — a Windows run must
// reproduce it digest for digest, or the demo's determinism claim dies right there.
//   rustc -O --edition 2021 -o fpsdemo.exe hainuwele\parallel\fpsdemo.rs
//   .\fpsdemo.exe --selfcheck                              # battery + 3 canon scenes, exit 0
//   .\fpsdemo.exe --replay fpsdemo_trace.txt               # v0 trace: chain must match the pin
//   .\fpsdemo.exe --play --trace-out walk_v14.txt          # LEFT stick (arrows) walks, RIGHT stick (mouse) looks; Esc/Enter/B/Start ends
//   .\fpsdemo.exe --replay walk_v14.txt                    # twice — chains must be IDENTICAL
//   .\fpsdemo.exe --replay walk_v14.txt                    #
//   .\fpsdemo.exe --replay walk_v14.txt --defect           # DIVERGED AT the plant, exit 0
//   .\fpsdemo.exe --replay walk_v14.txt --host "ROG-Ally-X-Z2-Extreme" `
//                  --power "Turbo-35W-AC" --scheduler "Win11-GameMode-UltimatePerf"
//
// GRADE (honest, D5): the lifted kernels are the placements' bytes and the selfcheck holds them
// to the placements' goldens at every start — re-run green on the authoring container for
// v1.2. The RENDER PATH is MEASURED across OSes (60 identical digest checkpoints on two
// traces) and its cost is MEASURED on the named host at the v1.1 rung: raster med ~2.0-2.4 ms
// worst 3.1 ms, present med ~0.28 ms at 720p — inside the 8.33 ms slot with the first-frame
// cold-start outlier (~15 ms) named and excluded as a start condition, not a steady state.
// v1.1's focus repair was REFUTED BY MEASUREMENT and v1.2's polling was too — not wrong,
// aimed at a device the machine does not have. What remains SPECULATIVE: the XInput path on
// THIS host (Armoury Crate may intercept even the native channel in some modes — pad_connected
// answers that in one run), the stick mapping FEEL, and every cost row of the walk that has
// still never happened.
// declared != verified; a green gate never certified a picture.

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
    fn SetForegroundWindow(h: HANDLE) -> i32;
    fn SetFocus(h: HANDLE) -> HANDLE;
    fn GetForegroundWindow() -> HANDLE;
    fn GetAsyncKeyState(vk: i32) -> i16;
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
    fn LoadLibraryW(n: *const u16) -> HANDLE;
    fn GetProcAddress(h: HANDLE, name: *const u8) -> usize;
}

// ---- XInput, loaded at runtime (the handheld's native channel; absence is a condition) --------
#[repr(C)]
#[derive(Clone, Copy, Default)]
struct XiGamepad { buttons: u16, lt: u8, rt: u8, lx: i16, ly: i16, rx: i16, ry: i16 }
#[repr(C)]
#[derive(Clone, Copy, Default)]
struct XiState { packet: u32, pad: XiGamepad }
type XiGetState = unsafe extern "system" fn(u32, *mut XiState) -> u32;

fn xinput_load() -> Option<XiGetState> {
    for dll in ["xinput1_4.dll", "xinput9_1_0.dll"] {
        let h = unsafe { LoadLibraryW(wstr(dll).as_ptr()) };
        if h != 0 {
            let p = unsafe { GetProcAddress(h, b"XInputGetState\0".as_ptr()) };
            if p != 0 { return Some(unsafe { std::mem::transmute::<usize, XiGetState>(p) }) }
        }
    }
    None
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



// ---- the world: the canon "mountains" parameter set over unbounded coordinates ----------------
const W_SEED: i64 = 1958;
const W_HS: i64 = 420;
const W_LAYERS: [(i64, i64); 4] = [(48, 5), (12, 3), (6, 2), (3, 1)];
const W_RAWMAX: i64 = 11 * VMAX;       // sum(amp) * VMAX for the layer set above
const H_SCALE: i64 = 16;               // DECLARED view scale: canon 0..420 -> world 0..26
const TILE: i64 = 3;
const VIEW: i64 = 20;
const NEAR8: i64 = 2 * 256;            // near clip in Q8 camera units — v1's 12-unit clip threw
                                       // away the four nearest rings of ground wholesale
const FAR8: i64 = VIEW * TILE * 256;   // patch edge in Q8 — the depth-fog ruler

fn raw_height(x: i64, y: i64) -> i64 {
    let mut raw = 0i64;
    for (li, &(cell, amp)) in W_LAYERS.iter().enumerate() {
        raw += amp * noise16(W_SEED, li as i64, cell, x, y);
    }
    floordiv(raw * W_HS, W_RAWMAX)
}

struct World { cache: std::collections::HashMap<(i64, i64), i64> }
impl World {
    fn new() -> World { World { cache: std::collections::HashMap::new() } }
    fn h(&mut self, x: i64, y: i64) -> i64 {
        if let Some(&v) = self.cache.get(&(x, y)) { return v }
        let v = floordiv(raw_height(x, y), H_SCALE);
        self.cache.insert((x, y), v);
        v
    }
}

// ---- fnv64: a DIVERGENCE DETECTOR, honestly named — not cryptographic ------------------------
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

// ---- the certified camera ---------------------------------------------------------------------
const SENS: i64 = ONE / 1024;          // DECLARED input scale: mouse count -> half-angle
const PITCH_MAX: i64 = (ONE / 8) * 7;  // clamp on accumulated pitch half-angle sum

struct Cam { q: Q4, pitch_acc: i64, px: i64, py: i64 }   // px, py in Q8 world units

fn qconj(q: Q4) -> Q4 { Q4 { w: q.w, x: -q.x, y: -q.y, z: -q.z } }

fn step_cam(fx: &mut Fx, cam: &mut Cam, keys: u32, dx: i64, dy: i64) {
    // yaw: world-frame Z increment; pitch: local-frame X increment, clamped by accumulation.
    let yaw_half = -dx * SENS / 8;
    let want = (cam.pitch_acc - dy * SENS / 8).clamp(-PITCH_MAX, PITCH_MAX);
    let pitch_half = want - cam.pitch_acc;
    cam.pitch_acc = want;
    let dq_yaw = fx.qnormalize(Q4 { w: ONE, x: 0, y: 0, z: yaw_half });
    let dq_pitch = fx.qnormalize(Q4 { w: ONE, x: pitch_half, y: 0, z: 0 });
    let q1 = fx.qmul(cam.q, dq_pitch);
    let q2 = fx.qmul(dq_yaw, q1);
    cam.q = fx.qnormalize(q2);

    // WASD on the rotated ground plane: forward = q * (+Y), right = q * (+X), z discarded.
    let fwd = fx.vrotate(cam.q, V3 { x: 0, y: ONE, z: 0 });
    let rgt = fx.vrotate(cam.q, V3 { x: ONE, y: 0, z: 0 });
    let sp = 40i64;                                        // Q8 world units per frame
    let (mut mx, mut my) = (0i64, 0i64);
    if keys & 1 != 0 { mx += (fwd.x >> 24) * sp / 256; my += (fwd.y >> 24) * sp / 256 }
    if keys & 4 != 0 { mx -= (fwd.x >> 24) * sp / 256; my -= (fwd.y >> 24) * sp / 256 }
    if keys & 2 != 0 { mx -= (rgt.x >> 24) * sp / 256; my -= (rgt.y >> 24) * sp / 256 }
    if keys & 8 != 0 { mx += (rgt.x >> 24) * sp / 256; my += (rgt.y >> 24) * sp / 256 }
    cam.px += mx;
    cam.py += my;
}

// ---- the renderer: certified rotation, windowed canon terrain ---------------------------------
fn raster_world(fx: &mut Fx, buf: &mut [u32], zbuf: &mut [i32], w: i32, h: i32,
                cam: &Cam, world: &mut World) {
    // sky: fixed gradient (the horizon is wherever the rotation puts the terrain now)
    for y in 0..h {
        let t = (y * 200 / h.max(1)) as u32;
        let c = (30 << 16) | ((70 + t / 3) << 8) | (130 + t / 2).min(255);
        let row = (y * w) as usize;
        for x in 0..w as usize { buf[row + x] = c }
    }
    for z in zbuf.iter_mut().take((w * h) as usize) { *z = i32::MAX }

    let f = h as i64 * 2;
    let (cx, cy) = (w as i64 / 2, h as i64 / 2);
    let cam_tile_x = floordiv(cam.px >> 8, TILE);
    let cam_tile_y = floordiv(cam.py >> 8, TILE);
    // THE EYE STANDS ON BILINEAR GROUND, IN Q8. v1 computed every world delta at INTEGER
    // world resolution (cam.px >> 8), so a walking camera rendered from the same snapped
    // position for ~7 frames and then jumped a whole unit — and eye height stepped discretely
    // at tile boundaries. Both were invisible to every run so far because no recorded walk has
    // ever moved (the v1 trace's keys never arrived; see the focus note at window creation).
    // The synthetic-walk harness saw it before any operator had to. VIEW-layer, never canon.
    let (rx8, ry8) = (cam.px - ((cam_tile_x * TILE) << 8), cam.py - ((cam_tile_y * TILE) << 8));
    let (u, v) = (rx8 / TILE, ry8 / TILE);                       // 0..255 within the tile
    let (h00, h10) = (world.h(cam_tile_x, cam_tile_y) << 8, world.h(cam_tile_x + 1, cam_tile_y) << 8);
    let (h01, h11) = (world.h(cam_tile_x, cam_tile_y + 1) << 8, world.h(cam_tile_x + 1, cam_tile_y + 1) << 8);
    let hx0 = h00 + (h10 - h00) * u / 256;
    let hx1 = h01 + (h11 - h01) * u / 256;
    let eye8 = hx0 + (hx1 - hx0) * v / 256 + (3 << 8);
    let qc = qconj(cam.q);

    let side = (2 * VIEW + 1) as usize;
    let mut screen: Vec<(i64, i64, i64)> = Vec::with_capacity(side * side);
    for gy in -VIEW..=VIEW {
        for gx in -VIEW..=VIEW {
            let (wx, wy) = (cam_tile_x + gx, cam_tile_y + gy);
            let dxw8 = ((wx * TILE) << 8) - cam.px;
            let dyw8 = ((wy * TILE) << 8) - cam.py;
            let dzw8 = (world.h(wx, wy) << 8) - eye8;
            // Q8 world delta -> Q32.32 -> certified rotation -> Q8 camera space
            let r = fx.vrotate(qc, V3 { x: dxw8 << 24, y: dyw8 << 24, z: dzw8 << 24 });
            let d8 = r.y >> 24;
            if d8 < NEAR8 { screen.push((i64::MIN, 0, 0)); continue }
            screen.push((cx + (r.x >> 24) * f / d8, cy - (r.z >> 24) * f / d8, d8));
        }
    }
    let idx = |gx: i64, gy: i64| ((gy + VIEW) * (2 * VIEW + 1) + gx + VIEW) as usize;
    for gy in -VIEW..VIEW {
        for gx in -VIEW..VIEW {
            let (wx, wy) = (cam_tile_x + gx, cam_tile_y + gy);
            let (h00, h10) = (world.h(wx, wy), world.h(wx + 1, wy));
            let (h01, h11) = (world.h(wx, wy + 1), world.h(wx + 1, wy + 1));
            let h4 = h00 + h10 + h01 + h11;
            // v1.6 — P3.4 CANDIDATE 1, GRADUATED: height bands + integer lambert sun.
            // Anchors from the MEASURED height histogram (480x480 canon tiles: median 12,
            // 96% below 19), piecewise-linear so band edges cannot ring; per-triangle
            // world-space normal, fixed integer sun, one small isqrt. All VIEW-layer:
            // the canon heights and the certified camera are untouched. Cost on the
            // committed walk workload measured statistically ZERO on the authoring
            // container (4.97s -> 4.91s / 1145 frames); the host A/B decides for real.
            fn isqrt(n: i64) -> i64 {
                if n <= 0 { return 0 }
                let mut x = n; let mut y = (x + 1) / 2;
                while y < x { x = y; y = (x + n / x) / 2 }
                x
            }
            let havg = h4 / 4;
            let jit = ((wx.wrapping_mul(73) ^ wy.wrapping_mul(151)) & 7) - 3;
            // anchors from the MEASURED height distribution (median 12, 96% below 19):
            // sand@4, grass@10, rock@16, snow@21 — piecewise-linear, so no band rings
            let band = |h: i64| -> (i64, i64, i64) {
                let lerp = |a: (i64, i64, i64), b: (i64, i64, i64), t_num: i64, t_den: i64| {
                    (a.0 + (b.0 - a.0) * t_num / t_den,
                     a.1 + (b.1 - a.1) * t_num / t_den,
                     a.2 + (b.2 - a.2) * t_num / t_den)
                };
                let sand = (150 + jit, 137 + jit, 94);
                let grass = (56 + jit * 2, 118 + jit * 2, 48 + jit);
                let rock = (99 + jit, 86 + jit, 72 + jit);
                let snow = (224, 227, 234);
                if h <= 4 { sand }
                else if h <= 10 { lerp(sand, grass, h - 4, 6) }
                else if h <= 16 { lerp(grass, rock, h - 10, 6) }
                else if h <= 21 { lerp(rock, snow, h - 16, 5) }
                else { snow }
            };
            let lam = |ax: i64, ay: i64, az: i64, bx: i64, by: i64, bz: i64| -> i64 {
                // normal = cross(edge1, edge2), sun L = (-2, -1, 3), lambert in 0..256
                let (nx, ny, nz) = (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx);
                let (nx, ny, nz) = if nz < 0 { (-nx, -ny, -nz) } else { (nx, ny, nz) };
                let dot = -2 * nx - ny + 3 * nz;
                if dot <= 0 { return 0 }
                let nn = isqrt(nx * nx + ny * ny + nz * nz);
                let ll = 4; // isqrt(4+1+9)=3.74 -> 4 (ceil keeps lam <= 256)
                if nn == 0 { return 0 }
                (dot * 256 / (nn * ll)).min(256)
            };
            // triangle 1 world edges: (TILE,0,h10-h00), (0,TILE,h01-h00); triangle 2 from h11
            let l1 = lam(TILE, 0, h10 - h00, 0, TILE, h01 - h00);
            let l2 = lam(0, TILE, h11 - h10, -TILE, 0, h01 - h11);
            let (br, bg, bb) = band(havg);
            let lit = |l: i64, c: i64| (c * (60 + 196 * l / 256) / 160).clamp(0, 255);
            let quad = [(idx(gx, gy), idx(gx + 1, gy), idx(gx, gy + 1),
                         (lit(l1, br), lit(l1, bg), lit(l1, bb))),
                        (idx(gx + 1, gy), idx(gx + 1, gy + 1), idx(gx, gy + 1),
                         (lit(l2, br), lit(l2, bg), lit(l2, bb)))];
            for &(ia, ib, ic, (tr, tg, tb)) in &quad {
                let (a, mut b, mut cc) = (screen[ia], screen[ib], screen[ic]);
                if a.0 == i64::MIN || b.0 == i64::MIN || cc.0 == i64::MIN { continue }
                // whole-triangle screen rejection: a near tile projects to a bbox far larger
                // than the screen; when every vertex is off one edge nothing can be covered
                if (a.0 < 0 && b.0 < 0 && cc.0 < 0) || (a.1 < 0 && b.1 < 0 && cc.1 < 0)
                    || (a.0 >= w as i64 && b.0 >= w as i64 && cc.0 >= w as i64)
                    || (a.1 >= h as i64 && b.1 >= h as i64 && cc.1 >= h as i64) { continue }
                let mut area = (b.0 - a.0) * (cc.1 - a.1) - (b.1 - a.1) * (cc.0 - a.0);
                if area == 0 { continue }
                // v1 kept only area > 0 — and ground below eye level winds NEGATIVE in
                // screen space (y grows downward), so the demo backface-culled the entire
                // floor of its own world; the "ribbon" the operator photographed was the
                // set of far faces steep enough to wind the other way. A heightfield the
                // camera walks ON is rendered two-sided.
                if area < 0 { std::mem::swap(&mut b, &mut cc); area = -area; }
                // depth fog toward the sky band: per-channel integer blend, deterministic
                let d3 = ((a.2 + b.2 + cc.2) / 3).clamp(0, FAR8);
                let dim = 14 + 18 * (FAR8 - d3) / FAR8;            // 14..32 of 32 (softer fog)
                let ch3 = |near: i64, sky: i64| ((near * dim + sky * (32 - dim)) / 32) as u32;
                let col = (ch3(tr, 60) << 16) | (ch3(tg, 120) << 8) | ch3(tb, 190);
                let x_lo = a.0.min(b.0).min(cc.0).max(0);
                let x_hi = a.0.max(b.0).max(cc.0).min(w as i64 - 1);
                let y_lo = a.1.min(b.1).min(cc.1).max(0);
                let y_hi = a.1.max(b.1).max(cc.1).min(h as i64 - 1);
                if x_lo > x_hi || y_lo > y_hi { continue }
                // incremental edge functions: the closed-form cross products are affine in
                // (px, py), so each is seeded once per row and STEPPED by integer adds — the
                // same exact values the per-pixel multiplies produced, cheaper by the width
                let (dw0x, dw0y) = (-(b.1 - a.1), b.0 - a.0);
                let (dw1x, dw1y) = (-(cc.1 - b.1), cc.0 - b.0);
                let (dw2x, dw2y) = (-(a.1 - cc.1), a.0 - cc.0);
                let mut w0r = (b.0 - a.0) * (y_lo - a.1) - (b.1 - a.1) * (x_lo - a.0);
                let mut w1r = (cc.0 - b.0) * (y_lo - b.1) - (cc.1 - b.1) * (x_lo - b.0);
                let mut w2r = (a.0 - cc.0) * (y_lo - cc.1) - (a.1 - cc.1) * (x_lo - cc.0);
                // the depth divide leaves the pixel loop too: floor(zn/area) is maintained as
                // an exact quotient/remainder pair stepped by adds — the container profile put
                // ~80% of frame cost in this one i64 division, and depth is nonnegative inside
                // coverage, so floor and the old truncation are the SAME integer (bit-identical
                // digests, checked against the pre-optimization chain in the authoring harness)
                let dznx = dw1x * a.2 + dw2x * b.2 + dw0x * cc.2;
                let (dq, dr) = (dznx.div_euclid(area), dznx.rem_euclid(area));
                for py in y_lo..=y_hi {
                    let row = (py * w as i64) as usize;
                    let (mut w0, mut w1, mut w2) = (w0r, w1r, w2r);
                    let zn = w1 * a.2 + w2 * b.2 + w0 * cc.2;
                    let (mut q, mut r) = (zn.div_euclid(area), zn.rem_euclid(area));
                    let mut entered = false;
                    for px in x_lo..=x_hi {
                        if w0 >= 0 && w1 >= 0 && w2 >= 0 {
                            entered = true;
                            let d = q as i32;
                            let i = row + px as usize;
                            if d < zbuf[i] { zbuf[i] = d; buf[i] = col }
                        } else if entered {
                            break; // a convex row span is contiguous: once left, never re-entered
                        }
                        w0 += dw0x; w1 += dw1x; w2 += dw2x;
                        q += dq; r += dr;
                        if r >= area { q += 1; r -= area }
                    }
                    w0r += dw0y; w1r += dw1y; w2r += dw2y;
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

// ---- the conformance door: the demo's math held to the placements' goldens -------------------
const CANON_PINS: [(&str, &str); 3] = [
    ("island", "7243652eb97adf557f336d7417ed19a769ea60764e1354f68f29e8b7b55cb222"),
    ("blank", "7cc67f6769959ff09356f20b6a0999d7c3c397b30e4fb4addbfc04c342faa83e"),
    ("mountains", "c57c56bee9650148b139b927aa1d036baca1f07d0a683982c01c4b17e1aa069e"),
];

fn selfcheck() -> bool {
    let mut ok = true;
    let mut fx = Fx::new();
    let d = battery(&mut fx, false);
    let batt_ok = d == GOLDEN && !fx.refused;
    println!("selfcheck fpquat battery : {}", if batt_ok { "MATCHES GOLDEN" }
             else { "MISMATCH — the camera math is NOT the certified math" });
    ok &= batt_ok;
    for s in scenes() {
        let falloff = if s.island { "island" } else { "none" };
        let heights = generate(s.w, s.h, s.seed, s.hs, &s.layers, s.island, s.fw);
        let dig = field_digest(s.w, s.h, s.hs, s.sl, falloff, &heights);
        let pin = CANON_PINS.iter().find(|&&(n, _)| n == s.name).map(|&(_, p)| p).unwrap_or("");
        let hit = dig == pin;
        println!("selfcheck canon {:9}: {}", s.name,
                 if hit { "MATCHES PIN" } else { "MISMATCH — the terrain is NOT the canon" });
        ok &= hit;
    }
    ok
}


const ONE: i64 = 1i64 << 32;
const IMAX: i128 = (1i128 << 63) - 1;
const COMP_MAX: i64 = 1i64 << 61;
const GOLDEN: &str = "3f4aa0d172713a4bf26433c19e211fbd52e474bbae603ce0c665d145412b7e7a";



// ---- the frozen laws (refusal is a sticky flag on the context) ------------------------
struct Fx {
    refused: bool,
}

#[derive(Clone, Copy)]
struct Q4 { w: i64, x: i64, y: i64, z: i64 }
#[derive(Clone, Copy)]
struct V3 { x: i64, y: i64, z: i64 }

impl Fx {
    fn new() -> Fx { Fx { refused: false } }

    fn rdiv(&mut self, p: i128, d: i128) -> i64 {
        // round to nearest, ties away from zero (d > 0) — the FROZEN rule
        let r = if p >= 0 { (2 * p + d) / (2 * d) } else { -((2 * (-p) + d) / (2 * d)) };
        if r > IMAX || r < -IMAX { self.refused = true; return 0; }
        r as i64
    }
    fn fin(&mut self, v: i64) -> i64 {
        if v > COMP_MAX || v < -COMP_MAX { self.refused = true; }
        v
    }
    fn qnorm2(&mut self, q: Q4) -> i64 {
        self.fin(q.w); self.fin(q.x); self.fin(q.y); self.fin(q.z);
        let s = (q.w as i128) * (q.w as i128) + (q.x as i128) * (q.x as i128)
              + (q.y as i128) * (q.y as i128) + (q.z as i128) * (q.z as i128);
        self.rdiv(s, ONE as i128)
    }
    fn qdot(&mut self, p: Q4, q: Q4) -> i64 {
        let s = (p.w as i128) * (q.w as i128) + (p.x as i128) * (q.x as i128)
              + (p.y as i128) * (q.y as i128) + (p.z as i128) * (q.z as i128);
        self.rdiv(s, ONE as i128)
    }
    fn qmul(&mut self, p: Q4, q: Q4) -> Q4 {
        let (pw, px, py, pz) = (p.w as i128, p.x as i128, p.y as i128, p.z as i128);
        let (qw, qx, qy, qz) = (q.w as i128, q.x as i128, q.y as i128, q.z as i128);
        Q4 {
            w: self.rdiv(pw * qw - px * qx - py * qy - pz * qz, ONE as i128),
            x: self.rdiv(pw * qx + px * qw + py * qz - pz * qy, ONE as i128),
            y: self.rdiv(pw * qy - px * qz + py * qw + pz * qx, ONE as i128),
            z: self.rdiv(pw * qz + px * qy - py * qx + pz * qw, ONE as i128),
        }
    }
    fn rsqrt(&mut self, x: i64) -> i64 {
        if x <= 0 { self.refused = true; return 0; }
        let n: u128 = (1u128 << 96) / (x as u128);
        let r = isqrt_newton(n);
        if (r as i128) > IMAX { self.refused = true; return 0; }
        r as i64
    }
    fn qnormalize(&mut self, q: Q4) -> Q4 {
        let n2 = self.qnorm2(q);
        if n2 <= 0 { self.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        let r = self.rsqrt(n2) as i128;
        Q4 {
            w: self.rdiv(q.w as i128 * r, ONE as i128),
            x: self.rdiv(q.x as i128 * r, ONE as i128),
            y: self.rdiv(q.y as i128 * r, ONE as i128),
            z: self.rdiv(q.z as i128 * r, ONE as i128),
        }
    }
    fn vrotate(&mut self, q: Q4, v: V3) -> V3 {
        let tx = 2 * self.rdiv(q.y as i128 * v.z as i128 - q.z as i128 * v.y as i128, ONE as i128);
        let ty = 2 * self.rdiv(q.z as i128 * v.x as i128 - q.x as i128 * v.z as i128, ONE as i128);
        let tz = 2 * self.rdiv(q.x as i128 * v.y as i128 - q.y as i128 * v.x as i128, ONE as i128);
        V3 {
            x: v.x + self.rdiv(q.w as i128 * tx as i128, ONE as i128)
                 + self.rdiv(q.y as i128 * tz as i128 - q.z as i128 * ty as i128, ONE as i128),
            y: v.y + self.rdiv(q.w as i128 * ty as i128, ONE as i128)
                 + self.rdiv(q.z as i128 * tx as i128 - q.x as i128 * tz as i128, ONE as i128),
            z: v.z + self.rdiv(q.w as i128 * tz as i128, ONE as i128)
                 + self.rdiv(q.x as i128 * ty as i128 - q.y as i128 * tx as i128, ONE as i128),
        }
    }
    fn qnlerp(&mut self, p: Q4, q0: Q4, t: i64) -> Q4 {
        if t < 0 || t > ONE { self.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        let mut q = q0;
        if self.qdot(p, q) < 0 { q = Q4 { w: -q.w, x: -q.x, y: -q.y, z: -q.z }; }
        let li = (ONE - t) as i128;
        let ti = t as i128;
        let b = Q4 {
            w: self.rdiv(p.w as i128 * li + q.w as i128 * ti, ONE as i128),
            x: self.rdiv(p.x as i128 * li + q.x as i128 * ti, ONE as i128),
            y: self.rdiv(p.y as i128 * li + q.y as i128 * ti, ONE as i128),
            z: self.rdiv(p.z as i128 * li + q.z as i128 * ti, ONE as i128),
        };
        self.qnormalize(b)
    }
    // wrap64 defect variants (norm2 + qmul only, mirroring reference + C defects)
    fn qnorm2_w(&mut self, q: Q4) -> i64 {
        let s = w64(w64(w64((q.w as i128) * (q.w as i128)) as i128 + w64((q.x as i128) * (q.x as i128)) as i128) as i128
                  + w64(w64((q.y as i128) * (q.y as i128)) as i128 + w64((q.z as i128) * (q.z as i128)) as i128) as i128);
        self.rdiv(s as i128, ONE as i128)
    }
    fn qmul_w(&mut self, p: Q4, q: Q4) -> Q4 {
        let m = |a: i64, b: i64| -> i64 { w64((a as i128) * (b as i128)) };
        let w_ = w64(w64(w64(m(p.w, q.w) as i128 - m(p.x, q.x) as i128) as i128
                       - w64(m(p.y, q.y) as i128 + m(p.z, q.z) as i128) as i128) as i128);
        let x_ = w64(w64(w64(m(p.w, q.x) as i128 + m(p.x, q.w) as i128) as i128
                       + w64(m(p.y, q.z) as i128 - m(p.z, q.y) as i128) as i128) as i128);
        let y_ = w64(w64(w64(m(p.w, q.y) as i128 - m(p.x, q.z) as i128) as i128
                       + w64(m(p.y, q.w) as i128 + m(p.z, q.x) as i128) as i128) as i128);
        let z_ = w64(w64(w64(m(p.w, q.z) as i128 + m(p.x, q.y) as i128) as i128
                       - w64(m(p.y, q.x) as i128 - m(p.z, q.w) as i128) as i128) as i128);
        Q4 {
            w: self.rdiv(w_ as i128, ONE as i128),
            x: self.rdiv(x_ as i128, ONE as i128),
            y: self.rdiv(y_ as i128, ONE as i128),
            z: self.rdiv(z_ as i128, ONE as i128),
        }
    }
}

fn w64(v: i128) -> i64 {
    // two's-complement i64 wrap — DEFECT ONLY (the real laws refuse, never wrap)
    (v as u64) as i64
}

fn isqrt_newton(n: u128) -> u128 {
    if n < 2 { return n; }
    let bl = 128 - n.leading_zeros() as i32;
    let mut r: u128 = 1u128 << ((bl + 1) / 2);
    loop {
        let nr = (r + n / r) >> 1;
        if nr >= r { break; }
        r = nr;
    }
    // belt-and-braces adjustment (provably unreachable for this stop rule; kept
    // so a mis-ported Newton variant still lands exactly on floor(sqrt(n)))
    while r * r > n { r -= 1; }
    while (r + 1) * (r + 1) <= n { r += 1; }
    r
}



// ---- battery (mirrors fpquat.py constants and row order exactly) ----------------------
fn battery(fx: &mut Fx, defect: bool) -> String {
    let h2 = ONE / 2;
    let q3 = 3 * ONE / 4;
    let t3 = ONE / 3;
    let quats = [
        Q4 { w: ONE, x: 0, y: 0, z: 0 },
        Q4 { w: ONE, x: h2, y: 0, z: 0 },
        Q4 { w: ONE, x: h2, y: q3, z: -t3 },
        Q4 { w: 3 * ONE, x: -2 * ONE, y: ONE, z: h2 },
    ];
    let vecs = [
        V3 { x: ONE, y: 0, z: 0 },
        V3 { x: 0, y: ONE, z: 0 },
        V3 { x: h2, y: q3, z: -ONE },
        V3 { x: 5 * ONE, y: -3 * ONE, z: 2 * ONE + 12345 },
    ];
    let rsq: [i64; 10] = [1, 2, ONE / 4, h2, ONE, 2 * ONE, 3 * ONE, 10 * ONE,
                          (1i64 << 48) + 7919, COMP_MAX];
    let nt: [i64; 4] = [0, ONE / 4, h2, ONE];

    let mut buf: Vec<u8> = Vec::with_capacity(8192);
    buf.extend_from_slice(b"URDRFPQ1");
    let put = |buf: &mut Vec<u8>, v: i64| buf.extend_from_slice(&v.to_be_bytes());

    for &x in rsq.iter() {
        buf.extend_from_slice(b"rsqrt");
        let r = fx.rsqrt(x);
        put(&mut buf, r);
    }
    for &q in quats.iter() {
        buf.extend_from_slice(b"norm2");
        let n = if defect { w64(fx.qnorm2_w(q) as i128) } else { fx.qnorm2(q) };
        put(&mut buf, n);
    }
    for &p in quats.iter() {
        for &q in quats.iter() {
            buf.extend_from_slice(b"qmul");
            let r = if defect { fx.qmul_w(p, q) } else { fx.qmul(p, q) };
            if defect {
                put(&mut buf, w64(r.w as i128)); put(&mut buf, w64(r.x as i128));
                put(&mut buf, w64(r.y as i128)); put(&mut buf, w64(r.z as i128));
            } else {
                put(&mut buf, r.w); put(&mut buf, r.x); put(&mut buf, r.y); put(&mut buf, r.z);
            }
        }
    }
    let mut units = [Q4 { w: 0, x: 0, y: 0, z: 0 }; 4];
    for i in 0..4 {
        units[i] = fx.qnormalize(quats[i]);
        buf.extend_from_slice(b"normalize");
        put(&mut buf, units[i].w); put(&mut buf, units[i].x);
        put(&mut buf, units[i].y); put(&mut buf, units[i].z);
    }
    for &u in units.iter() {
        for &v in vecs.iter() {
            buf.extend_from_slice(b"rotate");
            let r = fx.vrotate(u, v);
            put(&mut buf, r.x); put(&mut buf, r.y); put(&mut buf, r.z);
        }
    }
    for i in 0..4 {
        for &t in nt.iter() {
            buf.extend_from_slice(b"nlerp");
            let r = fx.qnlerp(quats[i], quats[(i + 1) % 4], t);
            put(&mut buf, r.w); put(&mut buf, r.x); put(&mut buf, r.y); put(&mut buf, r.z);
        }
    }
    sha256_hex(&buf)
}




const FRAC: i64 = 1 << 16;             // Q16 interpolation substrate (== Python FRAC)
const VMAX: i64 = 0xFFFF;              // lattice value range [0, VMAX]

// Floored integer division for d > 0 — matches Python `//`. Rust `/` truncates toward zero, so a
// negative numerator with a remainder is one too high; correct it down.
fn floordiv(n: i64, d: i64) -> i64 {
    if n % d != 0 && n < 0 { n / d - 1 } else { n / d }
}

// The seeded lattice value in [0, VMAX] — sha256("URDRHF1|seed|layer|xi|yi")[:4] big-endian & VMAX.
fn lattice(seed: i64, layer: i64, xi: i64, yi: i64) -> i64 {
    let s = format!("URDRHF1|{}|{}|{}|{}", seed, layer, xi, yi);
    let d = sha256(s.as_bytes());
    (u32::from_be_bytes([d[0], d[1], d[2], d[3]]) as i64) & VMAX
}

// The quintic fade 6t^5 - 15t^4 + 10t^3 in Q16, floor-rounded at each power (Python `_fade`).
fn fade(t: i64) -> i64 {
    let t2 = floordiv(t * t, FRAC);
    let t3 = floordiv(t2 * t, FRAC);
    let t4 = floordiv(t3 * t, FRAC);
    let t5 = floordiv(t4 * t, FRAC);
    6 * t5 - 15 * t4 + 10 * t3
}

// Seeded value noise at (x, y) for a lattice of `cell` size — bilinear under `fade`, Q16 floor math.
fn noise16(seed: i64, layer: i64, cell: i64, x: i64, y: i64) -> i64 {
    // FLOORED divmod: identical to `/`+`%` for x >= 0 (the canon domain — the selfcheck
    // digests prove it bit-for-bit), and correct for the demo's unbounded coordinates.
    let xi = floordiv(x, cell); let fx = x - xi * cell;
    let yi = floordiv(y, cell); let fy = y - yi * cell;
    let u = fade(floordiv(fx * FRAC, cell));
    let v = fade(floordiv(fy * FRAC, cell));
    let v00 = lattice(seed, layer, xi, yi);
    let v10 = lattice(seed, layer, xi + 1, yi);
    let v01 = lattice(seed, layer, xi, yi + 1);
    let v11 = lattice(seed, layer, xi + 1, yi + 1);
    let a = v00 + floordiv((v10 - v00) * u, FRAC); // v10 - v00 may be NEGATIVE — floordiv is load-bearing
    let b = v01 + floordiv((v11 - v01) * u, FRAC);
    a + floordiv((b - a) * v, FRAC)
}

// Sqrt-free radial island falloff in Q16: full inside r_in^2, zero outside r_out^2, linear in d^2.
fn island_mask(x: i64, y: i64, w: i64, h: i64, fw: i64) -> i64 {
    let cx2 = 2 * x - (w - 1);
    let cy2 = 2 * y - (h - 1);
    let d2 = cx2 * cx2 + cy2 * cy2;
    let r_out2 = (w - 1) * (w - 1) + (h - 1) * (h - 1);
    let r_in2 = floordiv(r_out2 * (256 - fw) * (256 - fw), 256 * 256);
    if d2 >= r_out2 { return 0; }
    if d2 <= r_in2 { return FRAC; }
    floordiv((r_out2 - d2) * FRAC, r_out2 - r_in2)
}

// The heightfield: row-major ints in [0, hs]. Same inputs, same bytes — the whole point.
fn generate(w: i64, h: i64, seed: i64, hs: i64, layers: &[(i64, i64)], island: bool, fw: i64) -> Vec<Vec<i64>> {
    let rawmax: i64 = layers.iter().map(|&(_c, a)| a * VMAX).sum();
    let mut rows = Vec::with_capacity(h as usize);
    for y in 0..h {
        let mut row = Vec::with_capacity(w as usize);
        for x in 0..w {
            let mut raw = 0i64;
            for (li, &(cell, amp)) in layers.iter().enumerate() {
                raw += amp * noise16(seed, li as i64, cell, x, y);
            }
            let mut hv = floordiv(raw * hs, rawmax);
            if island {
                hv = floordiv(hv * island_mask(x, y, w, h, fw), FRAC);
            }
            row.push(hv);
        }
        rows.push(row);
    }
    rows
}

// The URDRHF1 canon — SHA-256 over the declared header and the row-major heights (Python `field_digest`).
fn field_digest(w: i64, h: i64, hs: i64, sl: i64, falloff: &str, heights: &[Vec<i64>]) -> String {
    let mut m = Sha256::new();
    m.update(b"URDRHF1");
    m.update(format!("|{},{}|hs:{}|sl:{}|f:{}", w, h, hs, sl, falloff).as_bytes());
    for row in heights {
        m.update(b"|");
        let joined: Vec<String> = row.iter().map(|v| v.to_string()).collect();
        m.update(joined.join(",").as_bytes());
    }
    hex(&m.finish())
}

struct Scene { name: &'static str, w: i64, h: i64, seed: i64, hs: i64, sl: i64, layers: Vec<(i64, i64)>, island: bool, fw: i64 }

fn scenes() -> Vec<Scene> {
    vec![
        Scene { name: "island",    w: 64, h: 64, seed: 2920741843, hs: 420, sl: 72, layers: vec![(32, 4), (16, 2), (8, 1)],           island: true,  fw: 90 },
        Scene { name: "blank",     w: 16, h: 16, seed: 7,          hs: 100, sl: 30, layers: vec![(8, 1)],                             island: false, fw: 0 },
        Scene { name: "mountains", w: 64, h: 64, seed: 1958,       hs: 420, sl: 40, layers: vec![(48, 5), (12, 3), (6, 2), (3, 1)],   island: false, fw: 0 },
    ]
}



// ---- hand-rolled SHA-256 (verbatim from winding_rs / worldstep_rs) --------------------
const K: [u32; 64] = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2,
];
struct Sha256 { h: [u32; 8], buf: [u8; 64], n: usize, len: u64 }
impl Sha256 {
    fn new() -> Self { Sha256 { h: [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19], buf: [0; 64], n: 0, len: 0 } }
    fn update(&mut self, data: &[u8]) { for &b in data { self.buf[self.n] = b; self.n += 1; self.len = self.len.wrapping_add(1); if self.n == 64 { self.process(); self.n = 0; } } }
    fn process(&mut self) {
        let mut w = [0u32; 64];
        for i in 0..16 { w[i] = u32::from_be_bytes([self.buf[i*4], self.buf[i*4+1], self.buf[i*4+2], self.buf[i*4+3]]); }
        for i in 16..64 { let s0 = w[i-15].rotate_right(7) ^ w[i-15].rotate_right(18) ^ (w[i-15] >> 3); let s1 = w[i-2].rotate_right(17) ^ w[i-2].rotate_right(19) ^ (w[i-2] >> 10); w[i] = w[i-16].wrapping_add(s0).wrapping_add(w[i-7]).wrapping_add(s1); }
        let (mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut hh) = (self.h[0],self.h[1],self.h[2],self.h[3],self.h[4],self.h[5],self.h[6],self.h[7]);
        for i in 0..64 {
            let s1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let ch = (e & f) ^ ((!e) & g);
            let t1 = hh.wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let maj = (a & b) ^ (a & c) ^ (b & c);
            let t2 = s0.wrapping_add(maj);
            hh = g; g = f; f = e; e = d.wrapping_add(t1); d = c; c = b; b = a; a = t1.wrapping_add(t2);
        }
        self.h[0]=self.h[0].wrapping_add(a); self.h[1]=self.h[1].wrapping_add(b); self.h[2]=self.h[2].wrapping_add(c); self.h[3]=self.h[3].wrapping_add(d);
        self.h[4]=self.h[4].wrapping_add(e); self.h[5]=self.h[5].wrapping_add(f); self.h[6]=self.h[6].wrapping_add(g); self.h[7]=self.h[7].wrapping_add(hh);
    }
    fn finish(mut self) -> [u8; 32] {
        let bitlen = self.len.wrapping_mul(8);
        self.update(&[0x80]); while self.n != 56 { self.update(&[0x00]); }
        let lb = bitlen.to_be_bytes(); self.update(&lb);
        let mut out = [0u8; 32];
        for i in 0..8 { out[i*4..i*4+4].copy_from_slice(&self.h[i].to_be_bytes()); }
        out
    }
}
fn sha256(data: &[u8]) -> [u8; 32] { let mut m = Sha256::new(); m.update(data); m.finish() }
fn hex(b: &[u8]) -> String { let mut s = String::new(); for x in b { s.push_str(&format!("{:02x}", x)); } s }

fn sha256_hex(data: &[u8]) -> String { hex(&sha256(data)) }
// ---- the entry door ---------------------------------------------------------------------------
struct Args {
    host: String, power: String, scheduler: String, hz: i64, frames: u32,
    res: (i32, i32), play: bool, replay: String, defect: bool, selfcheck_only: bool,
    trace_out: String, out: String,
}

fn parse_argv() -> Result<Args, String> {
    let mut a = Args { host: "-".into(), power: "-".into(), scheduler: "-".into(), hz: 120,
                       frames: 1800, res: (1280, 720), play: false, replay: String::new(),
                       defect: false, selfcheck_only: false,
                       trace_out: "fpsdemo_trace.txt".into(),
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
            "--selfcheck" => a.selfcheck_only = true,
            "--trace-out" => a.trace_out = value(&mut i)?,
            "--out" => a.out = value(&mut i)?,
            other => return Err(format!("unknown flag {other} — this door refuses")),
        }
        i += 1;
    }
    if a.selfcheck_only {
        if a.play || !a.replay.is_empty() {
            return Err("--selfcheck runs alone".into());
        }
    } else if a.play == !a.replay.is_empty() {
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
    // THE DOOR: the demo's math is the certified math, checked at every start — a launch that
    // fails its selfcheck REFUSES to run, whatever mode was asked for.
    let door = selfcheck();
    if !door {
        eprintln!("FPSDEMO-REFUSE: selfcheck failed — not running with uncertified math");
        std::process::exit(1);
    }
    if args.selfcheck_only {
        println!("selfcheck: ALL MATCH — the camera is URDRFPQ1's battery and the terrain is \
                  URDRHF1's canon, bit for bit");
        return;
    }
    let trace_in = if args.replay.is_empty() { Vec::new() }
                   else { match load_trace(&args.replay) {
                       Ok(t) => t,
                       Err(e) => { eprintln!("FPSDEMO-REFUSE: {e}"); std::process::exit(2) } } };
    // A RECORD IS NOT A SCRATCH PATH (attest's law, at this door): v1's default --trace-out was
    // the exact filename of the operator's existing v0 recording, so one bare `--play` would
    // have replaced the tree's only recorded workload with a different measurement wearing the
    // same name. The only reason it survived is that a wrongly-typed invocation was refused.
    if args.play && std::path::Path::new(&args.trace_out).exists() {
        eprintln!("FPSDEMO-REFUSE: {} exists — a record is not a scratch path; pass \
                   --trace-out <fresh name> or move the old record first", args.trace_out);
        std::process::exit(2);
    }
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
    const WS_EX_TOPMOST: u32 = 0x0000_0008;
    let hwnd = unsafe {
        CreateWindowExW(WS_EX_TOPMOST, cls.as_ptr(), title.as_ptr(), WS_POPUP | WS_VISIBLE,
                        0, 0, scr_w, scr_h, 0, 0, inst, 0)
    };
    assert!(hwnd != 0, "CreateWindowExW failed");
    unsafe { ShowWindow(hwnd, SW_SHOW) };
    // v1's keyboard never arrived (0 keyed frames of 1800) and v1.1's SetForegroundWindow
    // repair FAILED ON THE REAL HOST TOO: the v1.1 recording came back keyed 0, moused 0.
    // The asymmetry was the diagnosis all along — the mouse survived v1 because it is POLLED
    // (GetCursorPos reads global state, focus-free) while the keyboard died because it was
    // QUEUED (WM_KEYDOWN reaches only the focused window, and Windows is entitled to refuse
    // a console-spawned process the foreground). v1.2 stops depending on what Windows may
    // refuse: keys are POLLED too (GetAsyncKeyState, the keyboard's GetCursorPos), Esc is
    // polled the same way, the window is TOPMOST so the operator sees what they steer, and
    // focus is DEMOTED from a dependency to a reported condition — the focus_foreground
    // line below is an instrument condition beside timer_1ms_granted, not a prerequisite.
    unsafe { SetForegroundWindow(hwnd); SetFocus(hwnd); }
    let focus_foreground = unsafe {
        let mut m = MSG { hwnd: 0, message: 0, wParam: 0, lParam: 0, time: 0,
                          pt: POINT { x: 0, y: 0 } };
        while PeekMessageW(&mut m, 0, 0, 0, PM_REMOVE) != 0 {
            TranslateMessage(&m); DispatchMessageW(&m);
        }
        GetForegroundWindow() == hwnd
    };
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
    let xi_get: Option<XiGetState> = if args.play { xinput_load() } else { None };
    let mut pad_seen = false;                  // a pad answered ERROR_SUCCESS at least once
    let mut padded: u32 = 0;                   // frames where the pad contributed input
    let mut end_armed = false;                 // end KEYS count only after an observed release
    let mut pad_end_armed = false;             // same law for the pad's end buttons
    let mut digests: Vec<(u32, u64)> = Vec::new();
    let mut digests_planted: Vec<(u32, u64)> = Vec::new();
    const PLANT_FRAME: u32 = 600;

    let mut fx_cam = Fx::new();
    let mut world = World::new();
    let mut cam = Cam { q: Q4 { w: ONE, x: 0, y: 0, z: 0 }, pitch_acc: 0, px: 0, py: 0 };
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
        // THE INPUT: live devices in --play (and RECORDED), the trace in --replay. Every
        // channel is POLLED global state — GetCursorPos for the mouse, GetAsyncKeyState for
        // keys (v1.2), XInputGetState for the pad (v1.3) — nothing depends on window focus.
        // The pad is FIRST-CLASS because the named host is a HANDHELD: its sticks emulate a
        // mouse only while the DESKTOP is foreground, and taking the foreground (the one thing
        // v1.2 verifiably achieved) is exactly what unplugs that emulation. Left stick walks,
        // right stick looks, B or Start ends the run. All channels merge into the SAME trace
        // vocabulary (keys dx dy), so replay does not know or care which device recorded.
        let (keys, dx, dy) = if args.play {
            let mut pt = POINT { x: 0, y: 0 };
            unsafe { GetCursorPos(&mut pt); SetCursorPos(center_x, center_y); }
            // v1.4: ARROW KEYS ALIAS WASD. The v1.3 run measured the last gap: pad_connected
            // true, padded 0, moused 1386 — the vendor layer keeps the physical sticks and
            // emits DESKTOP input (right stick as the mouse, which is where moused came from;
            // left stick as ARROW KEYS in the same scheme). The walk arrives on whatever
            // vocabulary the machine speaks; all of it lands in the same trace bits.
            let key = |vk: i32| -> u32 { unsafe { ((GetAsyncKeyState(vk) as u16 >> 15) & 1) as u32 } };
            let mut k = (key(0x57) | key(0x26))              // W  | Up
                | ((key(0x41) | key(0x25)) << 1)             // A  | Left
                | ((key(0x53) | key(0x28)) << 2)             // S  | Down
                | ((key(0x44) | key(0x27)) << 3);            // D  | Right
            // v1.5: END KEYS ARM ON AN OBSERVED RELEASE. v1.4 put Enter in the end-run set,
            // and Enter is the key that LAUNCHES the program from a shell — it was still
            // physically down when frame 0 polled, so the first real walk ended at birth
            // (frames 1, the activity line's own catch). Launch-time key state must not leak
            // into the run: an end key now counts only once every end key has been seen UP
            // during the run, so ending requires a press that BEGAN after launch.
            let end_down = unsafe {
                GetAsyncKeyState(VK_ESCAPE as i32) as u16 & 0x8000 != 0
                    || GetAsyncKeyState(0x0D) as u16 & 0x8000 != 0
            };
            if !end_down { end_armed = true }
            else if end_armed { QUIT.store(1, Ordering::SeqCst) }
            let (mut mdx, mut mdy) = ((pt.x - center_x) as i64, (pt.y - center_y) as i64);
            if let Some(get_state) = xi_get {
                let mut st = XiState::default();
                if unsafe { get_state(0, &mut st) } == 0 {
                    pad_seen = true;
                    const DEAD: i16 = 8000;
                    let g = st.pad;
                    if g.ly > DEAD { k |= 1 }                                // stick up    = W
                    if g.ly < -DEAD { k |= 4 }                               // stick down  = S
                    if g.lx < -DEAD { k |= 2 }                               // stick left  = A
                    if g.lx > DEAD { k |= 8 }                                // stick right = D
                    if g.rx.abs() > DEAD { mdx += (g.rx / 2048) as i64 }     // look
                    if g.ry.abs() > DEAD { mdy -= (g.ry / 2048) as i64 }     // stick up = look up
                    if g.buttons & 0x2010 == 0 { pad_end_armed = true }      // START | B both up
                    else if pad_end_armed { QUIT.store(1, Ordering::SeqCst) }
                    if k != 0 || g.rx.abs() > DEAD || g.ry.abs() > DEAD { padded += 1 }
                }
            }
            trace_rec.push((k, mdx, mdy));
            (k, mdx, mdy)
        } else {
            trace_in[frame as usize]
        };

        let _t0 = qpc();
        step_cam(&mut fx_cam, &mut cam, keys, dx, dy);     // the sim tick (certified rotation)
        if fx_cam.refused {
            eprintln!("FPSDEMO-REFUSE: the fixed-point substrate refused mid-walk (overflow \
                       ceiling) — this is a bug worth a paste, not a crash to hide");
            std::process::exit(3);
        }
        let _t_tick = qpc();
        let _view = (cam.px, cam.py, cam.q.w, cam.pitch_acc);   // the view export
        let t_view = qpc();
        raster_world(&mut fx_cam, &mut buf, &mut zbuf, cw, ch, &cam, &mut world);
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
        // Input traces are VERSION-PORTABLE by design (keys dx dy has one meaning across
        // versions; the v0 recording replays under v1.1 as a cross-version workload) while
        // digest chains are VERSION-BOUND — the chainless-record split, at the trace layer.
        let mut t = String::from("# fpsdemo v1.6 input trace: keys dx dy (one line per frame)
");
        for (k, dx, dy) in &trace_rec {
            t.push_str(&format!("{} {} {}
", k, dx, dy));
        }
        std::fs::write(&args.trace_out, &t).expect("trace write failed");
    }

    late_ns.sort_unstable();
    let (l50, l95, l99) = (pct(&late_ns, 50), pct(&late_ns, 95), pct(&late_ns, 99));
    let late_over = late_ns.iter().filter(|&&l| l > 1_000_000).count();
    let mut log = String::new();
    log.push_str(&format!(
        "fpsdemo v1.6 | host {} | power {} | scheduler {} | hz {} | res {}x{} | mode {} | qpf {}
",
        args.host, args.power, args.scheduler, args.hz, cw, ch,
        if args.play { "play" } else { "replay" }, freq));
    log.push_str(&format!("timer_1ms_granted {} | focus_foreground {} | xinput_loaded {} | \
pad_connected {}
",
                          timer_1ms_granted, focus_foreground,
                          if args.play { if xi_get.is_some() { "true" } else { "false" } }
                          else { "n/a" },
                          if args.play { if pad_seen { "true" } else { "false" } }
                          else { "n/a" }));
    log.push_str(&format!("frames {} | late_over_1ms {} | seg {}
", late_ns.len(), late_over, seg));
    log.push_str(&format!("late_ns p50 {} p95 {} p99 {}
", l50, l95, l99));
    for si in 0..n_segments as usize {
        let mut v = seg_raster[si].clone();
        if v.is_empty() { continue }
        v.sort_unstable();
        let mut pv = seg_present[si].clone();
        pv.sort_unstable();
        log.push_str(&format!(
            "seg {} n {} raster_ns {} {} {} present_ns {} {} {} late {}
",
            si, v.len(), v[0], pct(&v, 50), v[v.len() - 1],
            pv[0], pct(&pv, 50), pv[pv.len() - 1], seg_late[si]));
    }
    for (fr, d) in &digests {
        log.push_str(&format!("digest frame {} fnv64 {:016x}
", fr, d));
    }
    if args.play {
        // THE INSTRUMENT CARRIES ITS OWN CONTROL (probelog's lesson, at the input layer): the
        // v1 recording's defect was visible IN the trace — 0 keyed frames on a walk protocol —
        // but only to someone who opened the file. The activity line puts it in the summary.
        let keyed = trace_rec.iter().filter(|&&(k, _, _)| k != 0).count();
        let moused = trace_rec.iter().filter(|&&(_, dx, dy)| dx != 0 || dy != 0).count();
        log.push_str(&format!("trace {} frames -> {} | keyed {} | moused {} | padded {}
",
                              trace_rec.len(), args.trace_out, keyed, moused, padded));
        if keyed == 0 && padded == 0 {
            log.push_str("NOTE: no key and no pad input at any poll — if you were driving the \
                          sticks, check pad_connected above: false with sticks moving means \
                          XInput never saw the controller, which is its own finding
");
        }
    }
    if args.host == "-" {
        log.push_str("NOTE: no --host given — cost rows here are NOT_MEASURED; digests are \
                      host-independent and stand
");
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

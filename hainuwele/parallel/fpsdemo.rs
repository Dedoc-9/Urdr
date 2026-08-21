// SPDX-License-Identifier: AGPL-3.0-only
// Copyright (C) 2026 Daniel J. Dillberg
//
// fpsdemo.rs — THE CONFORMANCE CAMERA AND THE CANON TERRAIN (URDRFPD1, v1.17).
//
// v1.13 — THE WANDERER: fppose AND fpclip PROMOTED, BY THEIR OWN RULE. The dormancy law
// said those placements promote when a walk exposes their falsifier; the visual acceptance
// target (a third-person wanderer against the far field) is that walk. `--third` puts the
// certified biped on screen: the pose hierarchy and capsule certificate are fppose_rs's
// bytes, the clip sampler and canonical state machine are fpclip_rs's, both batteries run
// at every launch against the placements' own goldens (a failing launch refuses), and the
// avatar's screen form is a DECLARED capsule impostor, z-buffered like world geometry. The
// move keys drive the certified stepper (go on press, stop on release); the clip clock is
// the frame count over the declared 120 Hz cadence — no wall clock anywhere. Input moves
// the AVATAR; the render eye booms 3.5 units back along the camera's horizontal forward,
// both standing on the eye's own bilinear ground law. NOT claimed: the one-tick-late IK
// contract (feet ride the bilinear ground, stated); any collision between boom and terrain
// (the boom is a fixed offset, declared); the avatar's cost (the host prices --third
// before/after like every visual feature). --third off (the default) leaves every committed
// chain standing; --third requires the ladder path.
//
// v1.12 — THE COMPOSED SKY: R2d ADOPTED AS A VIEW. `--sky` replaces the gradient with the
// far-field channel wherever the terrain does not own the pixel: a pure function of view
// DIRECTION alone, world-fixed stars, cube-face quantization at 1/128 evaluated per 2x2
// block — v2 R2d's channel TYPE at its limit case (stars at infinity; the parallax quantum
// is infinite until regions arrive in the demo). THE PIXEL-IDENTITY CONTRACT: every
// terrain-owned pixel is BYTE-IDENTICAL with the sky on or off — the far field may never
// move a pixel the near field owns — verified per frame across the committed walk on the
// authoring container, with the sky counted non-vacuous (it paints) and sky-on replay
// deterministic (two runs, one chain). `--sky` is OFF by default, so every committed chain
// stands untouched; its cost rides INSIDE raster_ns, so the host's before/after (sky on vs
// off at the frozen reach) prices the feature the way every visual feature is priced. R2c's
// curvature drop is NOT adopted, with the arithmetic on record: at the shipped reaches
// (60/120 tiles) an earth-radius drop computes below a hundredth of a tile — adopting it
// would be the drop-blind vacuity planet.py's own plant refuses; it waits for a declared
// radius and a reach where it moves a pixel. The composition claimed is exactly what is
// painted: the terrain silhouette over a world-fixed far field.
//
// v1.11 — THE COMPETITIVE FREEZE. The defaults stop being placeholders and become the
// measured contract. REACH 60 IS THE COMPETITIVE DEFAULT: not because it feels right, but
// because it is the measured ceiling-clean operating point — the committed envelope
// (reachenv, URDRENV1) grades it FITS at 120 Hz BY CEILING with zero late frames on the
// committed walk, the only swept reach with that property. Reach 120 remains available
// explicitly (--reach 120) as the HIGH-REACH / VISTA mode: six times the original draw
// distance, measured viable at 120 Hz with less margin. Planetary reach is a DERIVATION,
// not a tuning knob (v2 R2c's horizon door), and belongs to a future adoption. THE CACHE
// RAIL DERIVES: with no --cache-cap given, the cap is 2x the ladder's own live footprint
// (the same resident-grid arithmetic capcost pins) — a declared MARGIN POLICY on the
// committed evidence (both measured working sets sat within 1.3x of footprint; every
// above-footprint cap measured count-identical to unbounded), never a proven optimum.
// --cache-cap 0 still means unbounded, any explicit N is honored, and the log declares
// which policy ran. COMPATIBILITY, stated: pre-v1.7 traces were recorded on the reach-20
// path — replaying one against its committed chain now requires --reach 20, because the
// default moved to the frozen competitive point.
//
// v1.10 — R4 ADOPTED: THE LAST UNBOUNDED MEMORY, BOUNDED. The committed walk measured the
// backing cache's working sets (22k entries at reach 60 up to 111k at 2000, a quarter to a
// third above prefill and climbing forever on a longer session). The v2 cache rung proved the
// law and its plants off-host; this version carries it into the demo: --cache-cap N bounds
// the backing map with deterministic insertion-order eviction (0, the default, keeps v1.9's
// unbounded behavior). THE IDENTITY CONTRACT IS ABSOLUTE: a cache over a pure function is a
// VIEW, eviction is a VIEW EVENT, and ANY cap must produce chains identical to the committed
// reach records — verified on the authoring container against the gate's own committed oracle
// before delivery, at caps from starvation to unbounded. The log grows one line per ladder
// run: cache_cap | occupancy | recomputes | evictions — the cap freeze follows the reach
// pattern, swept then chosen from numbers. Grid memory was already bounded by the ladder;
// with this, no allocation in the demo grows without a declared bound.
//
// v1.9 — THE RESIDENT GRID, the lever v1.8's sweep named, adopted by before/after. Every quad
// paid four hashed probes for corner heights and adjacent quads re-probed shared corners; each
// ring now holds its heights in a flat Vec indexed by lattice position, refilled from the
// backing cache only when the camera crosses that ring's stride boundary (ring k rebases every
// 2^k tiles — the refill amortizes, and rebase frames are visible honestly in the worst
// column). THE VALUES ARE IDENTICAL: this is a lookup restructure, not an arithmetic change,
// so every v1.8 chain stands at every reach — verified on the authoring container against the
// operator's own sweep digests before delivery. Grid memory is BOUNDED by the ladder; the
// backing cache remains unbounded (R4's debt, still named, still owed).
//
// v1.8 — THE SWEEP'S TWO CATCHES, REPAIRED. First: v1.7's log transparency lines never
// shipped — the version line still read v1.6, no reach field, no ring lines, no prefill_tiles
// — because an edit was applied without asserting it matched. An edit without an assert is a
// hope; every edit in this repair asserted. Second: the sweep measured the envelope (reach 20
// FITS 120 Hz; 500 already ~13.6-16.4 ms; 63488 ~38 ms) and thereby measured the per-vertex
// quaternion sandwich as the ring path's dominant cost. The rotation is IDENTICAL for every
// vertex, so v1.8 derives the rotation matrix from the CERTIFIED vrotate exactly three times
// per frame (the basis images, Q16) and applies it per vertex in plain i64 — the certified
// kernel still owns the rotation; the matrix is its per-frame shadow. The near path
// (reach <= 24) still runs vrotate per vertex, UNTOUCHED: the pinned v1.6 chains remain the
// identity contract. Ring-path chains change with the arithmetic (version-bound, as always);
// silhouette and seam laws re-verified on the authoring container before delivery.
//
// v1.7 — THE REACH SWEEP, STRICTLY AN EXPERIMENT. R2b's pictures answered the architectural
// question (reach, not local resolution, is the dominant fidelity/performance knob) and showed
// the full-reach ladder is photo-mode territory on the authoring container. This version turns
// that finding into a host-derived operating envelope under THREE SEPARATE CONTRACTS:
//
//   * RUNTIME — `--reach <tiles>` (default 20 = the v1.6 window) derives the ring ladder at
//     launch by the v2 R2a machinery, ported: pixel budget FIXED at 35 so reach is the ONE
//     variable; strides double; a stride seats only past its derived d_min; rings overlap one
//     coarse tile. The derived ladder is PRINTED in the log, line per ring, so the derivation
//     is checkable against hainuwele/v2/lod.py ring for ring.
//   * PERFORMANCE — each reach setting is classified independently against the measured 120 Hz
//     budget from its own named cost rows on the committed walk; candidate points 2000 / 10000 /
//     63488 tiles (~6 / 30 / 190 km) are CANDIDATES, and the Ally decides. Container numbers
//     stayed pictures; the host A/B is what turns the trade surface into evidence.
//   * IDENTITY — reach <= 24 never enters the ring path: raster_world runs UNTOUCHED and the
//     pinned v1.6 chains (v0-trace, walk_real, all-zero) are the regression contract, verified
//     on the authoring container before delivery. The expanded vista must not leak sky at a
//     ring seam — checked against a monolith render in the authoring harness (a seam pixel the
//     monolith paints terrain and the ladder paints sky is the falsifier).
//
// PREFILL IS A START CONDITION, NOT A FRAME COST. The ladder's cache cold-fill runs BEFORE the
// frame timer starts, its tile count prints in the log (`prefill_tiles`), and its wall-clock
// goes to stderr only — mixing a 0.6-2.8 s fill into the 15 ms frame-0 convention would
// contaminate the measurement rather than describe reality. The cache is UNBOUNDED (grows as
// the walk pulls ring edges); that defect is named here and owned by v2's R4 rung, not hidden.
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
// v1.17 — HALF A WORLD UNIT. At 2 units, with the eye 3 units above ground, pitching down past
// about atan(3/2) put the ground directly beneath INSIDE the near plane, where nothing can be
// projected at all — the operator saw it as a hole along the bottom of the view once v1.16 had
// removed the whole-quad hole underfoot. That was the plane doing its job, not a clipping
// defect, and only moving the plane moves it: the depression angle at which ground beneath falls
// inside goes from ~56 degrees to ~80.5.
//
// THE TRADE IS REAL, BOUNDED, AND IT CHOSE THIS CONSTANT. Projected coordinates scale as
// 1/NEAR8 and the depth term as their square times the reach, so a nearer plane spends
// admissible REACH. A quarter-unit plane was measured first and REFUSED 1080p at reach 120 — a
// fidelity/reach cell this arc had explicitly frozen — so it was rejected in favour of a half
// unit, which keeps 720p and 1080p at reach 60 and 120 with the worst case at 29% of the i64
// ceiling. See `projection_bound_ok`.
const NEAR8: i64 = 128;                // near clip in Q8 camera units — v1's 12-unit clip threw
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

// ---- v1.7: the reach ladder (R2a's machinery, ported verbatim in rule if not in tongue) ------
//   ONE VARIABLE: reach. The pixel budget is FIXED at 35 (visibly what v1.6 already accepts at
//   its window edge); strides double; a stride is admissible only past the distance where its
//   octave-prefix error bound projects under the budget; rings overlap one coarse tile so seams
//   are painted from behind. The derived ladder is PRINTED in the log so the runtime contract
//   is checkable against the v2 model line by line.
const LOD_PIX: i64 = 35;
const LOD_R0: i64 = 24;

fn lod_kept_mask(stride: i64) -> u32 {
    let mut m = 0u32;
    for (li, &(cell, _amp)) in W_LAYERS.iter().enumerate() {
        if cell >= 2 * stride || li == 0 { m |= 1 << li }
    }
    m
}

fn lod_error_bound(stride: i64) -> i64 {
    let kept = lod_kept_mask(stride);
    let mut dropped = 0i64;
    for (li, &(_cell, amp)) in W_LAYERS.iter().enumerate() {
        if kept & (1 << li) == 0 { dropped += amp * VMAX }
    }
    floordiv(floordiv(dropped * W_HS, W_RAWMAX), H_SCALE) + 2
}

fn lod_d_min(stride: i64, focal: i64) -> i64 {
    let e = lod_error_bound(stride);
    (e * focal + (LOD_PIX * TILE - 1)) / (LOD_PIX * TILE)
}

fn lod_schedule(reach: i64, focal: i64) -> Vec<(i64, i64, i64)> {
    // (stride, inner, outer) in tiles — mirrors hainuwele/v2/lod.py schedule(35, k)
    if reach <= LOD_R0 {
        return vec![(1, 0, reach)];
    }
    let mut starts: Vec<i64> = vec![0];
    let mut k = 1usize;
    loop {
        let stride = 1i64 << k;
        let prev = starts[k - 1];
        let mut start = std::cmp::max(if prev > 0 { 2 * prev } else { LOD_R0 },
                                      lod_d_min(stride, focal));
        if start <= prev { start = 2 * prev }
        if start >= reach || k >= 20 { break }
        starts.push(start);
        k += 1;
    }
    let mut rings = Vec::new();
    for (idx, &st) in starts.iter().enumerate() {
        let stride = 1i64 << idx;
        let outer = if idx + 1 < starts.len() { starts[idx + 1] + stride } else { reach };
        let inner = if idx == 0 { 0 } else { st - stride };
        rings.push((stride, inner, outer));
    }
    rings
}

// v1.9: THE RESIDENT GRID. The v1.8 sweep named the hashed height lookup as the next lever:
// every quad paid four map probes and adjacent quads re-probed shared corners. Each ring now
// holds its heights in a flat Vec indexed by lattice position, refilled from the backing cache
// only when the camera crosses that ring's stride boundary (ring k rebases every 2^k tiles, so
// the refill amortizes and the rebase spike is visible honestly in the worst column). Values
// are IDENTICAL — this is a lookup restructure, not an arithmetic change — so every v1.8
// chain stands, at every reach, verifiable against the operator's own sweep paste.
struct RingGrid { stride: i64, cells: i64, base_x: i64, base_y: i64, filled: bool,
                  side: i64, heights: Vec<i64> }

// v1.11 — THE COMPETITIVE FREEZE's cache policy: when no --cache-cap is given, the rail
// derives from the ladder's own live footprint (the sum of resident-grid areas — the same
// arithmetic capcost pins against committed records) times two: a MARGIN POLICY on measured
// evidence, never a proven optimum. Above the footprint the rail is measured FREE — counts
// equal unbounded, chains identical — so the derived default bounds memory without buying
// a single recompute on the committed walk.
fn derived_cap(rings: &[(i64, i64, i64)]) -> usize {
    rings.iter().map(|&(stride, _inn, out)| {
        let cells = out / stride + 1;
        let side = 2 * cells + 3;
        (side * side) as usize
    }).sum::<usize>() * 2
}

// v1.10 — R4 ADOPTED (v2/cache.py's law, in the demo): the backing map is BOUNDED with
// deterministic insertion-order eviction. A cache over a pure function is a VIEW and eviction
// is a VIEW EVENT: any cap must produce IDENTICAL digest chains — capacity changes cost,
// never values — and the committed reach records are the oracle that claim is checked
// against. --cache-cap 0 (the default) keeps the unbounded v1.9 behavior; the cap freeze
// follows the reach pattern: sweep, measure, then choose from the numbers.
struct LodWorld {
    cache: std::collections::HashMap<(i64, i64, i64), i64>,
    ring: std::collections::VecDeque<(i64, i64, i64)>,
    cap: usize,
    recomputes: u64,
    evictions: u64,
    grids: Vec<RingGrid>,
}
impl LodWorld {
    fn new(rings: &[(i64, i64, i64)], cap: usize) -> LodWorld {
        let grids = rings.iter().map(|&(stride, _inn, out)| {
            let cells = out / stride + 1;
            let side = 2 * cells + 3;                     // corners reach cells+1 on each axis
            RingGrid { stride, cells, base_x: 0, base_y: 0, filled: false, side,
                       heights: vec![0; (side * side) as usize] }
        }).collect();
        LodWorld { cache: std::collections::HashMap::new(),
                   ring: std::collections::VecDeque::new(), cap,
                   recomputes: 0, evictions: 0, grids }
    }
    fn h(&mut self, x: i64, y: i64, stride: i64) -> i64 {
        if let Some(&v) = self.cache.get(&(stride, x, y)) { return v }
        self.recomputes += 1;
        let kept = lod_kept_mask(stride);
        let mut raw = 0i64;
        for (li, &(cell, amp)) in W_LAYERS.iter().enumerate() {
            if kept & (1 << li) != 0 { raw += amp * noise16(W_SEED, li as i64, cell, x, y) }
        }
        let v = floordiv(floordiv(raw * W_HS, W_RAWMAX), H_SCALE);
        // THE CEILING IS ENFORCED HERE, LOCALLY, BY A DRAIN — not by trusting the pairing
        // invariant (ring.len() == cache.len()) that the rest of this impl maintains. In every
        // reachable state the loop runs 0 or 1 times, so victims, counts and chains are
        // unchanged; if a future edit ever lets the states drift, the drain still converges to
        // the cap and the debug assert names the corruption at its source.
        debug_assert_eq!(self.ring.len(), self.cache.len(),
                         "ring/cache drift — an eviction bug upstream of this miss");
        if self.cap > 0 {
            while self.cache.len() >= self.cap {
                let Some(victim) = self.ring.pop_front() else {
                    debug_assert!(false, "cache over cap with an empty ring — states drifted");
                    break;
                };
                self.cache.remove(&victim);
                self.evictions += 1;
            }
        }
        self.cache.insert((stride, x, y), v);
        self.ring.push_back((stride, x, y));
        v
    }
    fn rebase(&mut self, ri: usize, base_x: i64, base_y: i64) {
        let g = &mut self.grids[ri];
        if g.filled && g.base_x == base_x && g.base_y == base_y { return }
        g.base_x = base_x;
        g.base_y = base_y;
        g.filled = true;
        let (stride, cells, side) = (g.stride, g.cells, g.side);
        for gy in -(cells + 1)..=(cells + 1) {
            for gx in -(cells + 1)..=(cells + 1) {
                let v = self.h(base_x + gx * stride, base_y + gy * stride, stride);
                let idx = ((gy + cells + 1) * side + (gx + cells + 1)) as usize;
                self.grids[ri].heights[idx] = v;
            }
        }
    }
    fn prefill(&mut self, cx: i64, cy: i64, rings: &[(i64, i64, i64)]) -> u64 {
        let mut n = 0u64;
        for (ri, &(stride, _inn, _out)) in rings.iter().enumerate() {
            let bx = floordiv(cx, stride) * stride;
            let by = floordiv(cy, stride) * stride;
            self.rebase(ri, bx, by);
            n += (self.grids[ri].side * self.grids[ri].side) as u64;
        }
        n
    }
}

fn isqrt64(n: i64) -> i64 {
    if n <= 0 { return 0 }
    let mut x = n;
    let mut y = (x + 1) / 2;
    while y < x { x = y; y = (x + n / x) / 2 }
    x
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

// ---- v1.7: the ring renderer — the reach experiment's raster path ----------------------------
//   Ring 0 (stride 1) is the canon exactly; far rings sample the canon's octave prefix at their
//   stride. Seams are covered by one coarse tile of paint-behind overlap and the z-buffer; the
//   fog ruler is the reach itself, so aerial perspective scales with the world instead of ending
//   at a wall. When reach <= LOD_R0 this path is NEVER entered — raster_world runs, unchanged,
//   and the pinned v1.6 chains stand as the identity contract.
fn raster_rings(fx: &mut Fx, buf: &mut [u32], zbuf: &mut [i32], w: i32, h: i32,
                cam: &Cam, lod: &mut LodWorld, rings: &[(i64, i64, i64)]) {
    for y in 0..h {
        let t = (y * 200 / h.max(1)) as u32;
        let c = (30 << 16) | ((70 + t / 3) << 8) | (130 + t / 2).min(255);
        let row = (y * w) as usize;
        for x in 0..w as usize { buf[row + x] = c }
    }
    for z in zbuf.iter_mut().take((w * h) as usize) { *z = i32::MAX }

    let f = h as i64 * 2;
    let (cx, cy) = (w as i64 / 2, h as i64 / 2);
    let reach = rings[rings.len() - 1].2;
    let farq = reach * TILE * 256;
    let qc = qconj(cam.q);
    // v1.8: THE ROTATION IS THE SAME FOR EVERY VERTEX, so it is derived from the CERTIFIED
    // vrotate exactly three times per frame (the basis images) and applied per vertex as a
    // plain integer matrix in Q16 — the v1.7 sweep measured the per-vertex quaternion
    // sandwich as the dominant cost of the ring path. The certified kernel still owns the
    // rotation; the matrix is its per-frame shadow, and the near path (reach <= 24) still
    // runs vrotate per vertex, untouched, holding the pinned chains.
    let bx = fx.vrotate(qc, V3 { x: ONE, y: 0, z: 0 });
    let by = fx.vrotate(qc, V3 { x: 0, y: ONE, z: 0 });
    let bz = fx.vrotate(qc, V3 { x: 0, y: 0, z: ONE });
    let m = [bx.x >> 16, by.x >> 16, bz.x >> 16,
             bx.y >> 16, by.y >> 16, bz.y >> 16,
             bx.z >> 16, by.z >> 16, bz.z >> 16];          // Q16, |entry| <= 65536
    let ctx = floordiv(cam.px >> 8, TILE);
    let cty = floordiv(cam.py >> 8, TILE);
    let (rx8, ry8) = (cam.px - ((ctx * TILE) << 8), cam.py - ((cty * TILE) << 8));
    let (u, v) = (rx8 / TILE, ry8 / TILE);
    let (h00, h10) = (lod.h(ctx, cty, 1) << 8, lod.h(ctx + 1, cty, 1) << 8);
    let (h01, h11) = (lod.h(ctx, cty + 1, 1) << 8, lod.h(ctx + 1, cty + 1, 1) << 8);
    let hx0 = h00 + (h10 - h00) * u / 256;
    let hx1 = h01 + (h11 - h01) * u / 256;
    let eye8 = hx0 + (hx1 - hx0) * v / 256 + (3 << 8);

    for (ri, &(stride, inn, out)) in rings.iter().enumerate().rev() {
        let bx = floordiv(ctx, stride) * stride;
        let by = floordiv(cty, stride) * stride;
        lod.rebase(ri, bx, by);
        let (side, gcells) = (lod.grids[ri].side, lod.grids[ri].cells);
        let cells = out / stride + 1;
        for gy in -cells..cells {
            for gx in -cells..cells {
                let (wx, wy) = (bx + gx * stride, by + gy * stride);
                let m0 = (wx - ctx).abs().max((wy - cty).abs());
                let m1 = (wx + stride - ctx).abs().max((wy + stride - cty).abs());
                if m0.min(m1) > out || m0.max(m1) < inn { continue }
                let gi = |dx: i64, dy: i64| -> usize {
                    ((gy + dy + gcells + 1) * side + (gx + dx + gcells + 1)) as usize
                };
                let ha = lod.grids[ri].heights[gi(0, 0)];
                let hb = lod.grids[ri].heights[gi(1, 0)];
                let hc = lod.grids[ri].heights[gi(0, 1)];
                let hd = lod.grids[ri].heights[gi(1, 1)];
                let mut cam4 = [(0i64, 0i64, 0i64); 4];
                let mut any_in = false;
                for (i, (px_, py_, hh)) in [(wx, wy, ha), (wx + stride, wy, hb),
                                            (wx, wy + stride, hc),
                                            (wx + stride, wy + stride, hd)].iter().enumerate() {
                    let vx = ((px_ * TILE) << 8) - cam.px;          // Q8 world delta
                    let vy = ((py_ * TILE) << 8) - cam.py;
                    let vz = (hh << 8) - eye8;
                    // Q8 x Q16 -> >>16 -> Q8 camera space; |v| <= reach*TILE*256 < 2^28,
                    // |m| <= 2^16, so each product stays under 2^44 — i64 with room to spare
                    let rx = (m[0] * vx + m[1] * vy + m[2] * vz) >> 16;
                    let d8 = (m[3] * vx + m[4] * vy + m[5] * vz) >> 16;
                    let rz = (m[6] * vx + m[7] * vy + m[8] * vz) >> 16;
                    if d8 >= NEAR8 { any_in = true }
                    cam4[i] = (rx, d8, rz);
                }
                // A quad entirely behind the near plane still contributes nothing; a quad with
                // ONE corner behind it now contributes the part in front, which is the repair.
                if !any_in { continue }
                let h4 = ha + hb + hc + hd;
                let havg = h4 / 4;
                let jit = ((wx.wrapping_mul(73) ^ wy.wrapping_mul(151)) & 7) - 3;
                let lerp = |a: (i64, i64, i64), b: (i64, i64, i64), tn: i64, td: i64| {
                    (a.0 + (b.0 - a.0) * tn / td, a.1 + (b.1 - a.1) * tn / td,
                     a.2 + (b.2 - a.2) * tn / td)
                };
                let sand = (150 + jit, 137 + jit, 94);
                let grass = (56 + jit * 2, 118 + jit * 2, 48 + jit);
                let rock = (99 + jit, 86 + jit, 72 + jit);
                let snow = (224, 227, 234);
                let (br, bg, bb) = if havg <= 4 { sand }
                    else if havg <= 10 { lerp(sand, grass, havg - 4, 6) }
                    else if havg <= 16 { lerp(grass, rock, havg - 10, 6) }
                    else if havg <= 21 { lerp(rock, snow, havg - 16, 5) }
                    else { snow };
                let st = stride * TILE;
                let lam = |ax: i64, ay: i64, az: i64, bx2: i64, by2: i64, bz2: i64| -> i64 {
                    let (nx, ny, nz) = (ay * bz2 - az * by2, az * bx2 - ax * bz2,
                                        ax * by2 - ay * bx2);
                    let (nx, ny, nz) = if nz < 0 { (-nx, -ny, -nz) } else { (nx, ny, nz) };
                    let dot = -2 * nx - ny + 3 * nz;
                    if dot <= 0 { return 0 }
                    let nn = isqrt64(nx * nx + ny * ny + nz * nz);
                    if nn == 0 { return 0 }
                    (dot * 256 / (nn * 4)).min(256)
                };
                let l1 = lam(st, 0, hb - ha, 0, st, hc - ha);
                let l2 = lam(0, st, hd - hb, -st, 0, hc - hd);
                let lit = |l: i64, c: i64| (c * (60 + 196 * l / 256) / 160).clamp(0, 255);
                let camtris = [([cam4[0], cam4[1], cam4[2]],
                                (lit(l1, br), lit(l1, bg), lit(l1, bb))),
                               ([cam4[1], cam4[3], cam4[2]],
                                (lit(l2, br), lit(l2, bg), lit(l2, bb)))];
                // CLIP FIRST, PROJECT AFTER. A projected vertex behind the near plane is
                // meaningless, so the cut happens in camera space and only survivors divide.
                // Each source triangle yields 0, 1 or 2 output triangles: at most four.
                let pj = |v: CamV| (cx + v.0 * f / v.1, cy - v.2 * f / v.1, v.1);
                let z3 = (0i64, 0i64, 0i64);
                let mut tris = [(z3, z3, z3, z3); 4];
                let mut ntris = 0usize;
                for (ct, tint) in camtris.iter() {
                    let (cl, cn) = clip_near(ct);
                    for k in 1..cn.max(1) - 1 {
                        tris[ntris] = (pj(cl[0]), pj(cl[k]), pj(cl[k + 1]), *tint);
                        ntris += 1;
                    }
                }
                for &(a0, b0, c0, (tr, tg, tb)) in tris[..ntris].iter() {
                    let (a, mut b, mut cc) = (a0, b0, c0);
                    if (a.0 < 0 && b.0 < 0 && cc.0 < 0) || (a.1 < 0 && b.1 < 0 && cc.1 < 0)
                        || (a.0 >= w as i64 && b.0 >= w as i64 && cc.0 >= w as i64)
                        || (a.1 >= h as i64 && b.1 >= h as i64 && cc.1 >= h as i64) { continue }
                    let mut area = (b.0 - a.0) * (cc.1 - a.1) - (b.1 - a.1) * (cc.0 - a.0);
                    if area == 0 { continue }
                    if area < 0 { std::mem::swap(&mut b, &mut cc); area = -area; }
                    let d3 = ((a.2 + b.2 + cc.2) / 3).clamp(0, farq);
                    let dim = 14 + 18 * (farq - d3) / farq;
                    let ch3 = |near: i64, sky: i64| ((near * dim + sky * (32 - dim)) / 32) as u32;
                    let col = (ch3(tr, 60) << 16) | (ch3(tg, 120) << 8) | ch3(tb, 190);
                    let x_lo = a.0.min(b.0).min(cc.0).max(0);
                    let x_hi = a.0.max(b.0).max(cc.0).min(w as i64 - 1);
                    let y_lo = a.1.min(b.1).min(cc.1).max(0);
                    let y_hi = a.1.max(b.1).max(cc.1).min(h as i64 - 1);
                    if x_lo > x_hi || y_lo > y_hi { continue }
                    let (dw0x, dw0y) = (-(b.1 - a.1), b.0 - a.0);
                    let (dw1x, dw1y) = (-(cc.1 - b.1), cc.0 - b.0);
                    let (dw2x, dw2y) = (-(a.1 - cc.1), a.0 - cc.0);
                    let mut w0r = (b.0 - a.0) * (y_lo - a.1) - (b.1 - a.1) * (x_lo - a.0);
                    let mut w1r = (cc.0 - b.0) * (y_lo - b.1) - (cc.1 - b.1) * (x_lo - b.0);
                    let mut w2r = (a.0 - cc.0) * (y_lo - cc.1) - (a.1 - cc.1) * (x_lo - cc.0);
                    for py in y_lo..=y_hi {
                        let row = (py * w as i64) as usize;
                        let (mut w0, mut w1, mut w2) = (w0r, w1r, w2r);
                        let mut entered = false;
                        for px in x_lo..=x_hi {
                            if w0 >= 0 && w1 >= 0 && w2 >= 0 {
                                entered = true;
                                let zn = w1 * a.2 + w2 * b.2 + w0 * cc.2;
                                let d = (zn / area) as i32;
                                let i = row + px as usize;
                                if d < zbuf[i] { zbuf[i] = d; buf[i] = col }
                            } else if entered { break }
                            w0 += dw0x; w1 += dw1x; w2 += dw2x;
                        }
                        w0r += dw0y; w1r += dw1y; w2r += dw2y;
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
    let clip_ok = near_clip_battery();
    println!("selfcheck near clip      : {}", if clip_ok { "MATCHES CONTRACT" }
             else { "MISMATCH — the near plane is NOT clipped correctly" });
    ok &= clip_ok;
    // v1.13: the promoted placements run their batteries at every launch, same door
    let mut fxp = Fx::new();
    let pse_ok = pse_battery(&mut fxp);
    println!("selfcheck fppose battery : {}", if pse_ok { "MATCHES GOLDEN" }
             else { "MISMATCH — the pose path is NOT the certified path" });
    ok &= pse_ok;
    let mut fxc = Fx::new();
    let clp_ok = clp_battery(&mut fxc);
    println!("selfcheck fpclip battery : {}", if clp_ok { "MATCHES GOLDEN" }
             else { "MISMATCH — the clip path is NOT the certified path" });
    ok &= clp_ok;
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
    // NOTE, because the next caller will not read this file top to bottom: this is the tree's
    // floor division for a POSITIVE divisor. With d < 0 and n < 0 the quotient is positive and
    // the -1 correction is wrong, so every caller normalises the sign first. Every existing
    // call passes TILE or a ring stride; `clip_near` is the first to divide by a difference,
    // and it normalises rather than widening this helper under the pinned callers.
    if n % d != 0 && n < 0 { n / d - 1 } else { n / d }
}

// v1.16 — THE NEAR PLANE IS CLIPPED, NOT DISCARDED.
//
// THE DEFECT THE OPERATOR SAW. The eye stands 3 world units above bilinear ground and a tile is
// 3 units wide, so the quad the camera is standing on always has a corner at near-zero forward
// depth. The ring renderer rejected the WHOLE QUAD on the first such corner (`clipped = true;
// break`), which put a permanent tile-sized hole underfoot: look down, or walk onto ground that
// rises close, and you see through the floor to the sky. Raising the eye cannot help, because a
// vertex directly beneath the camera has forward depth near zero at any height. The near plane
// is the one plane a scanline rasteriser must genuinely clip against — the side planes are
// handled by scanning screen space, but depth is interpolated rather than rasterised, so there
// is no screen-space dodge for this one.
//
// Sutherland-Hodgman against a SINGLE plane: a triangle becomes nothing, a triangle, or a quad.
// Bounded work in one place, not a general clipper.
//
// THE ROUNDING IS DECLARED AND IT IS FLOOR, the same rule `floordiv` states everywhere else in
// this tree. It is applied to the interpolation PRODUCT, per component — no parameter `t` is
// ever materialised, because an integer t would be 0 or 1 and would collapse the cut onto a
// vertex. One division per component, and the sign is normalised so `floordiv` is used inside
// the domain where it is correct.
//
// Magnitudes: |rx|, |rz| and |d8| are bounded by reach * TILE * 256 < 2^28, so a component
// difference times a depth difference stays under 2^56 and i64 has room.
type CamV = (i64, i64, i64);                       // (right, forward, up) in Q8 camera space

// THE OVERFLOW BOUND, AS A LAUNCH DOOR RATHER THAN AS A HOPE.
//
// This was reachable BEFORE this rung and nothing checked it. Camera-space Q8 coordinates are
// bounded by `reach * TILE * 256`; a projected coordinate by `w/2 + that * f / NEAR8`; an edge
// function by about 4 M^2; and the depth interpolation `zn` by 3 * 4 M^2 * R, the binding term.
// At `--reach 500` under the OLD plane that product already sat within a factor of two of the
// i64 ceiling and at reach 1000 it passed it — silently, because nothing looked. The admissible
// range had a boundary nobody had named; this makes it explicit instead of leaving the
// arithmetic ceiling to be met by accident.
//
// The check runs in i128 so THE CHECK ITSELF cannot overflow, and it REFUSES rather than trusting
// runtime arithmetic to fail visibly. The bound is deliberately WORST-CASE and therefore
// conservative: it assumes a vertex simultaneously at maximum reach and at the near plane, which
// the geometry does not actually produce. A refusal that is too strict is visible and can be
// argued with; an overflow is silent and wrong.
fn projection_bound(reach: i64, w: i32, h: i32) -> i128 {
    let r = (reach * TILE * 256) as i128;
    let f = (h as i64 * 2) as i128;
    let m = (w.max(h) as i128) / 2 + r * f / NEAR8 as i128;
    12 * m * m * r
}

fn projection_bound_ok(reach: i64, w: i32, h: i32) -> bool {
    projection_bound(reach, w, h) <= i64::MAX as i128
}

fn max_admissible_reach(w: i32, h: i32) -> i64 {
    let (mut lo, mut hi) = (8i64, 200_000i64);
    if projection_bound_ok(hi, w, h) { return hi }
    while lo < hi {
        let mid = (lo + hi + 1) / 2;
        if projection_bound_ok(mid, w, h) { lo = mid } else { hi = mid - 1 }
    }
    lo
}

fn clip_near(tri: &[CamV; 3]) -> ([CamV; 4], usize) {
    let mut out = [(0i64, 0i64, 0i64); 4];
    let mut n = 0usize;
    for i in 0..3 {
        let a = tri[i];
        let b = tri[(i + 1) % 3];
        let (ain, bin) = (a.1 >= NEAR8, b.1 >= NEAR8);
        if ain { out[n] = a; n += 1; }
        if ain != bin {
            let (mut num, mut den) = (NEAR8 - a.1, b.1 - a.1);
            if den < 0 { num = -num; den = -den; }     // floordiv's domain, kept
            out[n] = (a.0 + floordiv((b.0 - a.0) * num, den), NEAR8,
                      a.2 + floordiv((b.2 - a.2) * num, den));
            n += 1;
        }
    }
    (out, n)
}

// THE CLIP CARRIES ITS OWN DOOR. Every other certified path in this demo proves itself at
// launch and refuses to run if it cannot; a repair to the one plane the rasteriser must clip
// against does not get to be the exception. Cheap enough to run on every start.
fn near_clip_battery() -> bool {
    let front = [(100i64, 5000i64, 40i64), (-90, 4000, 20), (30, 6000, -10)];
    let behind = [(100i64, 10i64, 40i64), (-90, 0, 20), (30, -500, -10)];
    let one_out = [(100i64, 10i64, 40i64), (-90, 4000, 20), (30, 6000, -10)];
    let two_out = [(100i64, 10i64, 40i64), (-90, 0, 20), (30, 6000, -10)];
    if clip_near(&front).1 != 3 { return false }          // wholly in front: untouched
    if clip_near(&behind).1 != 0 { return false }         // wholly behind: nothing
    let (o, n) = clip_near(&one_out);
    if n != 4 { return false }                            // ONE corner out is a QUAD, not a hole
    if (0..n).filter(|&k| o[k].1 == NEAR8).count() != 2 { return false }
    if clip_near(&two_out).1 != 3 { return false }
    // THE PROPERTY THE OLD PATH TRADED A HOLE FOR: nothing reaches the divide with a depth the
    // projection cannot survive. Swept, not argued.
    for a in [-4000i64, -1, 0, NEAR8 - 1, NEAR8, NEAR8 + 1, 90000] {
        for b in [-3000i64, 0, NEAR8, 77777] {
            for c in [-2i64, NEAR8, 1234567] {
                let (o, n) = clip_near(&[(7, a, 3), (-11, b, 5), (2, c, -9)]);
                for k in 0..n { if o[k].1 < NEAR8 { return false } }
            }
        }
    }
    // THE BOUND BITES AND IS NOT VACUOUS: the frozen cells must pass and something must refuse,
    // or the door is either decoration or a wall. The two operating points this arc froze are
    // named here so a future edit to the plane cannot quietly take one away.
    if !projection_bound_ok(60, 1280, 720) { return false }
    if !projection_bound_ok(120, 1280, 720) { return false }
    if !projection_bound_ok(60, 1920, 1080) { return false }
    if !projection_bound_ok(120, 1920, 1080) { return false }
    if projection_bound_ok(200_000, 1280, 720) { return false }
    let cap = max_admissible_reach(1280, 720);
    if !projection_bound_ok(cap, 1280, 720) { return false }
    if projection_bound_ok(cap + 1, 1280, 720) { return false }
    // the cut does not depend on which way the edge was walked (floordiv's domain, kept)
    clip_near(&[(0i64, 0i64, 0i64), (1000, 1024, 1000), (0, 4000, 0)]).1
        == clip_near(&[(1000i64, 1024i64, 1000i64), (0, 0, 0), (0, 4000, 0)]).1
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
// ---- v1.12: the far field (R2d adopted as a VIEW) ---------------------------------------------
// The sky stops being a gradient and becomes the far-field channel: a pure function of view
// DIRECTION alone, world-fixed, painted ONLY into pixels the terrain does not own. This is
// v2 R2d's channel type at its limit case — stars at infinity, so the parallax quantum is
// infinite (a finite quantum becomes meaningful when regions arrive in the demo). THE
// PIXEL-IDENTITY CONTRACT: a terrain-owned pixel (zbuf written) is BYTE-IDENTICAL with the
// sky on or off — the far field may never move a pixel the near field owns — and --sky off
// (the default) leaves every committed chain standing. Directions are quantized on cube
// faces at 1/128 and evaluated per 2x2 pixel block (the sky's own declared quanta); the
// hash is a cheap integer mix, not sha — the channel's LAWS are v2's, its art is the demo's.
fn star_hash(a: i64, b: i64, c: i64) -> u64 {
    let mut h = 0xcbf29ce484222325u64;
    for v in [a, b, c] {
        h ^= v as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h ^= h >> 29;
    h = h.wrapping_mul(0xbf58476d1ce4e5b9);
    h ^ (h >> 32)
}

fn star_sky(fx: &mut Fx, buf: &mut [u32], zbuf: &mut [i32], w: i32, h: i32, cam: &Cam) {
    let qc = qconj(cam.q);
    let bx = fx.vrotate(qc, V3 { x: ONE, y: 0, z: 0 });
    let by = fx.vrotate(qc, V3 { x: 0, y: ONE, z: 0 });
    let bz = fx.vrotate(qc, V3 { x: 0, y: 0, z: ONE });
    let m = [bx.x >> 16, by.x >> 16, bz.x >> 16,
             bx.y >> 16, by.y >> 16, bz.y >> 16,
             bx.z >> 16, by.z >> 16, bz.z >> 16];
    let f = h as i64 * 2;
    let (cx, cy) = (w as i64 / 2, h as i64 / 2);
    let mut sy = 0i32;
    while sy < h {
        let mut sx = 0i32;
        while sx < w {
            // a block fully owned by terrain skips the math entirely
            let mut any_sky = false;
            for oy in 0..2i32 {
                for ox in 0..2i32 {
                    let (px, py) = (sx + ox, sy + oy);
                    if px < w && py < h && zbuf[(py * w + px) as usize] == i32::MAX {
                        any_sky = true;
                    }
                }
            }
            if !any_sky { sx += 2; continue }
            // the block-center ray, camera space (x right, y forward, z up; screen y down),
            // lifted to world space through the transpose of the certified rotation's shadow
            let dx = sx as i64 + 1 - cx;
            let dz = cy - (sy as i64 + 1);
            let wx = m[0] * dx + m[3] * f + m[6] * dz;
            let wy = m[1] * dx + m[4] * f + m[7] * dz;
            let wz = m[2] * dx + m[5] * f + m[8] * dz;
            let (ax, ay, az) = (wx.abs(), wy.abs(), wz.abs());
            let (face, dom, u1, v1) = if ax >= ay && ax >= az {
                ((wx < 0) as i64, ax, wy, wz)
            } else if ay >= az {
                (2 + ((wy < 0) as i64), ay, wx, wz)
            } else {
                (4 + ((wz < 0) as i64), az, wx, wy)
            };
            let dom = dom.max(1);
            let hh = star_hash(face, u1 * 128 / dom, v1 * 128 / dom);
            if hh % 43 == 0 {
                let color = if hh & 0x400 != 0 { 0x00E8E8F2 } else { 0x00A8A8C0 };
                for oy in 0..2i32 {
                    for ox in 0..2i32 {
                        let (px, py) = (sx + ox, sy + oy);
                        if px < w && py < h {
                            let p = (py * w + px) as usize;
                            if zbuf[p] == i32::MAX { buf[p] = color }
                        }
                    }
                }
            }
            sx += 2;
        }
        sy += 2;
    }
}

// ---- v1.13: the wanderer (fppose + fpclip PROMOTED into the demo) -----------------------------
// The dormancy rule said fppose/fpclip promote when a walk exposes their falsifier; a
// third-person camera IS that walk — an avatar on screen exercises the posed hierarchy, the
// clip sampler and the state machine every frame. The kernels below are lifted VERBATIM from
// the certified placements (fppose_rs, fpclip_rs — the one edit is the same one heightfield
// took: they call THIS demo's Fx, whose kernel ops are fpquat's placement bytes), and the
// demo runs BOTH placement batteries at every launch against the same goldens the gate pins:
// the posed-biped digest and coverage certificate (URDRPSE1) and the walk-pose + 96-tick
// state-machine trace (URDRCLP1). A launch that fails either refuses to run third-person.
// The avatar's SCREEN form is a capsule impostor — the certificate certifies joints and
// capsules; the impostor is DECLARED presentation, z-buffered like world geometry.
const PSE_PARENT: [i32; 5] = [-1, 0, 1, 1, 1];
const PSE_NAMES: [&str; 5] = ["root", "spine", "head", "arm_l", "arm_r"];
const PSE_OFFX: [i64; 5] = [0, 0, 0, -14, 14];
const PSE_OFFY: [i64; 5] = [0, 0, 0, 0, 0];
const PSE_OFFZ: [i64; 5] = [0, 24, 20, 16, 16];
const PSE_WALK: [Q4; 5] = [
    Q4 { w: 4294734297, x: 0, y: 44736816, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4291243873, x: -178801828, y: 0, z: 0 },
    Q4 { w: 4291243873, x: 178801828, y: 0, z: 0 },
];
const PSE_REACH: [Q4; 5] = [
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 4294967296 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
    Q4 { w: 4294967296, x: 0, y: 0, z: 0 },
];
const PSE_GOLDEN: &str = "fee3c118e2788ef72eb200ef2f6d4da691246324fec8e8018e29b69ff3101959";
const CLP_G_POSE: &str = "73b763f88474cb0a3f02fee3e4e3624c42d7ab4ee62b3d6ae52f2fd59b5c4886";
const CLP_G_TRACE: &str = "823a7746c286213065c5dd50b2765cb5f66680872cd376fca26e305d9c764fd3";
const CLP_TICKS: usize = 96;
const CLP_HZ: i64 = 240;

fn pse_radius(i: usize) -> i64 { [0, 12 * ONE, 8 * ONE, 6 * ONE, 6 * ONE][i] }
fn pse_off(i: usize) -> V3 { V3 { x: PSE_OFFX[i] * ONE, y: PSE_OFFY[i] * ONE, z: PSE_OFFZ[i] * ONE } }

fn pose_world(fx: &mut Fx, pose: &[Q4; 5], swapped: bool) -> ([Q4; 5], [V3; 5]) {
    let mut wq = [Q4 { w: 0, x: 0, y: 0, z: 0 }; 5];
    let mut wp = [V3 { x: 0, y: 0, z: 0 }; 5];
    for i in 0..5 {
        if i == 0 {
            wq[0] = fx.qnormalize(pose[0]);
            wp[0] = pse_off(0);
        } else {
            let p = PSE_PARENT[i] as usize;
            let comp = if swapped { fx.qmul(pose[i], wq[p]) } else { fx.qmul(wq[p], pose[i]) };
            wq[i] = fx.qnormalize(comp);
            let moved = fx.vrotate(wq[p], pse_off(i));
            wp[i] = V3 {
                x: fx.fin(wp[p].x + moved.x),
                y: fx.fin(wp[p].y + moved.y),
                z: fx.fin(wp[p].z + moved.z),
            };
        }
    }
    (wq, wp)
}

struct U256 { hi: u128, lo: u128 }
fn mul128(a: u128, b: u128) -> U256 {
    let (a_hi, a_lo) = (a >> 64, a & 0xFFFF_FFFF_FFFF_FFFF);
    let (b_hi, b_lo) = (b >> 64, b & 0xFFFF_FFFF_FFFF_FFFF);
    let ll = a_lo * b_lo;
    let lh = a_lo * b_hi;
    let hl = a_hi * b_lo;
    let hh = a_hi * b_hi;
    let mid = (ll >> 64) + (lh & 0xFFFF_FFFF_FFFF_FFFF) + (hl & 0xFFFF_FFFF_FFFF_FFFF);
    U256 { hi: hh + (lh >> 64) + (hl >> 64) + (mid >> 64),
           lo: (mid << 64) | (ll & 0xFFFF_FFFF_FFFF_FFFF) }
}
fn add256(a: U256, b: U256) -> U256 {
    let (lo, carry) = a.lo.overflowing_add(b.lo);
    U256 { hi: a.hi + b.hi + (carry as u128), lo }
}
fn le256(a: U256, b: U256) -> bool { a.hi < b.hi || (a.hi == b.hi && a.lo <= b.lo) }

fn in_capsule(pt: V3, a: V3, b: V3, r: i64) -> bool {
    let dx = b.x as i128 - a.x as i128;
    let dy = b.y as i128 - a.y as i128;
    let dz = b.z as i128 - a.z as i128;
    let apx = pt.x as i128 - a.x as i128;
    let apy = pt.y as i128 - a.y as i128;
    let apz = pt.z as i128 - a.z as i128;
    let dd = dx * dx + dy * dy + dz * dz;
    let rr = (r as i128) * (r as i128);
    if dd == 0 {
        return apx * apx + apy * apy + apz * apz <= rr;
    }
    let tn = apx * dx + apy * dy + apz * dz;
    if tn <= 0 {
        return apx * apx + apy * apy + apz * apz <= rr;
    }
    if tn >= dd {
        let bpx = pt.x as i128 - b.x as i128;
        let bpy = pt.y as i128 - b.y as i128;
        let bpz = pt.z as i128 - b.z as i128;
        return bpx * bpx + bpy * bpy + bpz * bpz <= rr;
    }
    let ap2 = apx * apx + apy * apy + apz * apz;
    let a256 = mul128(ap2 as u128, dd as u128);
    let b256 = mul128(tn as u128, tn as u128);
    let c256 = mul128(rr as u128, dd as u128);
    le256(a256, add256(b256, c256))
}
fn pse_covers(joints: &[V3; 5], ca: &[V3; 5], cb: &[V3; 5]) -> bool {
    for j in 0..5 {
        let mut inside = false;
        for i in 1..5 {
            if in_capsule(joints[j], ca[i], cb[i], pse_radius(i)) { inside = true; break; }
        }
        if !inside { return false }
    }
    true
}
fn pse_caps(wp: &[V3; 5]) -> ([V3; 5], [V3; 5]) {
    let mut ca = [V3 { x: 0, y: 0, z: 0 }; 5];
    let mut cb = [V3 { x: 0, y: 0, z: 0 }; 5];
    for i in 1..5 { ca[i] = wp[PSE_PARENT[i] as usize]; cb[i] = wp[i]; }
    (ca, cb)
}

fn posed_digest(fx: &mut Fx, pose: &[Q4; 5], swapped: bool) -> String {
    let (wq, wp) = pose_world(fx, pose, swapped);
    let mut sh = Sha256::new();
    sh.update(b"URDRPSE1");
    for i in 0..5 {
        for &c in &[wq[i].w, wq[i].x, wq[i].y, wq[i].z] { sh.update(&c.to_be_bytes()); }
    }
    for i in 0..5 {
        for &c in &[wp[i].x, wp[i].y, wp[i].z] { sh.update(&c.to_be_bytes()); }
    }
    for i in 1..5 {
        sh.update(PSE_NAMES[i].as_bytes());
        let a = wp[PSE_PARENT[i] as usize];
        let b = wp[i];
        for &c in &[a.x, a.y, a.z, b.x, b.y, b.z] { sh.update(&c.to_be_bytes()); }
        sh.update(&pse_radius(i).to_be_bytes());
    }
    hex(&sh.finish())
}

#[derive(Clone, Copy)]
struct Track { n: usize, t: [i64; 5], q: [Q4; 5] }
#[derive(Clone, Copy)]
struct Clip { tr: [Track; 5], looped: bool }

fn rotq(x: i64, y: i64, z: i64) -> Q4 { Q4 { w: ONE, x, y, z } }

fn demo_idle() -> Clip {
    let h2 = ONE / 2;
    let e64 = ONE / 64;
    let zero = rotq(0, 0, 0);
    let still = Track { n: 3, t: [0, h2, ONE, 0, 0], q: [zero, zero, zero, zero, zero] };
    let mut sway = still;
    sway.q[1] = rotq(e64, 0, 0);
    Clip { tr: [still, sway, sway, still, still], looped: true }
}
fn demo_walk() -> Clip {
    let qt = ONE / 4;
    let h2 = ONE / 2;
    let e8 = ONE / 8;
    let e64 = ONE / 64;
    let zero = rotq(0, 0, 0);
    let t5 = [0, qt, h2, 3 * qt, ONE];
    let still = Track { n: 5, t: t5, q: [zero; 5] };
    let mut swing_l = still;
    swing_l.q[0] = rotq(e8, 0, 0); swing_l.q[2] = rotq(-e8, 0, 0); swing_l.q[4] = rotq(e8, 0, 0);
    let mut swing_r = still;
    swing_r.q[0] = rotq(-e8, 0, 0); swing_r.q[2] = rotq(e8, 0, 0); swing_r.q[4] = rotq(-e8, 0, 0);
    let mut bob = still;
    bob.q[1] = rotq(0, e64, 0); bob.q[3] = rotq(0, -e64, 0);
    Clip { tr: [bob, still, still, swing_l, swing_r], looped: true }
}

fn sample_track(fx: &mut Fx, tr: &Track, t: i64, looped: bool) -> Q4 {
    let t0 = tr.t[0];
    let tk = tr.t[tr.n - 1];
    if t < t0 { fx.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
    let lt = if looped {
        t0 + ((t - t0) % (tk - t0))
    } else {
        if t > tk { fx.refused = true; return Q4 { w: 0, x: 0, y: 0, z: 0 }; }
        t
    };
    let (mut lo, mut hi) = (0usize, tr.n);
    while lo < hi {
        let mid = (lo + hi) / 2;
        if tr.t[mid] <= lt { lo = mid + 1; } else { hi = mid; }
    }
    let mut i = lo - 1;
    if i >= tr.n - 1 { i = tr.n - 2; }
    let u = fx.rdiv((lt - tr.t[i]) as i128 * ONE as i128, (tr.t[i + 1] - tr.t[i]) as i128);
    fx.qnlerp(tr.q[i], tr.q[i + 1], u)
}
fn sample_pose(fx: &mut Fx, c: &Clip, t: i64) -> [Q4; 5] {
    let mut out = [Q4 { w: 0, x: 0, y: 0, z: 0 }; 5];
    for b in 0..5 { out[b] = sample_track(fx, &c.tr[b], t, c.looped); }
    out
}

// states: 0=idle 1=walk ; events: 0=go 1=sprint 2=stop — the CANONICAL minimum-priority
// resolution, lifted with its rule table (the authored-order defect is the placement's plant)
const CLP_RULES: [(usize, usize, usize, i64); 4] =
    [(1, 0, 1, 5), (1, 1, 1, 2), (0, 1, 0, 0), (1, 0, 2, 0)];
const CLP_STATE_NAME: [&str; 2] = ["idle", "walk"];
const CLP_SCRIPT: [(usize, usize); 3] = [(24, 0), (48, 1), (72, 2)];

fn step_canonical(state: usize, ev: usize) -> (usize, bool) {
    let mut best: Option<(usize, i64)> = None;
    for &(f, to, e, pr) in CLP_RULES.iter() {
        if f == state && e == ev {
            if best.map_or(true, |(_, bp)| pr < bp) { best = Some((to, pr)); }
        }
    }
    match best { Some((to, _)) => (to, true), None => (state, false) }
}

fn clip_trace_digest(fx: &mut Fx) -> String {
    let clips = [demo_idle(), demo_walk()];
    let mut sh = Sha256::new();
    sh.update(b"URDRCLP1");
    let (mut state, mut start, mut si) = (0usize, 0usize, 0usize);
    for i in 0..CLP_TICKS {
        if si < 3 && CLP_SCRIPT[si].0 == i {
            let (ns, moved) = step_canonical(state, CLP_SCRIPT[si].1);
            if moved { state = ns; start = i; }
            si += 1;
        }
        let lt = fx.rdiv(i as i128 * ONE as i128, CLP_HZ as i128)
               - fx.rdiv(start as i128 * ONE as i128, CLP_HZ as i128);
        let pose = sample_pose(fx, &clips[state], lt);
        sh.update(&(i as u64).to_be_bytes());
        sh.update(CLP_STATE_NAME[state].as_bytes());
        for q in pose.iter() {
            sh.update(&q.w.to_be_bytes());
            sh.update(&q.x.to_be_bytes());
            sh.update(&q.y.to_be_bytes());
            sh.update(&q.z.to_be_bytes());
        }
    }
    hex(&sh.finish())
}

fn pse_battery(fx: &mut Fx) -> bool {
    let d = posed_digest(fx, &PSE_WALK, false);
    let (_, wp) = pose_world(fx, &PSE_WALK, false);
    let (ca, cb) = pse_caps(&wp);
    let (_, wpr) = pose_world(fx, &PSE_REACH, false);
    let (ra, rb) = pse_caps(&wpr);
    let swapped = posed_digest(fx, &PSE_WALK, true);
    d == PSE_GOLDEN && pse_covers(&wp, &ca, &cb) && pse_covers(&wpr, &ra, &rb)
        && swapped != PSE_GOLDEN && !fx.refused
}
fn clp_battery(fx: &mut Fx) -> bool {
    let u = fx.rdiv(ONE as i128, 3);
    let pose = sample_pose(fx, &demo_walk(), u);
    let mut sh = Sha256::new();
    sh.update(b"URDRCLP1");
    for q in pose.iter() {
        sh.update(&q.w.to_be_bytes());
        sh.update(&q.x.to_be_bytes());
        sh.update(&q.y.to_be_bytes());
        sh.update(&q.z.to_be_bytes());
    }
    hex(&sh.finish()) == CLP_G_POSE && clip_trace_digest(fx) == CLP_G_TRACE && !fx.refused
}

// ---- the avatar on screen: ground-clamped, facing the camera's horizontal forward -------------
// Joint positions come out of the CERTIFIED pose path in Q32.32 skeleton units (a 44-unit
// biped); >>28 maps them to Q8 world units at 1/16 scale — a 2.75-unit wanderer against a
// 3-unit eye. The facing basis derives from the camera matrix's forward column, normalized
// with the exact integer isqrt; the ground clamp is the same bilinear the eye stands on. The
// one-tick-late IK contract is NOT claimed here — feet ride the bilinear ground, stated.
fn avatar_joints(fx: &mut Fx, lod: &mut LodWorld, cam: &Cam, m: &[i64; 9],
                 clip_state: usize, t_q32: i64) -> ([V3; 5], i64) {
    let clips = [demo_idle(), demo_walk()];
    let pose = sample_pose(fx, &clips[clip_state], t_q32);
    let (_, wp) = pose_world(fx, &pose, false);
    // facing: the camera's horizontal forward (m[3], m[4]) normalized to Q16
    let (fwx, fwy) = (m[3], m[4]);
    let n2 = fwx * fwx + fwy * fwy;
    let (f16x, f16y) = if n2 == 0 { (0, 1 << 16) } else {
        let n = isqrt64(n2).max(1);
        (fwx * 65536 / n, fwy * 65536 / n)
    };
    let (r16x, r16y) = (f16y, -f16x);              // right = forward rotated -90 about Z
    // ground under the anchor, bilinear, Q8 (the eye's own law)
    let ctx = floordiv(cam.px >> 8, TILE);
    let cty = floordiv(cam.py >> 8, TILE);
    let (rx8, ry8) = (cam.px - ((ctx * TILE) << 8), cam.py - ((cty * TILE) << 8));
    let (u, v) = (rx8 / TILE, ry8 / TILE);
    let (h00, h10) = (lod.h(ctx, cty, 1) << 8, lod.h(ctx + 1, cty, 1) << 8);
    let (h01, h11) = (lod.h(ctx, cty + 1, 1) << 8, lod.h(ctx + 1, cty + 1, 1) << 8);
    let hx0 = h00 + (h10 - h00) * u / 256;
    let hx1 = h01 + (h11 - h01) * u / 256;
    let ground8 = hx0 + (hx1 - hx0) * v / 256;
    let mut out = [V3 { x: 0, y: 0, z: 0 }; 5];
    for i in 0..5 {
        let (lx, ly, lz) = (wp[i].x >> 28, wp[i].y >> 28, wp[i].z >> 28);   // Q8, 1/16 scale
        out[i] = V3 {
            x: cam.px + ((r16x * lx + f16x * ly) >> 16),
            y: cam.py + ((r16y * lx + f16y * ly) >> 16),
            z: ground8 + lz,
        };
    }
    (out, ground8)
}

const AV_COLORS: [u32; 5] = [0, 0x00A03028, 0x00D9B48A, 0x00703830, 0x00703830];

fn draw_avatar(buf: &mut [u32], zbuf: &mut [i32], w: i32, h: i32, m: &[i64; 9],
               eye: (i64, i64, i64), joints: &[V3; 5]) {
    let f = h as i64 * 2;
    let (cx, cy) = (w as i64 / 2, h as i64 / 2);
    for i in 1..5 {
        let a = joints[PSE_PARENT[i] as usize];
        let b = joints[i];
        let r8 = pse_radius(i) >> 28;              // Q8 world radius at the same 1/16 scale
        let mut sp = [(0i64, 0i64, 0i64); 2];
        let mut behind = 0;
        for (k, j) in [a, b].iter().enumerate() {
            let (dx, dy, dz) = (j.x - eye.0, j.y - eye.1, j.z - eye.2);
            let rx = (m[0] * dx + m[1] * dy + m[2] * dz) >> 16;
            let ry = (m[3] * dx + m[4] * dy + m[5] * dz) >> 16;
            let rz = (m[6] * dx + m[7] * dy + m[8] * dz) >> 16;
            let d8 = ry.max(NEAR8);
            if ry < NEAR8 { behind += 1 }
            sp[k] = (cx + rx * f / d8, cy - rz * f / d8, d8);
        }
        if behind == 2 { continue }
        let rpx = (r8 * f / sp[0].2.min(sp[1].2)).max(1);
        let x_lo = (sp[0].0.min(sp[1].0) - rpx).max(0);
        let x_hi = (sp[0].0.max(sp[1].0) + rpx).min(w as i64 - 1);
        let y_lo = (sp[0].1.min(sp[1].1) - rpx).max(0);
        let y_hi = (sp[0].1.max(sp[1].1) + rpx).min(h as i64 - 1);
        if x_lo > x_hi || y_lo > y_hi { continue }
        let (sx, sy) = (sp[1].0 - sp[0].0, sp[1].1 - sp[0].1);
        let l2 = sx * sx + sy * sy;
        let rr = rpx * rpx;
        for py in y_lo..=y_hi {
            let row = (py * w as i64) as usize;
            for px in x_lo..=x_hi {
                let (vx, vy) = (px - sp[0].0, py - sp[0].1);
                let tn = if l2 == 0 { 0 } else { (vx * sx + vy * sy).clamp(0, l2) };
                let (qx, qy) = if l2 == 0 { (0, 0) } else { (sx * tn / l2, sy * tn / l2) };
                let (ex, ey) = (vx - qx, vy - qy);
                if ex * ex + ey * ey <= rr {
                    let d = if l2 == 0 { sp[0].2 } else { sp[0].2 + (sp[1].2 - sp[0].2) * tn / l2 };
                    let p = row + px as usize;
                    let di = d.clamp(0, i32::MAX as i64) as i32;
                    if di < zbuf[p] { zbuf[p] = di; buf[p] = AV_COLORS[i]; }
                }
            }
        }
    }
}

// ---- v1.14: the castle (worldgeom's record, drawn) --------------------------------------------
// A committed geometry record produced by tools/terrain/worldgeom.py from an authored .wrk —
// authored as WHAT ITS PARTS ARE (walls, towers, blocks with spans, heights, crenels), never as
// vertices, and generated onto the same certified ground this renderer draws. The record is
// runtime-frame Q8 convex plan prisms; this reads them and rasters top faces and side quads
// through the SAME projection, edge functions and z-buffer the terrain uses, so a castle
// occupies pixels by winning depth like everything else. --castle is OFF by default and every
// committed chain stands untouched.
struct Prism { poly: Vec<(i64, i64)>, zb: i64, zt: i64, color: u32 }

fn load_castle(path: &str) -> Result<Vec<Prism>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("--castle: {e}"))?;
    let mut out = Vec::new();
    for ln in text.lines() {
        if ln.starts_with('#') || ln.trim().is_empty() { continue }
        let p: Vec<&str> = ln.split_whitespace().collect();
        if p.len() < 6 || p[0] != "prism" { return Err("castle record line malformed".into()) }
        let color = u32::from_str_radix(p[2], 16).map_err(|_| "castle: colour")?;
        let zb: i64 = p[3].parse().map_err(|_| "castle: zb")?;
        let zt: i64 = p[4].parse().map_err(|_| "castle: zt")?;
        let n: usize = p[5].parse().map_err(|_| "castle: n")?;
        if p.len() != 6 + 2 * n { return Err("castle: vertex count disagrees".into()) }
        let mut poly = Vec::with_capacity(n);
        for i in 0..n {
            poly.push((p[6 + 2 * i].parse().map_err(|_| "castle: x")?,
                       p[7 + 2 * i].parse().map_err(|_| "castle: y")?));
        }
        out.push(Prism { poly, zb, zt, color });
    }
    if out.is_empty() { return Err("castle record has no prisms".into()) }
    Ok(out)
}

fn draw_castle(buf: &mut [u32], zbuf: &mut [i32], w: i32, h: i32, m: &[i64; 9],
               eye: (i64, i64, i64), prisms: &[Prism], farq: i64) {
    let f = h as i64 * 2;
    let (cx, cy) = (w as i64 / 2, h as i64 / 2);
    // v1.17: the castle rides the SAME near-plane rule as the terrain. v1.14 marked a vertex
    // behind the plane with a sentinel depth and dropped the whole triangle, which is the
    // discard the ring renderer just stopped doing — so a wall could vanish at arm's length
    // exactly where the ground used to. Camera space out, clipped in `tri`, projected after.
    let project = |p: (i64, i64, i64)| -> CamV {
        let (dx, dy, dz) = (p.0 - eye.0, p.1 - eye.1, p.2 - eye.2);
        let rx = (m[0] * dx + m[1] * dy + m[2] * dz) >> 16;
        let ry = (m[3] * dx + m[4] * dy + m[5] * dz) >> 16;
        let rz = (m[6] * dx + m[7] * dy + m[8] * dz) >> 16;
        (rx, ry, rz)
    };
    let tri = |buf: &mut [u32], zbuf: &mut [i32],
                   a: CamV, b: CamV, c: CamV, col: u32| {
        let (fan, fann) = clip_near(&[a, b, c]);
        if fann < 3 { return }
        let pj = |v: CamV| (cx + v.0 * f / v.1, cy - v.2 * f / v.1, v.1);
        for k in 1..fann - 1 {
            let (a, b, c) = (pj(fan[0]), pj(fan[k]), pj(fan[k + 1]));
            let (mut b, mut c) = (b, c);
            let mut area = (b.0 - a.0) * (c.1 - a.1) - (b.1 - a.1) * (c.0 - a.0);
            if area == 0 { continue }
            if area < 0 { std::mem::swap(&mut b, &mut c); area = -area }
            let x_lo = a.0.min(b.0).min(c.0).max(0);
            let x_hi = a.0.max(b.0).max(c.0).min(w as i64 - 1);
            let y_lo = a.1.min(b.1).min(c.1).max(0);
            let y_hi = a.1.max(b.1).max(c.1).min(h as i64 - 1);
            if x_lo > x_hi || y_lo > y_hi { continue }
            let d3 = ((a.2 + b.2 + c.2) / 3).clamp(0, farq);
            // the same depth fog the terrain wears, so distance reads the same on both
            let dim = 14 + 18 * (farq - d3) / farq;
            let ch3 = |near: i64, sky: i64| ((near * dim + sky * (32 - dim)) / 32) as u32;
            let (tr, tg, tb) = (((col >> 16) & 255) as i64, ((col >> 8) & 255) as i64,
                                (col & 255) as i64);
            let cc = (ch3(tr, 60) << 16) | (ch3(tg, 120) << 8) | ch3(tb, 190);
            for py in y_lo..=y_hi {
                let row = (py * w as i64) as usize;
                for px in x_lo..=x_hi {
                    let w0 = (b.0 - a.0) * (py - a.1) - (b.1 - a.1) * (px - a.0);
                    let w1 = (c.0 - b.0) * (py - b.1) - (c.1 - b.1) * (px - b.0);
                    let w2 = (a.0 - c.0) * (py - c.1) - (a.1 - c.1) * (px - c.0);
                    if w0 < 0 || w1 < 0 || w2 < 0 { continue }
                    let d = (a.2 * w1 + b.2 * w2 + c.2 * w0) / area;
                    let di = d.clamp(0, i32::MAX as i64) as i32;
                    let i = row + px as usize;
                    if di < zbuf[i] { zbuf[i] = di; buf[i] = cc }
                }
            }
        }
    };
    for pr in prisms.iter() {
        let n = pr.poly.len();
        // sides
        for i in 0..n {
            let (ax, ay) = pr.poly[i];
            let (bx, by) = pr.poly[(i + 1) % n];
            let p0 = project((ax, ay, pr.zb));
            let p1 = project((bx, by, pr.zb));
            let p2 = project((bx, by, pr.zt));
            let p3 = project((ax, ay, pr.zt));
            tri(buf, zbuf, p0, p1, p2, pr.color);
            tri(buf, zbuf, p0, p2, p3, pr.color);
        }
        // top face, fanned from vertex 0 (convex by the generator's own refusal)
        let t0 = project((pr.poly[0].0, pr.poly[0].1, pr.zt));
        for i in 1..n - 1 {
            let t1 = project((pr.poly[i].0, pr.poly[i].1, pr.zt));
            let t2 = project((pr.poly[i + 1].0, pr.poly[i + 1].1, pr.zt));
            tri(buf, zbuf, t0, t1, t2, pr.color);
        }
    }
}

// ---- the entry door ---------------------------------------------------------------------------
struct Args {
    host: String, power: String, scheduler: String, hz: i64, frames: u32,
    res: (i32, i32), play: bool, replay: String, defect: bool, selfcheck_only: bool, sky: bool,
    third: bool, await_focus: bool, castle: String,
    trace_out: String, out: String, reach: i64, cache_cap: usize,
}

fn parse_argv() -> Result<Args, String> {
    let mut a = Args { host: "-".into(), power: "-".into(), scheduler: "-".into(), hz: 120,
                       frames: 1800, res: (1280, 720), play: false, replay: String::new(),
                       defect: false, selfcheck_only: false, sky: false, third: false,
                       await_focus: false, castle: String::new(),
                       trace_out: "fpsdemo_trace.txt".into(),
                       out: "fpsdemo_log.txt".into(), reach: 60, cache_cap: usize::MAX };
                       // reach 60: THE COMPETITIVE FREEZE (measured ceiling-clean at 120 Hz);
                       // cache_cap MAX is the sentinel for "derive the rail from the ladder"
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
            "--sky" => a.sky = true,
            "--third" => a.third = true,
            "--await-focus" => a.await_focus = true,
            "--castle" => a.castle = value(&mut i)?,
            "--reach" => {
                a.reach = value(&mut i)?.parse().map_err(|_| "--reach: not an integer")?;
                if !(8..=200_000).contains(&a.reach) {
                    return Err(format!("--reach {} outside 8..=200000 tiles — this door \
refuses a reach it cannot derive a ladder for", a.reach));
                }
            }
            "--cache-cap" => {
                a.cache_cap = value(&mut i)?.parse().map_err(|_| "--cache-cap: not an integer")?;
            }
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

// v1.15 — THE TRACE DECLARES ITS OWN LENGTH, AND THE TWO IDENTITIES ARE SEPARATE.
//
// THE NEUTRAL RULER. Until now `expected` was the number of rows the file happened to contain,
// so `consumed == expected` established only that the program consumed everything a DAMAGED
// trace held. A partial write or an interrupted copy shrank the ruler to match the workload and
// the run reported complete. The ruler may not be derived from the thing it measures, so the
// recorder writes `# frames N` and the loader takes `expected` from that declaration. The
// loader already skipped `#` lines, so every trace written before this version still loads —
// as LEGACY, carrying no declaration, which is a fact the record then states rather than hides.
//
// TWO DIGESTS, TWO MEANINGS, AND THE SPLIT IS `worldbind`'s (S19). `bytes` is PROVENANCE: which
// artifact was this. `workload` is IDENTITY: which motion is this — taken over the canonical
// rows, so comments, blank lines, whitespace and platform line endings cannot move it. An A/B
// compares WORKLOAD, because a line-ending change is not a different walk; `bytes` stays because
// a pair that agrees on the walk and disagrees on the file is a different situation from one
// that agrees on both, and a reader who cannot tell them apart is reading a weaker record.
//
// AND THE SEMANTIC DIGEST COMES FROM THE SAME PARSE THAT FEEDS THE REPLAY. A second parse would
// be a second interpretation of the trace, and the digest would then identify the workload some
// other reader saw rather than the one this program loaded.
struct TraceIn {
    rows: Vec<(u32, i64, i64)>,
    declared: Option<usize>,
    bytes_hex: String,
    workload_hex: String,
}

fn load_trace(path: &str) -> Result<TraceIn, String> {
    let raw = std::fs::read(path).map_err(|e| format!("trace {path}: {e}"))?;
    let bytes_hex = sha256_hex(&raw);
    let text = String::from_utf8(raw).map_err(|_| format!("trace {path}: not UTF-8"))?;
    let mut rows = Vec::new();
    let mut declared: Option<usize> = None;
    for (ln_no, ln) in text.lines().enumerate() {
        let s = ln.trim();
        if s.is_empty() { continue }
        if let Some(rest) = s.strip_prefix("# frames ") {
            if declared.is_some() {
                return Err(format!("trace {path}: two `# frames` declarations"))
            }
            declared = Some(rest.trim().parse()
                .map_err(|_| format!("trace {path}: `# frames` wants an integer"))?);
            continue
        }
        if s.starts_with('#') { continue }
        let p: Vec<&str> = s.split_whitespace().collect();
        if p.len() != 3 { return Err(format!("trace line {}: wants `keys dx dy`", ln_no + 1)) }
        rows.push((p[0].parse().map_err(|_| "keys")?,
                   p[1].parse().map_err(|_| "dx")?,
                   p[2].parse().map_err(|_| "dy")?));
    }
    if rows.is_empty() { return Err("trace is empty — nothing to replay".into()) }
    if let Some(n) = declared {
        if n != rows.len() {
            // A FORMAT FAILURE, NEVER A SHORT REPLAY. A trace that disagrees with itself cannot
            // be measured against, so it refuses here rather than producing a record that would
            // have to be adjudicated later.
            return Err(format!("trace {path}: declares {n} frames and carries {} — a declared \
                                length that disagrees with its rows is a FORMAT failure",
                               rows.len()))
        }
    }
    let mut canon = String::new();
    for (k, dx, dy) in &rows { canon.push_str(&format!("{} {} {}\n", k, dx, dy)); }
    let workload_hex = sha256_hex(canon.as_bytes());
    Ok(TraceIn { rows, declared, bytes_hex, workload_hex })
}

fn main() {
    let args = match parse_argv() {
        Ok(a) => a,
        Err(e) => { eprintln!("FPSDEMO-REFUSE: {e}"); std::process::exit(2) }
    };
    if !projection_bound_ok(args.reach, args.res.0, args.res.1) {
        eprintln!("FPSDEMO-REFUSE: --reach {} at {}x{} exceeds the projection bound — with the \
                   near plane at {}/256 world units the edge-function and depth terms would pass \
                   the i64 ceiling, and this door refuses rather than trusting the arithmetic to \
                   fail visibly. Maximum admissible reach at this resolution is {}",
                  args.reach, args.res.0, args.res.1, NEAR8,
                  max_admissible_reach(args.res.0, args.res.1));
        std::process::exit(2);
    }
    if args.third && args.reach <= LOD_R0 {
        eprintln!("FPSDEMO-REFUSE: --third needs the ladder path (reach > {LOD_R0}) — the \
                   wanderer stands on the derived rings, not the compat window");
        std::process::exit(2);
    }
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
    let trace_in = if args.replay.is_empty() {
                       TraceIn { rows: Vec::new(), declared: None,
                                 bytes_hex: String::new(), workload_hex: String::new() } }
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
    let total_frames = if args.play { args.frames } else { trace_in.rows.len() as u32 };

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
    let pump = |_x: i32| unsafe {
        let mut m = MSG { hwnd: 0, message: 0, wParam: 0, lParam: 0, time: 0,
                          pt: POINT { x: 0, y: 0 } };
        while PeekMessageW(&mut m, 0, 0, 0, PM_REMOVE) != 0 {
            TranslateMessage(&m); DispatchMessageW(&m);
        }
    };
    pump(0);
    let mut focus_foreground = unsafe { GetForegroundWindow() == hwnd };
    // v1.13.3: AN INSTRUMENT MAY WAIT FOR ITS DECLARED CONDITIONS — BUT NEVER DEPEND ON
    // THEM. `--await-focus` holds the run at the door until the operator clicks the window,
    // which is what a cost record wants: measuring a background window measures a different
    // operation. The wait is BOUNDED (30 s) and REPORTED (`focus_wait_ms`), and expiry
    // PROCEEDS rather than hanging — because the named host is a handheld whose vendor layer
    // can keep foreground for itself (L83's whole subject), and an instrument that could
    // block forever on a condition it does not need is the dependency L83 retired, wearing a
    // patience costume. The counter (L85) still reports what actually held per frame; this
    // only improves the odds that it reads 1145/1145.
    let mut focus_wait_ms: i64 = 0;
    if args.await_focus && !focus_foreground {
        eprintln!("await-focus: CLICK THE DEMO WINDOW to begin — waiting up to 30 s (the run \
                   starts regardless when the bound expires; a wait is a courtesy, never a \
                   dependency)");
        let t0 = qpc();
        loop {
            pump(0);
            focus_foreground = unsafe { GetForegroundWindow() == hwnd };
            focus_wait_ms = ticks_to_ns(qpc() - t0, freq) / 1_000_000;
            if focus_foreground || focus_wait_ms >= 30_000 { break }
            unsafe { Sleep(20) };
        }
        eprintln!("await-focus: {} after {} ms", if focus_foreground { "GRANTED" }
                  else { "NOT GRANTED — proceeding, conditions reported as measured" },
                  focus_wait_ms);
    }
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
    // v1.7: THE REACH LADDER, derived (one variable). reach <= LOD_R0 keeps the v1.6 path
    // untouched — the pinned chains are the identity contract. PREFILL RUNS BEFORE THE TIMER:
    // the cache cold-fill is a START CONDITION, printed as a count, never mixed into frame
    // stats (a 0.6-2.8 s fill inside frame 0 would contaminate the measurement, not describe
    // it). The elapsed fill time goes to stderr — wall-clock stays out of the log body.
    let ladder = if args.reach > LOD_R0 { lod_schedule(args.reach, ch as i64 * 2) }
                 else { Vec::new() };
    // v1.11: resolve the cache policy — sentinel derives the rail, 0 stays unbounded,
    // an explicit N is honored. The derivation runs BEFORE prefill so the door is up
    // for every insertion the run ever makes.
    let cache_cap = if args.cache_cap == usize::MAX {
        if ladder.is_empty() { 0 } else { derived_cap(&ladder) }
    } else { args.cache_cap };
    let cache_policy = if args.cache_cap == usize::MAX {
        if ladder.is_empty() { "compat-path" } else { "derived-rail-2x-footprint" }
    } else if args.cache_cap == 0 { "unbounded-explicit" } else { "explicit" };
    let mut lodw = LodWorld::new(&ladder, cache_cap);
    // v1.13.1: PREFILL AT THE RENDER EYE, NOT THE AVATAR. The named host's first v1.13 run
    // caught the leak: with --third the prefill warmed the cache at the avatar's spawn tile
    // while frame 0 rastered from the boom eye twelve units back, so the first frame paid
    // ring rebases the prefill convention exists to keep OUT of frame stats (one 8.9 ms
    // startup frame, the run's only late frame). The start condition now anchors where the
    // first frame actually looks from. Values never move — the prefill only warms the cache
    // — so every chain stands; only the start condition's honesty changed.
    let prefill_tiles: u64 = if !ladder.is_empty() {
        let (pfx, pfy) = if args.third {
            let qc0 = qconj(cam.q);
            let by0 = fx_cam.vrotate(qc0, V3 { x: 0, y: ONE, z: 0 });
            let (fwx, fwy) = (by0.x >> 16, by0.y >> 16);
            let n2 = fwx * fwx + fwy * fwy;
            let (f16x, f16y) = if n2 == 0 { (0, 1 << 16) } else {
                let n = isqrt64(n2).max(1);
                (fwx * 65536 / n, fwy * 65536 / n)
            };
            (cam.px - (f16x * AV_BOOM8 >> 16), cam.py - (f16y * AV_BOOM8 >> 16))
        } else { (cam.px, cam.py) };
        let t0 = qpc();
        let n = lodw.prefill(floordiv(pfx >> 8, TILE), floordiv(pfy >> 8, TILE), &ladder);
        eprintln!("prefill: {} tiles in {} ms (start condition, outside frame stats)",
                  n, ticks_to_ns(qpc() - t0, freq) / 1_000_000);
        n
    } else { 0 };
    let mut deadline = qpc() + ticks_per_frame;

    // v1.13: the wanderer's state — the canonical stepper's state, its entry frame, and the
    // per-frame camera-matrix shadow the avatar and boom share.
    let mut av_state: usize = 0;
    let mut av_start: u32 = 0;
    let mut av_m: [i64; 9] = [0; 9];
    let castle: Vec<Prism> = if args.castle.is_empty() { Vec::new() } else {
        match load_castle(&args.castle) {
            Ok(p) => { eprintln!("castle: {} prisms from {}", p.len(), args.castle); p }
            Err(e) => { eprintln!("FPSDEMO-REFUSE: {e}"); std::process::exit(2) }
        }
    };
    let mut focus_frames: u32 = 0;                 // v1.13.2: focus as a COUNT, not a guess
    const AV_BOOM8: i64 = 12 * 256;                // the boom: 12 units behind (the 28-degree
                                                   // vertical FOV makes a near boom a face full
                                                   // of cloak; 12 units frames the wanderer)
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
            trace_in.rows[frame as usize]
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
        // v1.13: the wanderer. Input drives the AVATAR anchor (cam.px/py); the render eye
        // booms back along the camera's horizontal forward, and the avatar's clip state
        // machine is the certified canonical stepper driven by the move keys (go on press,
        // stop on release — the same two-event vocabulary the trace already carries).
        let rcam = if args.third {
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
                let n = isqrt64(n2).max(1);
                (fwx * 65536 / n, fwy * 65536 / n)
            };
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
            let reach = ladder[ladder.len() - 1].2;
            draw_castle(&mut buf, &mut zbuf, cw, ch, &cm, (rcam.px, rcam.py, ceye),
                        &castle, reach * TILE * 256);
        }
        if args.third && !ladder.is_empty() {
            let t_q32 = fx_cam.rdiv((frame - av_start) as i128 * ONE as i128, 120);
            let (joints, _g8) = avatar_joints(&mut fx_cam, &mut lodw, &cam, &av_m,
                                              av_state, t_q32);
            // the render eye, recomputed by the eye's own bilinear law at the boom position
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
        if args.sky { star_sky(&mut fx_cam, &mut buf, &mut zbuf, cw, ch, &rcam); }
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
        // v1.13.2: A CONDITION SAMPLED ONCE IS AN ASSUMPTION THAT IT HELD THROUGHOUT. The
        // named host's composition run reported focus_foreground false from a single
        // start-of-run sample, which cannot say whether the window lacked focus for one
        // frame or for all of them — and a background window is scheduled differently, so
        // the cost record's conditions were unknown exactly where they mattered most.
        // Focus is still a REPORTED CONDITION, never a dependency (L83 stands): it is now
        // reported as a COUNT. Sampled here, outside both timed windows.
        if unsafe { GetForegroundWindow() } == hwnd { focus_frames += 1 }

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
        let mut t = String::from("# fpsdemo v1.17 input trace: keys dx dy (one line per frame)
");
        // THE DECLARATION, written by the only party that knows the intended length.
        t.push_str(&format!("# frames {}
", trace_rec.len()));
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
        "fpsdemo v1.17 | host {} | power {} | scheduler {} | hz {} | res {}x{} | mode {} | \
reach {} | sky {} | third {} | castle {} | qpf {}\n",
        args.host, args.power, args.scheduler, args.hz, cw, ch,
        if args.play { "play" } else { "replay" }, args.reach,
        if args.sky { "starfield" } else { "off" },
        if args.third { "wanderer" } else { "off" },
        if castle.is_empty() { "off".to_string() } else { format!("{}", castle.len()) },
        freq));
    if !ladder.is_empty() {
        for &(stride, inn, out) in &ladder {
            log.push_str(&format!("ring stride {} tiles {}..{}\n", stride, inn, out));
        }
        log.push_str(&format!("prefill_tiles {}\n", prefill_tiles));
        log.push_str(&format!("cache_cap {} | occupancy {} | recomputes {} | evictions {}\n",
                              cache_cap, lodw.cache.len(), lodw.recomputes,
                              lodw.evictions));
        log.push_str(&format!("cache_policy {}\n", cache_policy));
    }
    log.push_str(&format!("timer_1ms_granted {} | focus_foreground {} | focus_frames {}/{} | \
focus_wait_ms {} | xinput_loaded {} | pad_connected {}
",
                          timer_1ms_granted, focus_foreground, focus_frames, frame,
                          focus_wait_ms,
                          if args.play { if xi_get.is_some() { "true" } else { "false" } }
                          else { "n/a" },
                          if args.play { if pad_seen { "true" } else { "false" } }
                          else { "n/a" }));

    // v1.15 — THE MEASUREMENT ADMISSION CONTRACT. `COMPLETE` means EVERY condition this
    // measurement class declares has passed; it does not mean the program reached the end of
    // its input. A truncated replay used to print a record indistinguishable in shape from a
    // finished one, and the only reason one was ever caught is that three runs were compared by
    // hand. The conditions are emitted individually so a future one is a NAMED PREDICATE rather
    // than another ad-hoc boolean, and the status is their conjunction.
    //
    // THE CLASS DECIDES WHAT COUNTS AS VALID, so this is a declaration and not an `if` ladder
    // waiting to grow. `replay` requires strict frame equality and strict focus equality — a
    // frame drawn to a window without the foreground is a measurement nobody was watching.
    // `play` carries NO completeness verdict at all, because a play run produces a TRACE rather
    // than a measurement and its final frame losing focus as the window closes is benign; a
    // door that fired on almost every honest session is the warning nobody reads.
    //
    // THE INSTRUMENT REPORTS; THE GATE ADJUDICATES. The reader recomputes these predicates from
    // the record's own fields and compares them to the status printed here. Agreement admits or
    // rejects; DISAGREEMENT is a third and more serious outcome, because it means this contract
    // and the reader's have drifted apart — the failure where both halves are individually green
    // and the pair is lying.
    log.push_str(&format!("measurement_class {}
",
                          if args.play { "play" } else { "replay" }));
    if !args.replay.is_empty() {
        let expected = trace_in.declared.unwrap_or(trace_in.rows.len());
        let frames_ok = frame as usize == expected;
        let focus_ok = focus_frames == frame;
        let mut missed: Vec<&str> = Vec::new();
        if !frames_ok { missed.push("frames") }
        if !focus_ok { missed.push("focus") }
        log.push_str(&format!("replay_trace {} bytes {}
", args.replay, trace_in.bytes_hex));
        log.push_str(&format!("replay_workload sha256 {}
", trace_in.workload_hex));
        log.push_str(&format!("replay_declared {}
",
                              match trace_in.declared {
                                  Some(n) => n.to_string(),
                                  None => "legacy".to_string() }));
        log.push_str(&format!("replay_frames {}/{}
", frame, expected));
        log.push_str(&format!("replay_focus {}/{}
", focus_frames, frame));
        log.push_str(&format!("replay_status {}
",
                              if missed.is_empty() { "COMPLETE".to_string() }
                              else { format!("INCOMPLETE ({})", missed.join(", ")) }));
    }
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

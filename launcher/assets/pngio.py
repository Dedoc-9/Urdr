# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""pngio — a stdlib PNG codec for the launcher's asset tools (off-gate).

Reads 8-bit RGB / RGBA / greyscale PNGs (all five scanline filters, no interlace) into a flat RGB or RGBA byte
buffer, and writes RGB / RGBA buffers as unfiltered PNGs. No PIL, no numpy: the asset tools must run on the same
stdlib Python that runs the gate. Reproducible up to the container: `write_png` bytes depend on zlib, so identity
is always the PIXEL sha256 (`pixel_sha256`), never the file's — the same lesson `vista.png_bytes` states."""
import hashlib
import struct
import zlib

_SIG = b"\x89PNG\r\n\x1a\n"


class PngError(Exception):
    pass


def _chunks(data):
    if data[:8] != _SIG:
        raise PngError("not a PNG (bad signature)")
    pos = 8
    while pos + 8 <= len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        yield tag, body
        pos += 12 + ln
        if tag == b"IEND":
            return


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def read_png(path):
    """-> (width, height, channels, pixels) with pixels a flat bytes buffer, row-major, `channels` in {1, 3, 4}."""
    with open(path, "rb") as fh:
        data = fh.read()
    w = h = None
    bit_depth = colour = interlace = None
    idat = bytearray()
    for tag, body in _chunks(data):
        if tag == b"IHDR":
            w, h, bit_depth, colour, _cm, _fm, interlace = struct.unpack(">IIBBBBB", body[:13])
        elif tag == b"IDAT":
            idat += body
    if w is None:
        raise PngError("no IHDR")
    if bit_depth != 8:
        raise PngError("only 8-bit PNGs are read (got bit depth %d)" % bit_depth)
    if interlace:
        raise PngError("interlaced PNGs are not read")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(colour)
    if channels is None:
        raise PngError("unsupported colour type %d (palette PNGs are not read)" % colour)
    raw = zlib.decompress(bytes(idat))
    stride = w * channels
    out = bytearray(h * stride)
    prev = bytearray(stride)
    pos = 0
    for row in range(h):
        f = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if f == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                c = prev[i - channels] if i >= channels else 0
                line[i] = (line[i] + _paeth(a, prev[i], c)) & 0xFF
        elif f != 0:
            raise PngError("bad scanline filter %d" % f)
        out[row * stride:(row + 1) * stride] = line
        prev = line
    if channels == 2:                                            # grey+alpha -> RGBA
        rgba = bytearray()
        for i in range(0, len(out), 2):
            rgba += bytes((out[i], out[i], out[i], out[i + 1]))
        out, channels = rgba, 4
    return w, h, channels, bytes(out)


def to_rgb(w, h, channels, pixels):
    """Drop alpha / expand grey so callers can work in RGB."""
    if channels == 3:
        return pixels
    out = bytearray()
    if channels == 4:
        for i in range(0, len(pixels), 4):
            out += pixels[i:i + 3]
    else:
        for v in pixels:
            out += bytes((v, v, v))
    return bytes(out)


def write_png(path, w, h, channels, pixels, level=6):
    """RGB (3) or RGBA (4) flat buffer -> PNG file. Unfiltered scanlines; zlib level as given."""
    if channels not in (3, 4):
        raise PngError("write_png takes RGB or RGBA")
    stride = w * channels
    if len(pixels) != h * stride:
        raise PngError("pixel buffer is %d bytes, expected %d" % (len(pixels), h * stride))
    rows = bytearray()
    for r in range(h):
        rows.append(0)
        rows += pixels[r * stride:(r + 1) * stride]

    def chunk(tag, body):
        c = tag + body
        return struct.pack(">I", len(body)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    data = (_SIG + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2 if channels == 3 else 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(rows), level)) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(data)
    return data


def pixel_sha256(pixels):
    return hashlib.sha256(bytes(pixels)).hexdigest()


def file_sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()

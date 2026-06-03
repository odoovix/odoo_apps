#!/usr/bin/env python3
import math
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_GIF = ROOT / "demo.gif"
OUT_BANNER = ROOT / "banner.png"
WIDTH = 960
HEIGHT = 520
SCALE_X = WIDTH / 1364.0
SCALE_Y = HEIGHT / 738.0


def sx(value):
    return int(round(value * SCALE_X))


def sy(value):
    return int(round(value * SCALE_Y))


def read_png(path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    pos = 8
    width = height = bit_depth = color_type = None
    compressed = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        pos += 4
        ctype = data[pos:pos + 4]
        pos += 4
        chunk = data[pos:pos + length]
        pos += length + 4
        if ctype == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", chunk)
        elif ctype == b"IDAT":
            compressed.extend(chunk)
        elif ctype == b"IEND":
            break
    if bit_depth != 8 or color_type != 6:
        raise ValueError(f"Unsupported PNG format in {path.name}: bit depth {bit_depth}, color type {color_type}")
    raw = zlib.decompress(bytes(compressed))
    stride = width * 4
    rows = []
    prev = [0] * stride
    p = 0
    for _ in range(height):
        filter_type = raw[p]
        p += 1
        row = list(raw[p:p + stride])
        p += stride
        if filter_type == 1:
            for i in range(stride):
                left = row[i - 4] if i >= 4 else 0
                row[i] = (row[i] + left) & 255
        elif filter_type == 2:
            for i in range(stride):
                row[i] = (row[i] + prev[i]) & 255
        elif filter_type == 3:
            for i in range(stride):
                left = row[i - 4] if i >= 4 else 0
                row[i] = (row[i] + ((left + prev[i]) >> 1)) & 255
        elif filter_type == 4:
            for i in range(stride):
                a = row[i - 4] if i >= 4 else 0
                b = prev[i]
                c = prev[i - 4] if i >= 4 else 0
                row[i] = (row[i] + paeth(a, b, c)) & 255
        elif filter_type != 0:
            raise ValueError(f"Unsupported PNG filter {filter_type} in {path.name}")
        rows.append(row)
        prev = row
    return width, height, rows


def paeth(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def make_canvas():
    pixels = [0] * (WIDTH * HEIGHT * 4)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r = int(24 + (60 - 24) * x / (WIDTH - 1))
            g = int(9 + (22 - 9) * x / (WIDTH - 1))
            b = int(40 + (102 - 40) * x / (WIDTH - 1))
            cx = x - 300
            cy = y - 540
            glow = max(0.0, 1.0 - math.sqrt(cx * cx + cy * cy) / 470.0)
            r = min(255, int(r + 70 * glow))
            g = min(255, int(g + 35 * glow))
            b = min(255, int(b + 90 * glow))
            idx = (y * WIDTH + x) * 4
            pixels[idx:idx + 4] = [r, g, b, 255]
    return pixels


def fill_rect(pixels, x, y, w, h, color):
    r, g, b, a = color
    alpha = a / 255.0
    for yy in range(max(0, y), min(HEIGHT, y + h)):
        row = yy * WIDTH
        for xx in range(max(0, x), min(WIDTH, x + w)):
            idx = (row + xx) * 4
            if alpha >= 1:
                pixels[idx:idx + 4] = [r, g, b, 255]
            else:
                inv = 1.0 - alpha
                pixels[idx] = int(r * alpha + pixels[idx] * inv)
                pixels[idx + 1] = int(g * alpha + pixels[idx + 1] * inv)
                pixels[idx + 2] = int(b * alpha + pixels[idx + 2] * inv)
                pixels[idx + 3] = 255


def fill_rounded_rect(pixels, x, y, w, h, radius, color):
    rr = radius * radius
    r, g, b, a = color
    alpha = a / 255.0
    for yy in range(max(0, y), min(HEIGHT, y + h)):
        for xx in range(max(0, x), min(WIDTH, x + w)):
            dx = 0
            dy = 0
            if xx < x + radius:
                dx = x + radius - xx
            elif xx >= x + w - radius:
                dx = xx - (x + w - radius - 1)
            if yy < y + radius:
                dy = y + radius - yy
            elif yy >= y + h - radius:
                dy = yy - (y + h - radius - 1)
            if dx and dy and dx * dx + dy * dy > rr:
                continue
            idx = (yy * WIDTH + xx) * 4
            if alpha >= 1:
                pixels[idx:idx + 4] = [r, g, b, 255]
            else:
                inv = 1.0 - alpha
                pixels[idx] = int(r * alpha + pixels[idx] * inv)
                pixels[idx + 1] = int(g * alpha + pixels[idx + 1] * inv)
                pixels[idx + 2] = int(b * alpha + pixels[idx + 2] * inv)
                pixels[idx + 3] = 255


def blit_cover(pixels, png, box, crop_focus=0.5):
    src_w, src_h, rows = png
    dst_x, dst_y, dst_w, dst_h = box
    src_ratio = src_w / src_h
    dst_ratio = dst_w / dst_h
    if src_ratio > dst_ratio:
        crop_h = src_h
        crop_w = int(crop_h * dst_ratio)
        crop_x = int((src_w - crop_w) * crop_focus)
        crop_y = 0
    else:
        crop_w = src_w
        crop_h = int(crop_w / dst_ratio)
        crop_x = 0
        crop_y = int((src_h - crop_h) * crop_focus)
    for yy in range(dst_h):
        sy = crop_y + min(crop_h - 1, int(yy * crop_h / dst_h))
        src_row = rows[sy]
        dy = dst_y + yy
        if dy < 0 or dy >= HEIGHT:
            continue
        for xx in range(dst_w):
            sx = crop_x + min(crop_w - 1, int(xx * crop_w / dst_w))
            sidx = sx * 4
            alpha = src_row[sidx + 3]
            if alpha == 0:
                continue
            didx = (dy * WIDTH + (dst_x + xx)) * 4
            if dst_x + xx < 0 or dst_x + xx >= WIDTH:
                continue
            if alpha == 255:
                pixels[didx:didx + 4] = src_row[sidx:sidx + 4]
            else:
                a = alpha / 255.0
                inv = 1.0 - a
                pixels[didx] = int(src_row[sidx] * a + pixels[didx] * inv)
                pixels[didx + 1] = int(src_row[sidx + 1] * a + pixels[didx + 1] * inv)
                pixels[didx + 2] = int(src_row[sidx + 2] * a + pixels[didx + 2] * inv)
                pixels[didx + 3] = 255


def add_frame(png_main, png_secondary):
    pixels = make_canvas()
    fill_rounded_rect(pixels, sx(72), sy(74), sx(560), sy(500), sx(30), (10, 4, 22, 42))
    fill_rounded_rect(pixels, sx(92), sy(114), sx(346), sy(38), sx(19), (255, 255, 255, 248))
    fill_rounded_rect(pixels, sx(92), sy(170), sx(298), sy(38), sx(19), (255, 255, 255, 248))
    fill_rounded_rect(pixels, sx(92), sy(226), sx(270), sy(38), sx(19), (255, 255, 255, 248))
    fill_rounded_rect(pixels, sx(750), sy(82), sx(530), sy(252), sx(28), (255, 255, 255, 24))
    fill_rounded_rect(pixels, sx(790), sy(388), sx(490), sy(258), sx(28), (255, 255, 255, 20))
    fill_rounded_rect(pixels, sx(822), sy(654), sx(432), sy(52), sx(16), (255, 255, 255, 245))
    fill_rect(pixels, sx(838), sy(670), sx(150), sy(10), (255, 255, 255, 188))
    blit_cover(pixels, png_main, (sx(754), sy(86), sx(522), sy(244)), crop_focus=0.5)
    blit_cover(pixels, png_secondary, (sx(794), sy(392), sx(482), sy(250)), crop_focus=0.5)
    blit_cover(pixels, png_secondary, (sx(826), sy(658), sx(424), sy(44)), crop_focus=0.82)
    return pixels


def build_palette():
    palette = []
    for r in [0, 51, 102, 153, 204, 255]:
        for g in [0, 51, 102, 153, 204, 255]:
            for b in [0, 51, 102, 153, 204, 255]:
                palette.append((r, g, b))
    extras = [
        (24, 9, 40), (44, 20, 83), (60, 22, 102), (91, 58, 181),
        (229, 220, 255), (251, 248, 255), (255, 255, 255), (15, 10, 28),
        (183, 167, 255), (132, 106, 240), (243, 230, 255), (210, 194, 247),
    ]
    palette.extend(extras)
    while len(palette) < 256:
        g = int(255 * len(palette) / 255)
        palette.append((g, g, g))
    return palette[:256]


PALETTE = build_palette()


def rgba_to_indices(pixels):
    out = bytearray(WIDTH * HEIGHT)
    for i in range(WIDTH * HEIGHT):
        r = pixels[i * 4]
        g = pixels[i * 4 + 1]
        b = pixels[i * 4 + 2]
        if r == g == b:
            idx = 228 + min(27, r // 10) if r < 280 else 255
        else:
            idx = (round(r / 51) * 36) + (round(g / 51) * 6) + round(b / 51)
            if idx > 215:
                idx = 215
        out[i] = idx
    return bytes(out)


def pack_codes(indices, min_code_size):
    clear = 1 << min_code_size
    end = clear + 1
    code_size = min_code_size + 1
    dictionary = {bytes([i]): i for i in range(clear)}
    next_code = end + 1
    bits = []

    def emit(code):
        bits.append((code, code_size))

    emit(clear)
    prefix = bytes([indices[0]])
    for value in indices[1:]:
        char = bytes([value])
        combo = prefix + char
        if combo in dictionary:
            prefix = combo
            continue
        emit(dictionary[prefix])
        if next_code < 4096:
            dictionary[combo] = next_code
            next_code += 1
            if next_code == (1 << code_size) and code_size < 12:
                code_size += 1
        else:
            emit(clear)
            dictionary = {bytes([i]): i for i in range(clear)}
            next_code = end + 1
            code_size = min_code_size + 1
        prefix = char
    emit(dictionary[prefix])
    emit(end)

    out = bytearray()
    cur = 0
    nbits = 0
    for code, size in bits:
        cur |= code << nbits
        nbits += size
        while nbits >= 8:
            out.append(cur & 255)
            cur >>= 8
            nbits -= 8
    if nbits:
        out.append(cur & 255)
    return bytes(out)


def subblocks(data):
    result = bytearray()
    for i in range(0, len(data), 255):
        chunk = data[i:i + 255]
        result.append(len(chunk))
        result.extend(chunk)
    result.append(0)
    return bytes(result)


def write_gif(frames, path):
    palette_bytes = bytearray()
    for r, g, b in PALETTE:
        palette_bytes.extend([r, g, b])
    out = bytearray()
    out.extend(b"GIF89a")
    out.extend(struct.pack("<HH", WIDTH, HEIGHT))
    out.extend(bytes([0b11110111, 0, 0]))
    out.extend(palette_bytes)
    out.extend(b"!\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")
    for delay, frame in frames:
        out.extend(b"!\xF9\x04\x04")
        out.extend(struct.pack("<H", delay))
        out.extend(b"\x00\x00")
        out.extend(b",")
        out.extend(struct.pack("<HHHHB", 0, 0, WIDTH, HEIGHT, 0))
        out.append(8)
        out.extend(subblocks(pack_codes(frame, 8)))
    out.append(0x3B)
    path.write_bytes(bytes(out))


def write_png_rgba(width, height, pixels, path):
    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        start = y * stride
        raw.extend(pixels[start:start + stride])

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
    png.extend(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
    png.extend(chunk(b"IEND", b""))
    path.write_bytes(bytes(png))


def make_canvas_full(width, height):
    pixels = [0] * (width * height * 4)
    for y in range(height):
        for x in range(width):
            r = int(24 + (60 - 24) * x / max(1, width - 1))
            g = int(9 + (22 - 9) * x / max(1, width - 1))
            b = int(40 + (102 - 40) * x / max(1, width - 1))
            cx = x - int(width * 0.22)
            cy = y - int(height * 0.80)
            glow = max(0.0, 1.0 - math.sqrt(cx * cx + cy * cy) / (width * 0.35))
            r = min(255, int(r + 70 * glow))
            g = min(255, int(g + 35 * glow))
            b = min(255, int(b + 90 * glow))
            idx = (y * width + x) * 4
            pixels[idx:idx + 4] = [r, g, b, 255]
    return pixels


def fill_rect_full(pixels, width, height, x, y, w, h, color):
    r, g, b, a = color
    alpha = a / 255.0
    for yy in range(max(0, y), min(height, y + h)):
        row = yy * width
        for xx in range(max(0, x), min(width, x + w)):
            idx = (row + xx) * 4
            if alpha >= 1:
                pixels[idx:idx + 4] = [r, g, b, 255]
            else:
                inv = 1.0 - alpha
                pixels[idx] = int(r * alpha + pixels[idx] * inv)
                pixels[idx + 1] = int(g * alpha + pixels[idx + 1] * inv)
                pixels[idx + 2] = int(b * alpha + pixels[idx + 2] * inv)
                pixels[idx + 3] = 255


def fill_rounded_rect_full(pixels, width, height, x, y, w, h, radius, color):
    rr = radius * radius
    r, g, b, a = color
    alpha = a / 255.0
    for yy in range(max(0, y), min(height, y + h)):
        for xx in range(max(0, x), min(width, x + w)):
            dx = 0
            dy = 0
            if xx < x + radius:
                dx = x + radius - xx
            elif xx >= x + w - radius:
                dx = xx - (x + w - radius - 1)
            if yy < y + radius:
                dy = y + radius - yy
            elif yy >= y + h - radius:
                dy = yy - (y + h - radius - 1)
            if dx and dy and dx * dx + dy * dy > rr:
                continue
            idx = (yy * width + xx) * 4
            if alpha >= 1:
                pixels[idx:idx + 4] = [r, g, b, 255]
            else:
                inv = 1.0 - alpha
                pixels[idx] = int(r * alpha + pixels[idx] * inv)
                pixels[idx + 1] = int(g * alpha + pixels[idx + 1] * inv)
                pixels[idx + 2] = int(b * alpha + pixels[idx + 2] * inv)
                pixels[idx + 3] = 255


def blit_cover_full(pixels, width, height, png, box, crop_focus=0.5):
    src_w, src_h, rows = png
    dst_x, dst_y, dst_w, dst_h = box
    src_ratio = src_w / src_h
    dst_ratio = dst_w / dst_h
    if src_ratio > dst_ratio:
        crop_h = src_h
        crop_w = int(crop_h * dst_ratio)
        crop_x = int((src_w - crop_w) * crop_focus)
        crop_y = 0
    else:
        crop_w = src_w
        crop_h = int(crop_w / dst_ratio)
        crop_x = 0
        crop_y = int((src_h - crop_h) * crop_focus)
    for yy in range(dst_h):
        sy = crop_y + min(crop_h - 1, int(yy * crop_h / dst_h))
        src_row = rows[sy]
        dy = dst_y + yy
        if dy < 0 or dy >= height:
            continue
        for xx in range(dst_w):
            dx = dst_x + xx
            if dx < 0 or dx >= width:
                continue
            sx_value = crop_x + min(crop_w - 1, int(xx * crop_w / dst_w))
            sidx = sx_value * 4
            alpha = src_row[sidx + 3]
            if alpha == 0:
                continue
            didx = (dy * width + dx) * 4
            if alpha == 255:
                pixels[didx:didx + 4] = src_row[sidx:sidx + 4]
            else:
                a = alpha / 255.0
                inv = 1.0 - a
                pixels[didx] = int(src_row[sidx] * a + pixels[didx] * inv)
                pixels[didx + 1] = int(src_row[sidx + 1] * a + pixels[didx + 1] * inv)
                pixels[didx + 2] = int(src_row[sidx + 2] * a + pixels[didx + 2] * inv)
                pixels[didx + 3] = 255


def blit_crop_full(pixels, width, height, png, src_box, dst_box):
    src_w, src_h, rows = png
    src_x, src_y, src_box_w, src_box_h = src_box
    dst_x, dst_y, dst_w, dst_h = dst_box
    for yy in range(dst_h):
        sy = src_y + min(src_box_h - 1, int(yy * src_box_h / dst_h))
        src_row = rows[sy]
        dy = dst_y + yy
        if dy < 0 or dy >= height:
            continue
        for xx in range(dst_w):
            dx = dst_x + xx
            if dx < 0 or dx >= width:
                continue
            sx_value = src_x + min(src_box_w - 1, int(xx * src_box_w / dst_w))
            sidx = sx_value * 4
            alpha = src_row[sidx + 3]
            if alpha == 0:
                continue
            didx = (dy * width + dx) * 4
            if alpha == 255:
                pixels[didx:didx + 4] = src_row[sidx:sidx + 4]
            else:
                a = alpha / 255.0
                inv = 1.0 - a
                pixels[didx] = int(src_row[sidx] * a + pixels[didx] * inv)
                pixels[didx + 1] = int(src_row[sidx + 1] * a + pixels[didx + 1] * inv)
                pixels[didx + 2] = int(src_row[sidx + 2] * a + pixels[didx + 2] * inv)
                pixels[didx + 3] = 255


def build_banner_png():
    width = 1364
    height = 738
    pixels = make_canvas_full(width, height)
    fill_rounded_rect_full(pixels, width, height, 64, 66, 582, 490, 30, (10, 4, 22, 42))
    fill_rounded_rect_full(pixels, width, height, 64, 66, 582, 490, 30, (244, 239, 255, 18))
    fill_rounded_rect_full(pixels, width, height, 98, 96, 488, 312, 46, (255, 255, 255, 18))

    fill_rounded_rect_full(pixels, width, height, 748, 80, 528, 248, 28, (246, 241, 255, 34))
    fill_rounded_rect_full(pixels, width, height, 790, 386, 486, 214, 28, (246, 241, 255, 28))
    fill_rounded_rect_full(pixels, width, height, 776, 612, 500, 96, 18, (255, 253, 253, 248))

    config = read_png(ROOT / "img" / "2.png")
    lines = read_png(ROOT / "img" / "4.png")
    preview = read_png(ROOT / "export_preview.png")
    logo = read_png(ROOT / "icon.png")

    blit_crop_full(pixels, width, height, logo, (150, 120, 724, 724), (112, 104, 460, 294))
    fill_rect_full(pixels, width, height, 112, 104, 460, 10, (42, 18, 80, 255))
    blit_cover_full(pixels, width, height, config, (754, 86, 516, 236), crop_focus=0.5)
    blit_cover_full(pixels, width, height, lines, (796, 392, 474, 202), crop_focus=0.5)
    blit_cover_full(pixels, width, height, preview, (782, 618, 488, 84), crop_focus=0.5)

    fill_rounded_rect_full(pixels, width, height, 796, 626, 158, 10, 5, (255, 255, 255, 188))
    write_png_rgba(width, height, pixels, OUT_BANNER)


def main():
    images = [read_png(ROOT / "img" / f"{idx}.png") for idx in range(1, 7)]
    secondary = images[5]
    frames = []
    for image in images[:5]:
        frames.append((90, rgba_to_indices(add_frame(image, secondary))))
    frames.append((140, rgba_to_indices(add_frame(images[4], images[5]))))
    frames.append((170, rgba_to_indices(add_frame(images[5], images[5]))))
    write_gif(frames, OUT_GIF)
    build_banner_png()
    print(f"Wrote {OUT_GIF}")
    print(f"Wrote {OUT_BANNER}")


if __name__ == "__main__":
    main()

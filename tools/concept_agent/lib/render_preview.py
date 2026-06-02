from pathlib import Path

import numpy as np


def render_class_preview(instance, output_dir, class_name):
    from PIL import Image, ImageDraw

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    vertices = np.asarray(instance.vertices, dtype=float)
    faces = np.asarray(instance.faces, dtype=int)

    image_size = 512
    margin = 36
    image = Image.new("RGB", (image_size, image_size), "white")
    draw = ImageDraw.Draw(image, "RGBA")

    projected = _project_xy(vertices, image_size=image_size, margin=margin)
    for face in faces[:2000]:
        polygon = [tuple(projected[index]) for index in face]
        draw.polygon(polygon, fill=(110, 150, 190, 70), outline=(32, 63, 90, 170))

    draw.text((16, 14), class_name, fill=(25, 25, 25))
    filename = f"{_safe_filename(class_name)}.png"
    path = output_dir / filename
    image.save(path)
    return path


def write_preview_sheet(preview_paths, output_path):
    from PIL import Image, ImageDraw

    preview_paths = [Path(path) for path in preview_paths if path]
    if not preview_paths:
        return None

    thumbs = []
    for path in preview_paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((220, 220))
        thumbs.append((path, image.copy()))

    cols = min(4, len(thumbs))
    rows = int(np.ceil(len(thumbs) / cols))
    cell_w, cell_h = 250, 260
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    for index, (path, image) in enumerate(thumbs):
        row, col = divmod(index, cols)
        left = col * cell_w + (cell_w - image.width) // 2
        top = row * cell_h + 14
        sheet.paste(image, (left, top))
        draw.text((col * cell_w + 12, row * cell_h + 232), path.stem[:32], fill=(25, 25, 25))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)
    return output_path


def _project_xy(vertices, image_size, margin):
    xy = vertices[:, [0, 1]]
    min_xy = xy.min(axis=0)
    max_xy = xy.max(axis=0)
    span = max_xy - min_xy
    scale = (image_size - 2 * margin) / max(float(span.max()), 1e-9)
    normalized = (xy - min_xy) * scale + margin
    normalized[:, 1] = image_size - normalized[:, 1]
    return normalized.astype(int)


def _safe_filename(value):
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value)

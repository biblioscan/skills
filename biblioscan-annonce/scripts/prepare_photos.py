#!/usr/bin/env python3
"""Associe les photos aux ISBN/ASIN et les prépare pour l'upload (JPEG, <= 1600 px).

Rangements acceptés, détectés automatiquement :
  1. sous-dossier par livre   photos/9782909698281/*.jpg
  2. fichiers nommés          photos/9782909698281_1.jpg, photos/2909698289-dos.heic
  3. dossier en vrac          photos/IMG_0001.HEIC ...  -> listés dans "unmatched"

Usage : prepare_photos.py <dossier_photos> <id1> [<id2> ...] [--out <dossier>]
Sortie : JSON sur stdout {"books": {id: [chemins]}, "unmatched": [...], "missing": [...]}
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

IMG_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}
MAX_SIDE = 1600


def isbn10_to_13(s):
    core = "978" + s[:9]
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(core))
    return core + str((10 - total % 10) % 10)


def isbn13_to_10(s):
    if not s.startswith("978"):
        return None
    core = s[3:12]
    total = sum(int(d) * (10 - i) for i, d in enumerate(core))
    check = (11 - total % 11) % 11
    return core + ("X" if check == 10 else str(check))


def variants(raw):
    """Toutes les écritures sous lesquelles un identifiant peut apparaître dans un nom de fichier."""
    s = re.sub(r"[^0-9A-Za-z]", "", raw).upper()
    out = {s}
    if re.fullmatch(r"\d{13}", s):
        v10 = isbn13_to_10(s)
        if v10:
            out.add(v10)
    elif re.fullmatch(r"\d{9}[\dX]", s):
        out.add(isbn10_to_13(s))
    return out


def natural_key(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def is_img(p):
    return p.is_file() and p.suffix.lower() in IMG_EXT and not p.name.startswith(".")


def convert(src, dst):
    """Convertit en JPEG redimensionné ; sips (macOS) puis Pillow, sinon copie brute."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("sips"):
        r = subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", "-Z", str(MAX_SIDE), str(src), "--out", str(dst)],
            capture_output=True,
        )
        if r.returncode == 0 and dst.exists():
            return dst
    try:
        from PIL import Image, ImageOps

        img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        img.thumbnail((MAX_SIDE, MAX_SIDE))
        img.save(dst, "JPEG", quality=85)
        return dst
    except Exception:
        if src.suffix.lower() in {".jpg", ".jpeg"}:
            shutil.copy2(src, dst)
            return dst
        print(f"avertissement : impossible de convertir {src}", file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--out")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    out = Path(args.out).expanduser().resolve() if args.out else root / "_prepared"
    used = set()
    books, missing = {}, []

    for raw in args.ids:
        keys = variants(raw)
        found = []
        # 1. sous-dossier dont le nom contient l'identifiant
        for d in sorted(p for p in root.iterdir() if p.is_dir() and p != out):
            name = re.sub(r"[^0-9A-Za-z]", "", d.name).upper()
            if any(k in name for k in keys):
                found = sorted((p for p in d.iterdir() if is_img(p)), key=natural_key)
                break
        # 2. fichiers à la racine dont le nom contient l'identifiant
        if not found:
            found = sorted(
                (p for p in root.iterdir() if is_img(p) and any(k in re.sub(r"[^0-9A-Za-z]", "", p.stem).upper() for k in keys)),
                key=natural_key,
            )
        if not found:
            missing.append(raw)
            continue
        used.update(found)
        prepared = [convert(p, out / raw / f"{i + 1}_{p.stem}.jpg") for i, p in enumerate(found)]
        books[raw] = [str(p) for p in prepared if p]

    # 3. le reste (racine + sous-dossiers non attribués) = vrac, converti pour pouvoir être regardé
    unmatched = []
    for p in sorted((p for p in root.rglob("*") if is_img(p) and out not in p.parents and p not in used), key=natural_key):
        dst = convert(p, out / "_vrac" / f"{p.parent.name}__{p.stem}.jpg" if p.parent != root else out / "_vrac" / f"{p.stem}.jpg")
        if dst:
            unmatched.append({"original": str(p), "prepared": str(dst), "mtime": p.stat().st_mtime})

    json.dump({"books": books, "unmatched": unmatched, "missing": missing, "out": str(out)}, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()

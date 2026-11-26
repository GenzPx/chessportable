#!/usr/bin/env sh
set -e

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/apt-repo}"
REPO_URL="${2:-https://genzpx.github.io/chessportable}"

sh "$SCRIPT_DIR/build_deb.sh"

PKG_VERSION="$(python3 -c "import re; print(re.search(r'__version__\s*=\s*\"([^\"]+)\"', open('${ROOT_DIR}/chessportable/__init__.py').read()).group(1))")"
DEB_FILE="${ROOT_DIR}/chessportable_${PKG_VERSION}_all.deb"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"
cp "$DEB_FILE" "$OUT_DIR/"

python3 - "$OUT_DIR" "$(basename "$DEB_FILE")" "$PKG_VERSION" "$REPO_URL" <<'PYEOF'
import gzip
import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

out_dir = Path(sys.argv[1])
deb_name = sys.argv[2]
version = sys.argv[3]
repo_url = sys.argv[4].rstrip("/")
deb_path = out_dir / deb_name

control = subprocess.check_output(["dpkg-deb", "-f", str(deb_path)], text=True).strip()
data = deb_path.read_bytes()
size = len(data)
md5 = hashlib.md5(data).hexdigest()
sha1 = hashlib.sha1(data).hexdigest()
sha256 = hashlib.sha256(data).hexdigest()

packages_txt = (
    f"{control}\n"
    f"Filename: ./{deb_name}\n"
    f"Size: {size}\n"
    f"MD5sum: {md5}\n"
    f"SHA1: {sha1}\n"
    f"SHA256: {sha256}\n\n"
)

pkg_file = out_dir / "Packages"
pkg_file.write_text(packages_txt, encoding="utf-8")
(out_dir / "Packages.gz").write_bytes(gzip.compress(packages_txt.encode("utf-8"), mtime=0))

now_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")

def hashes_for(p: Path):
    b = p.read_bytes()
    return len(b), hashlib.md5(b).hexdigest(), hashlib.sha256(b).hexdigest()

files = [("Packages", *hashes_for(pkg_file)), ("Packages.gz", *hashes_for(out_dir / "Packages.gz"))]
release_lines = [
    "Origin: GenzPX",
    "Label: ChessPortable Termux Repo",
    "Suite: stable",
    "Codename: stable",
    f"Date: {now_str}",
    "Architectures: all",
    "Description: Termux APT repository for ChessPortable by GenzPX",
    "MD5Sum:",
]
for fname, fsize, fmd5, _ in files:
    release_lines.append(f" {fmd5} {fsize:>16} {fname}")
release_lines.append("SHA256:")
for fname, fsize, _, fsha256 in files:
    release_lines.append(f" {fsha256} {fsize:>16} {fname}")

(out_dir / "Release").write_text("\n".join(release_lines) + "\n", encoding="utf-8")

html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ChessPortable v{version} by GenzPX — Termux APT Repository</title>
<style>
  body {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: #0d1117; color: #e6edf3; max-width: 720px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
  h1 {{ color: #58a6ff; }}
  pre {{ background: #161b22; border: 1px solid #30363d; padding: 14px; border-radius: 8px; overflow-x: auto; }}
  code {{ color: #7ee787; }}
  a {{ color: #58a6ff; }}
  .badge {{ display: inline-block; background: #238636; color: #fff; padding: 2px 8px; border-radius: 999px; font-size: 12px; }}
  .foot {{ margin-top: 32px; color: #8b949e; font-size: 13px; }}
</style>
</head>
<body>
  <h1>♟ ChessPortable <span class="badge">v{version}</span></h1>
  <p>Full CLI Chess untuk Termux by <strong>GenzPX</strong> — Pure Python, 10 Bots, Per-Bot Adaptive (A 0-9), ARC Auto-Sequence, ECO Openings, Tactical Coach, Gauntlet, Puzzles &amp; 2P.</p>
  <h2>Install via Termux <code>pkg</code></h2>
  <pre><code>echo "deb [trusted=yes] {repo_url} ./" &gt; $PREFIX/etc/apt/sources.list.d/chessportable.list
pkg update
pkg install chessportable</code></pre>
  <h2>Jalankan</h2>
  <pre><code>chessportable</code></pre>
  <p>Download langsung <a href="./{deb_name}">{deb_name}</a> lalu jalankan <code>pkg install ./{deb_name}</code>.</p>
  <p class="foot">Created by <a href="https://github.com/GenzPx/chessportable">GenzPX</a></p>
</body>
</html>
"""
(out_dir / "index.html").write_text(html, encoding="utf-8")
(out_dir / ".nojekyll").write_text("", encoding="utf-8")
print(f"APT repo generated at: {out_dir}")
PYEOF

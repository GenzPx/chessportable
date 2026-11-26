#!/usr/bin/env sh
set -e

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
PKG_NAME="chessportable"
PKG_VERSION="$(python3 -c "import re; print(re.search(r'__version__\s*=\s*\"([^\"]+)\"', open('${ROOT_DIR}/chessportable/__init__.py').read()).group(1))")"
PKG_ARCH="all"
TERMUX_PREFIX="data/data/com.termux/files/usr"
OUT_DEB="${ROOT_DIR}/${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"

STAGE_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGE_DIR"' EXIT
chmod 0755 "$STAGE_DIR"

mkdir -p "$STAGE_DIR/DEBIAN"
mkdir -p "$STAGE_DIR/$TERMUX_PREFIX/bin"
mkdir -p "$STAGE_DIR/$TERMUX_PREFIX/lib/chessportable"

cp -R "$ROOT_DIR/chessportable" "$STAGE_DIR/$TERMUX_PREFIX/lib/chessportable/chessportable"
find "$STAGE_DIR/$TERMUX_PREFIX/lib/chessportable" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGE_DIR/$TERMUX_PREFIX/lib/chessportable" -name "*.pyc" -delete 2>/dev/null || true
chmod -R a+rX "$STAGE_DIR/$TERMUX_PREFIX/lib/chessportable"

cat > "$STAGE_DIR/$TERMUX_PREFIX/bin/chessportable" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
export PYTHONPATH="/data/data/com.termux/files/usr/lib/chessportable${PYTHONPATH:+:$PYTHONPATH}"
if command -v python3 >/dev/null 2>&1; then
    exec python3 -m chessportable "$@"
else
    exec python -m chessportable "$@"
fi
EOF
chmod 0755 "$STAGE_DIR/$TERMUX_PREFIX/bin/chessportable"

INSTALLED_SIZE=$(du -sk "$STAGE_DIR/$TERMUX_PREFIX" | awk '{print $1}')

cat > "$STAGE_DIR/DEBIAN/control" <<EOF
Package: ${PKG_NAME}
Version: ${PKG_VERSION}
Architecture: ${PKG_ARCH}
Maintainer: GenzPX <GenzPx@users.noreply.github.com>
Homepage: https://github.com/GenzPx/chessportable
Depends: python
Section: games
Priority: optional
Installed-Size: ${INSTALLED_SIZE}
Description: ChessPortable CLI chess for Termux by GenzPX
 ChessPortable v${PKG_VERSION} ("Apex Evolution") by GenzPX is a pure-Python
 terminal chess game for Termux. Includes 10 bots (Starrys 150 to Jim 4000),
 Global ('A') and Per-Bot Adaptive ('A 0'..'A 9'), ARC auto-sequence mode,
 85+ ECO opening detector, Tactical Coach with PV, post-game move review,
 Gauntlet Boss Rush, 20 Puzzles, 2-Player mode, 6 themes, clocks, and PGN.
EOF
chmod 0644 "$STAGE_DIR/DEBIAN/control"

if dpkg-deb --help 2>&1 | grep -q -- "--root-owner-group"; then
    dpkg-deb -Zgzip --root-owner-group --build "$STAGE_DIR" "$OUT_DEB"
else
    dpkg-deb -Zgzip --build "$STAGE_DIR" "$OUT_DEB"
fi

echo ""
echo "Berhasil bikin paket Termux: $OUT_DEB"
echo "Install di Termux dengan: pkg install ./${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"

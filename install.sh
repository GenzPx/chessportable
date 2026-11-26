#!/usr/bin/env sh
set -e

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if [ -n "${PREFIX:-}" ] && [ -d "$PREFIX/bin" ]; then
    TARGET_PREFIX="$PREFIX"
    if [ -x "$PREFIX/bin/sh" ]; then
        SH_BIN="$PREFIX/bin/sh"
    else
        SH_BIN="/usr/bin/env sh"
    fi
else
    TARGET_PREFIX="${HOME}/.local"
    SH_BIN="/usr/bin/env sh"
fi

BIN_DIR="${TARGET_PREFIX}/bin"
LIB_DIR="${TARGET_PREFIX}/lib/chessportable"

echo "Installing ChessPortable by GenzPX to ${TARGET_PREFIX}..."
mkdir -p "$BIN_DIR" "$LIB_DIR"

rm -rf "$LIB_DIR/chessportable"
cp -R "$SCRIPT_DIR/chessportable" "$LIB_DIR/chessportable"
find "$LIB_DIR/chessportable" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

cat > "$BIN_DIR/chessportable" <<EOF
#!${SH_BIN}
export PYTHONPATH="${LIB_DIR}\${PYTHONPATH:+:\$PYTHONPATH}"
if command -v python3 >/dev/null 2>&1; then
    exec python3 -m chessportable "\$@"
else
    exec python -m chessportable "\$@"
fi
EOF
chmod 0755 "$BIN_DIR/chessportable"

echo ""
echo "Selesai! ChessPortable berhasil di-install."
echo "Jalankan langsung dengan: chessportable"
if [ -z "${PREFIX:-}" ]; then
    echo "(Pastikan ${BIN_DIR} ada di PATH kamu)"
fi

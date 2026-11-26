TERMUX_PKG_HOMEPAGE=https://github.com/GenzPx/chessportable
TERMUX_PKG_DESCRIPTION="ChessPortable CLI chess for Termux by GenzPX"
TERMUX_PKG_LICENSE="MIT"
TERMUX_PKG_MAINTAINER="@GenzPx"
TERMUX_PKG_VERSION="3.0.0"
TERMUX_PKG_SRCURL="https://github.com/GenzPx/chessportable/archive/refs/tags/v${TERMUX_PKG_VERSION}.tar.gz"
TERMUX_PKG_SHA256=""
TERMUX_PKG_DEPENDS="python"
TERMUX_PKG_PLATFORM_INDEPENDENT=true
TERMUX_PKG_BUILD_IN_SRC=true

termux_step_make_install() {
    mkdir -p "${TERMUX_PREFIX}/lib/chessportable"
    cp -R "${TERMUX_PKG_SRCDIR}/chessportable" "${TERMUX_PREFIX}/lib/chessportable/chessportable"

    cat > "${TERMUX_PREFIX}/bin/chessportable" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
export PYTHONPATH="/data/data/com.termux/files/usr/lib/chessportable${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m chessportable "$@"
EOF
    chmod 0755 "${TERMUX_PREFIX}/bin/chessportable"
}

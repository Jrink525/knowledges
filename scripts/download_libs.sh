#!/bin/bash
# Download missing shared libraries for Chromium
cd /home/node/.openclaw/workspace

declare -A MISSING_LIBS
MISSING_LIBS=(
    ["libx11-6"]="libx/libx11:1.8.4-2+deb12u3"
    ["libxcomposite1"]="libx/libxcomposite:0.4.5-1"
    ["libxdamage1"]="libx/libxdamage:1.1.5-2"
    ["libxext6"]="libx/libxext:1.3.4-1+b1"
    ["libxfixes3"]="libx/libxfixes:6.0.0-2"
    ["libxrandr2"]="libx/libxrandr:1.5.2-2+b1"
    ["libasound2"]="alsa/alsa-lib:1.2.8-1"
    ["libatk1.0-0"]="atk/atk1.0:2.46.0-5"
    ["libatk-bridge2.0-0"]="at-spi2-atk:2.46.0-5"
    ["libatspi2.0-0"]="at-spi2-core:2.46.0-5"
    ["libcairo2"]="cairo:1.16.0-7"
    ["libcups2"]="cups:2.4.2-3+deb12u9"
    ["libdbus-1-3"]="dbus:1.14.10-1+deb12u1"
    ["libgbm1"]="mesa:22.3.6-1+deb12u1"
    ["libpango-1.0-0"]="pango:1.50.12+ds-1"
    ["libxcb1"]="libx/libxcb:1.15-1"
    ["libxkbcommon0"]="libx/libxkbcommon:1.5.0-1"
    ["libsqlite3-0"]="sqlite3:3.40.1-2+deb12u2"
    ["libpixman-1-0"]="pixman:0.42.2-1"
    ["libfontconfig1"]="fontconfig:2.14.1-4"
    ["libfreetype6"]="freetype:2.12.1+dfsg-5"
    ["libdatrie1"]="datrie:0.2.13-2+b1"
    ["libthai0"]="thai:0.1.29-2"
    ["libharfbuzz0b"]="harfbuzz:7.0.0-2"
    ["libfribidi0"]="fribidi:1.0.8-2+deb12u1"
    ["libxrender1"]="libx/libxrender:0.9.10-1.1"
    ["libpng16-16"]="libpng:1.6.39-2"
    ["libzstd1"]="zstd:1.5.4+dfsg2-5"
    ["liblzma5"]="xz-utils:5.4.1-0.2"
    ["libbrotli1"]="brotli:1.0.9-2+b6"
    ["libexpat1"]="expat:2.5.0-1+deb12u1"
    ["libgraphite2-3"]="graphite2:1.3.14-1"
    ["libselinux1"]="libselinux:3.5-2"
    ["libegl1"]="egl:1.5.0-1"
    ["libwayland-client0"]="wayland:1.21.0-1"
    ["libdrm2"]="drm:2.4.114-1+b1"
    ["libxshmfence1"]="libxshmfence:1.3-1"
    ["libxxf86vm1"]="libx/libxxf86vm:1.1.4-1+b2"
    ["libxcb-dri2-0"]="libx/libxcb:1.15-1"
    ["libxcb-dri3-0"]="libx/libxcb:1.15-1"
    ["libxcb-present0"]="libx/libxcb:1.15-1"
    ["libxcb-sync1"]="libx/libxcb:1.15-1"
)

for pkg in "${!MISSING_LIBS[@]}"; do
    val="${MISSING_LIBS[$pkg]}"
    path="${val%%:*}"
    ver="${val##*:}"
    
    url="http://deb.debian.org/debian/pool/main/${path}/${pkg}_${ver}_amd64.deb"
    status=$(curl -sL -o "${pkg}.deb" "$url" -w "%{http_code}" 2>&1)
    
    if [ "$status" != "200" ]; then
        # Try with deb12u suffix
        for v in "${ver}+deb12u1" "${ver}+deb12u2" "${ver}+deb12u3"; do
            url2="http://deb.debian.org/debian/pool/main/${path}/${pkg}_${v}_amd64.deb"
            status=$(curl -sL -o "${pkg}.deb" "$url2" -w "%{http_code}" 2>&1)
            if [ "$status" == "200" ]; then break; fi
        done
    fi
    
    if [ "$status" != "200" ]; then
        rm -f "${pkg}.deb"
        echo "FAIL: $pkg"
    else
        size=$(stat -c%s "${pkg}.deb" 2>/dev/null || echo 0)
        echo "OK: $pkg ($size bytes)"
    fi
done

echo "=== Download summary ==="
ls -la *.deb 2>/dev/null | grep -v ' 300 ' | wc -l
echo "debs downloaded successfully"

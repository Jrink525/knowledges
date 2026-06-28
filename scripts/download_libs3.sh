#!/bin/bash
# Second batch - correct pool paths
cd /home/node/.openclaw/workspace

# Format: deb_filename:pool_path (relative to pool/main/)
# For package names like "libcairo2" the pool is under "c/" because the SOURCE pkg is "cairo"
# The rule is: pool/main/<first_letter>/<source_pkg_name>/

DEBS=(
    "libx11-6_1.8.4-2+deb12u2_amd64.deb:libx/libx11"
    "libasound2_1.2.8-1+b1_amd64.deb:a/alsa-lib"
    "libasound2-data_1.2.8-1_all.deb:a/alsa-lib"
    "libcups2_2.4.2-3+deb12u9_amd64.deb:c/cups"
    "libcups2-common_2.4.2-3+deb12u9_all.deb:c/cups"
    "libdbus-1-3_1.14.10-1~deb12u1_amd64.deb:d/dbus"
    "libcairo2_1.16.0-7_amd64.deb:c/cairo"
    "libfontconfig1_2.14.1-4_amd64.deb:f/fontconfig"
    "libfontconfig-common_2.14.1-4_all.deb:f/fontconfig"
    "libpango-1.0-0_1.50.12+ds-1_amd64.deb:p/pango"
    "libpangoft2-1.0-0_1.50.12+ds-1_amd64.deb:p/pango"
    "libpangocairo-1.0-0_1.50.12+ds-1_amd64.deb:p/pango"
    "libatk1.0-0_2.46.0-5_amd64.deb:a/atk1.0"
    "libatk1.0-data_2.46.0-5_all.deb:a/atk1.0"
    "libharfbuzz0b_7.0.0-2_amd64.deb:h/harfbuzz"
    "libfreetype6_2.12.1+dfsg-5+deb12u4_amd64.deb:f/freetype"
    "libpixman-1-0_0.42.2-1_amd64.deb:p/pixman"
    "libexpat1_2.5.0-1+deb12u2_amd64.deb:e/expat"
    "libpng16-16_1.6.39-2_amd64.deb:libp/libpng"
    "libbrotli1_1.0.9-2+b6_amd64.deb:b/brotli"
    "libzstd1_1.5.4+dfsg2-5_amd64.deb:z/zstd"
    "libgraphite2-3_1.3.14-1_amd64.deb:g/graphite2"
    "libgbm1_22.3.6-1+deb12u1_amd64.deb:m/mesa"
    "libdrm2_2.4.114-1+b1_amd64.deb:d/drm"
    "libwayland-client0_1.21.0-1_amd64.deb:w/wayland"
    "libselinux1_3.4-1+b6_amd64.deb:libs/libselinux"
    "libfribidi0_1.0.8-2.1_amd64.deb:f/fribidi"
    "libdatrie1_0.2.13-2+b1_amd64.deb:d/datrie"
    "libthai0_0.1.29-2_amd64.deb:t/thai"
    "libthai-data_0.1.29-2_all.deb:t/thai"
    "liblzma5_5.4.1-0.2_amd64.deb:x/xz-utils"
    "libxshmfence1_1.3-1_amd64.deb:libx/libxshmfence"
    "libegl1_1.5.0-1_amd64.deb:e/egl"
    "libegl-mesa0_22.3.6-1+deb12u1_amd64.deb:m/mesa"
    "libgl1-mesa-dri_22.3.6-1+deb12u1_amd64.deb:m/mesa"
    "libglapi-mesa_22.3.6-1+deb12u1_amd64.deb:m/mesa"
    "libxcb-glx0_1.15-1_amd64.deb:libx/libxcb"
    "libx11-xcb1_1.8.4-2+deb12u2_amd64.deb:libx/libx11"
)

for entry in "${DEBS[@]}"; do
    IFS=':' read -r debname path <<< "$entry"
    url="http://deb.debian.org/debian/pool/main/${path}/${debname}"
    status=$(curl -sL -o "$debname" "$url" -w "%{http_code}" 2>&1)
    if [ "$status" = "200" ]; then
        echo "OK: $debname"
    else
        rm -f "$debname"
        echo "FAIL: $debname"
    fi
done

echo "=== Summary ==="
ls -la *.deb 2>/dev/null | grep -v ' 300 ' | wc -l
echo "debs available"
ls -la *.deb 2>/dev/null | grep -v ' 300 '

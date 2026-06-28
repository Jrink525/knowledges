#!/bin/bash
cd /home/node/.openclaw/workspace

MORE_DEBS="
libXau6:libx/libxau:1.0.9-1
libXdmcp6:libx/libxdmcp:1.1.2-3
libatk1.0-0:a/atk1.0:2.46.0-5
libatk-bridge2.0-0:a/at-spi2-atk:2.46.0-5
libatspi2.0-0:a/at-spi2-core:2.46.0-5
libavahi-client3:avahi:0.8-10+deb12u1
libavahi-common3:avahi:0.8-10+deb12u1
libdrm2:d/drm:2.4.114-1+b1
libpango-1.0-0:p/pango:1.50.12+ds-1
libpng16-16:libp/libpng:1.6.39-2
libwayland-server0:w/wayland:1.21.0-1
libxcb-render0:libx/libxcb:1.15-1
libxcb-shm0:libx/libxcb:1.15-1
libpangoft2-1.0-0:p/pango:1.50.12+ds-1
libpangocairo-1.0-0:p/pango:1.50.12+ds-1
"

while IFS=: read -r pkg path ver; do
    [ -z "$pkg" ] && continue
    url="http://deb.debian.org/debian/pool/main/${path}/${pkg}_${ver}_amd64.deb"
    status=$(curl -sL -o "${pkg}.deb" "$url" -w "%{http_code}" 2>&1)
    if [ "$status" != "200" ]; then
        for v in "${ver}+deb12u1" "${ver}+deb12u2" "${ver}+deb12u3" "${ver}+deb12u4"; do
            url2="http://deb.debian.org/debian/pool/main/${path}/${pkg}_${v}_amd64.deb"
            status=$(curl -sL -o "${pkg}.deb" "$url2" -w "%{http_code}" 2>&1)
            [ "$status" = "200" ] && break
        done
    fi
    if [ "$status" = "200" ]; then
        echo "OK: $pkg"
    else
        rm -f "${pkg}.deb"
        echo "FAIL: $pkg"
    fi
done <<< "$MORE_DEBS"

echo "=== Summary ==="
ls -la *.deb 2>/dev/null | grep -v ' 300 ' | wc -l
echo "debs"

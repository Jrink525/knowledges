#!/usr/bin/env python3
"""Download and extract missing shared libraries for chromium."""
import os, json, urllib.request, zipfile
from html.parser import HTMLParser

WORKSPACE = '/home/node/.openclaw/workspace'
LIBDIR = os.path.join(WORKSPACE, 'libs')
os.makedirs(LIBDIR, exist_ok=True)

# Look at which specific libs we're missing
# We'll use a simple approach: for each missing lib, find it via snapshot.d.o
# But first - let's just extract the .so files from the debs we already have

def extract_deb(deb_path, target_dir):
    """Extract .deb (ar archive) and get the data.tar.*"""
    import subprocess, tarfile
    # A .deb is an ar archive. We can use Python's ar support via extracting with subprocess
    # Actually .deb = ar archive containing: debian-binary, control.tar.*, data.tar.*
    
    # Use python to process ar format manually (simple case)
    with open(deb_path, 'rb') as f:
        data = bytearray(f.read())
    
    # Find ar file entries
    idx = 0
    entries = {}
    while idx < len(data):
        if chr(data[idx]) != '!':
            break
        # ar header: name (16), timestamp (12), owner (6), group (6), mode (8), size (10) + `\n`
        name = data[idx:idx+16].rstrip().decode('ascii', errors='replace')
        sz_str = data[idx+48:idx+58].rstrip()
        try:
            sz = int(sz_str)
        except:
            break
        content_start = idx + 60
        content = data[content_start:content_start+sz]
        entries[name] = content
        idx = content_start + sz
        # align to 2
        if idx % 2 != 0:
            idx += 1
    
    # Find data.tar
    data_tar = None
    for name, content in entries.items():
        if name.startswith('data.tar.'):
            data_tar = content
            break
    
    if not data_tar:
        print(f"  No data.tar found in {deb_path}")
        return []
    
    extracted = []
    with tarfile.open(fileobj=type('BytesIO', (), {'read': lambda s: data_tar})(), mode='r:*') as tar:
        for member in tar:
            if member.name.endswith('.so') or member.name.endswith('.so.0') or '.so.' in member.name:
                member_path = os.path.join(target_dir, os.path.basename(member.name))
                if not os.path.exists(member_path):
                    with open(member_path, 'wb') as f:
                        f.write(tar.extractfile(member).read())
                    os.chmod(member_path, 0o755)
                    extracted.append(member_path)
                    print(f"  Extracted: {os.path.basename(member.name)}")
    
    return extracted

# Extract from downloaded debs
deb_dir = WORKSPACE
deb_files = [f for f in os.listdir(deb_dir) if f.endswith('.deb') and os.path.getsize(os.path.join(deb_dir, f)) > 1000]
print(f"Found {len(deb_files)} valid debs")

all_extracted = []
for deb_file in deb_files:
    deb_path = os.path.join(deb_dir, deb_file)
    size_kb = os.path.getsize(deb_path) / 1024
    print(f"Processing {deb_file} ({size_kb:.0f} KB)...")
    extracted = extract_deb(deb_path, LIBDIR)
    all_extracted.extend(extracted)
    # Remove the deb
    os.remove(deb_path)

print(f"\nExtracted {len(all_extracted)} shared libraries to {LIBDIR}")
for lib in sorted(all_extracted):
    print(f"  {os.path.basename(lib)}")

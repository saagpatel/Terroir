#!/usr/bin/env bash
# Locked, synthetic-only Python/FlatBuffers setup; no geographic downloads.
set -euo pipefail
pipeline_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
command -v uv >/dev/null || { echo 'Install uv to use the locked pipeline setup.' >&2; exit 1; }
python_bin=${TERROIR_PYTHON:-python3.12}
"$python_bin" -c 'import sys; assert sys.version_info[:2] == (3, 12), "Python 3.12 required"'
if [[ ! -x "$pipeline_dir/venv/bin/python" ]]; then
    uv venv --python "$python_bin" "$pipeline_dir/venv"
fi
"$pipeline_dir/venv/bin/python" -c 'import sys; assert sys.version_info[:2] == (3, 12), "Existing venv must use Python 3.12"'
uv pip sync --python "$pipeline_dir/venv/bin/python" --require-hashes "$pipeline_dir/requirements.lock"
"$pipeline_dir/venv/bin/python" - "$pipeline_dir" <<'PY'
import hashlib
import io
import os
from pathlib import Path
import platform
import subprocess
import sys
import urllib.request
import zipfile

root = Path(sys.argv[1])
version = '25.12.19'
assets = {
    ('Linux', 'x86_64'): ('Linux.flatc.binary.g%2B%2B-13.zip', '9f87066dc5dfa7fe02090b55bab5f3e55df03e32c9b0cdf229004ade7d091039'),
    ('Darwin', 'arm64'): ('Mac.flatc.binary.zip', '9340a5f9900b95e34ccadcb06bceec91180cc8b83098d5e966ed6d8d590cbba2'),
    ('Darwin', 'x86_64'): ('MacIntel.flatc.binary.zip', 'b1b0c5bd2b4a19282d461e5ba725f41399af23ef42f4277605b75148996f2f4b'),
}
key = (platform.system(), platform.machine())
if key not in assets:
    raise SystemExit(f'No pinned flatc asset configured for {key}; do not substitute a compiler.')
asset, digest = assets[key]
cache = root / '.tools' / f'flatc-{version}-{key[0]}-{key[1]}.zip'
cache.parent.mkdir(parents=True, exist_ok=True)
if not cache.exists():
    url = f'https://github.com/google/flatbuffers/releases/download/v{version}/{asset}'
    with urllib.request.urlopen(url) as response:
        payload = response.read()
    if hashlib.sha256(payload).hexdigest() != digest:
        raise SystemExit('flatc download checksum mismatch')
    temporary = cache.with_suffix('.tmp')
    temporary.write_bytes(payload)
    temporary.replace(cache)
payload = cache.read_bytes()
if hashlib.sha256(payload).hexdigest() != digest:
    raise SystemExit('Cached flatc checksum mismatch; inspect/remove only this invalid cache file.')
with zipfile.ZipFile(io.BytesIO(payload)) as archive:
    binary = archive.read('flatc')
target = root / 'venv' / 'bin' / 'flatc'
if not target.exists() or target.read_bytes() != binary:
    target.write_bytes(binary)
    target.chmod(0o755)
actual = subprocess.check_output([target, '--version'], text=True).strip()
if actual != f'flatc version {version}':
    raise SystemExit(f'Unexpected compiler: {actual}')
print(actual)
print(f'Verified release asset SHA-256: {digest}')
PY
printf 'Activate with: source %s/venv/bin/activate\n' "$pipeline_dir"

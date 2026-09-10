"""Recover only known EFB source identities for layered patch regressions."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

def without_dispatch_overlay(source):
    identity = hashlib.sha256(source).hexdigest()
    if identity in ('661ffe6c2b64b12090d0d181c279ec7d12e53cce309822e481f22796dc132a77',
                    '9164b11a36e898f4e2ee479b975c751deb2752f2b27047d610feb0290197405f'):
        return source
    root = Path(__file__).resolve().parents[1]
    patch = root/'patches/experiments/efb-dispatch-timing.patch'
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == '5226881b8ce0f00b0b2673b68f40040fa4490771d170aade1289db00ae19b638'
    with tempfile.TemporaryDirectory(prefix='galaxypad-efb-source-') as directory:
        folder = Path(directory)
        target = folder/'Source/Core/VideoCommon/EFBInterface.cpp'
        target.parent.mkdir(parents=True)
        target.write_bytes(source)
        header = folder/'Source/Core/Common/GalaxyPadEFBDispatchTiming.h'
        header.parent.mkdir(parents=True)
        header.write_bytes((root/'patches/experiments/efb-dispatch-timing.h').read_bytes())
        subprocess.run(['git', 'apply', '--reverse', str(patch)], cwd=folder, check=True, capture_output=True)
        result = target.read_bytes()
        assert hashlib.sha256(result).hexdigest() == '9164b11a36e898f4e2ee479b975c751deb2752f2b27047d610feb0290197405f', 'unknown EFB source'
        subprocess.run(['git', 'apply', str(patch)], cwd=folder, check=True, capture_output=True)
        assert target.read_bytes() == source
        return result

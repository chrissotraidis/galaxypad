#!/usr/bin/env python3
"""Copy the mixer with configured, running-state gap filling restored for Apple DMA.

This creates an unselected experiment only. Existing granule replay/fading,
startup reserve, adaptive rate, diagnostics, and paused/disabled behavior remain.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'ref/ModernGekko/vendor/dolphin/Source/Core/AudioCommon'
OLD = '''    // Preserve the true queue position on Apple platforms so the adaptive rate
    // above can recover. Rewinding into old granules makes music sound selectively
    // muted as Dolphin's gap filler repeatedly fades the replayed data.
    if (this == &m_mixer->m_dma_mixer)
'''
NEW = '''    // Honor configured gap filling during emulation. Keep silence and the
    // startup reserve when replay is disabled or the core is not running.
    if (this == &m_mixer->m_dma_mixer &&
        !(m_mixer->m_config_fill_audio_gaps && is_running))
'''


def candidate(original):
    if original.count(OLD) != 1:
        raise ValueError('Unknown Apple DMA underrun branch; review source first')
    return original.replace(OLD, NEW)


def create(output):
    output = output.resolve()
    if output.exists() or SOURCE == output or SOURCE in output.parents:
        raise ValueError('Output must be a new directory outside canonical source')
    original = (SOURCE / 'Mixer.cpp').read_text()
    changed = candidate(original)
    output.mkdir(parents=True)
    (output / 'Mixer.cpp').write_text(changed)
    (output / 'Mixer.h').write_bytes((SOURCE / 'Mixer.h').read_bytes())
    patch = ''.join(difflib.unified_diff(original.splitlines(True), changed.splitlines(True),
        fromfile='a/Source/Core/AudioCommon/Mixer.cpp',
        tofile='b/Source/Core/AudioCommon/Mixer.cpp'))
    (output / 'audio-gap-fill.patch').write_text(patch)
    manifest = {'selected': False, 'source': str(SOURCE),
        'source_sha256': hashlib.sha256(original.encode()).hexdigest(),
        'candidate_sha256': hashlib.sha256(changed.encode()).hexdigest(),
        'change': 'Apple DMA defers to existing gap filler only when enabled and running'}
    (output / 'provenance.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(create(parser.parse_args().output), indent=2))

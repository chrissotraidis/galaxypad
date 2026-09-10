#!/usr/bin/env python3
"""Prepare an isolated VI-header overlay, never modify the vendor/product tree."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]

def transform(source, capacity=16384):
    if capacity not in (16384,65536):
        raise ValueError('Private capacity must be 16384 or 65536')
    edits = [
        ('  using Buffer = ViTimingBuffer<>;',
         '#ifdef GALAXYPAD_PRIVATE_THREAD_WORK\n'
         f'  static constexpr std::size_t kWorkCapacity = {capacity};\n'
         '  using Buffer = ViTimingBuffer<kWorkCapacity>;\n#else\n'
         '  using Buffer = ViTimingBuffer<>;\n#endif'),
        ('#include "vi-timing-buffer.h"', '#include "vi-timing-buffer.h"\n'
         '#ifdef GALAXYPAD_PRIVATE_THREAD_WORK\n#include "thread-work-recorder.h"\n#endif'),
        ('    result_ = Result::Disabled;', '    result_ = Result::Disabled;\n'
         '#ifdef GALAXYPAD_PRIVATE_THREAD_WORK\n'
         '    work_.ConfigureApple(path_.empty() ? nullptr : std::getenv("GALAXYPAD_THREAD_WORK_TIMING"));\n#endif'),
        ('    const auto sample = clock();', '    const auto sample = clock();\n'
         '#ifdef GALAXYPAD_PRIVATE_THREAD_WORK\n    work_.Record(sample.wall_ns);\n#endif'),
        ('    finished_ = true;', '    finished_ = true;\n'
         '#ifdef GALAXYPAD_PRIVATE_THREAD_WORK\n'
         '    const auto work_result = work_.FlushAfterJoin();\n'
         '    if (work_result != ThreadWorkRecorder<kWorkCapacity>::Result::Disabled)\n'
         '      std::fprintf(stderr, "[galaxypad] thread-work export_result=%d\\n", static_cast<int>(work_result));\n#endif'),
        ('  std::unique_ptr<Buffer> buffer_;', '#ifdef GALAXYPAD_PRIVATE_THREAD_WORK\n'
         '  ThreadWorkRecorder<kWorkCapacity> work_;\n#endif\n  std::unique_ptr<Buffer> buffer_;'),
    ]
    for before, after in edits:
        if source.count(before) != 1:
            raise ValueError(f'VI recorder anchor missing or ambiguous: {before}')
        source = source.replace(before, after)
    return source

def prepare(output, capacity=16384):
    canonical = ROOT/'patches/experiments'
    source = (canonical/'vi-timing-recorder.h').read_text()
    if source != (ROOT/'ref/ModernGekko/src/runtime/vi-timing-recorder.h').read_text():
        raise ValueError('Canonical/vendor recorder mismatch')
    transformed = transform(source, capacity)
    output.mkdir(parents=True, exist_ok=False)
    # Mechanical copy/overlay into an explicitly new private directory only.
    (output/'vi-timing-recorder.h').write_text(transformed)
    for name in ('vi-timing-buffer.h','thread-work-recorder.h'):
        shutil.copyfile(canonical/name,output/name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    prepare(parser.parse_args().output.resolve())

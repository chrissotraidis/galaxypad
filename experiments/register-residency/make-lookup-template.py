#!/usr/bin/env python3
"""Copy the pinned module template and route its void dispatch through gp_find_original."""
from pathlib import Path
import argparse, shutil
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--runtime', type=Path, required=True, help='Pinned RecompCore checkout (vendor/dolphin)')
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
here = Path(__file__).resolve().parent
shutil.copytree(a.runtime/'module-template', a.output)
shutil.copy(here/'gp_lookup.h', a.output/'gp_lookup.h')
f = a.output/'module_export.c'; s = f.read_text()
s = s.replace('#include "StaticRecompABI.h"\n', '#include "StaticRecompABI.h"\n#include "gp_lookup.h"\n', 1)
start = s.index('RECOMP_MODULE_EXPORT void staticrecomp_dispatch_void_v1'); end = s.index('#endif', start)
body = s[start:end]; assert body.count('dolrecomp_find_original(') == 2
f.write_text(s[:start] + body.replace('dolrecomp_find_original(', 'gp_find_original(') + s[end:])
print('template ready:', a.output)

#!/usr/bin/env python3
"""Validate the staged standalone probe, not Galaxy runtime acceptance."""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import tempfile

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('build',type=Path)
args=parser.parse_args();build=args.build.resolve()
environment=os.environ.copy();environment.pop('GALAXYPAD_LLVM_ARM64_PROBE',None)
with tempfile.TemporaryDirectory(prefix='galaxypad-arm64-emission-') as directory:
    temp=Path(directory);obj=temp/'probe.o';ir=temp/'probe.ll'
    command=[str(build/'test_llvm_backend'),str(obj),str(ir)]
    rejected=subprocess.run(command,env=environment,text=True,capture_output=True)
    assert rejected.returncode!=0
    assert 'supported production targets' in rejected.stderr
    assert not obj.exists() and not ir.exists()
    environment['GALAXYPAD_LLVM_ARM64_PROBE']='1'
    emitted=subprocess.run(command,env=environment,text=True,capture_output=True,check=True)
    assert 'probe refuses cross-chunk range tables' in emitted.stderr
    object_kind=subprocess.check_output(['file',str(obj)],text=True)
    assert 'Mach-O 64-bit object arm64' in object_kind
    text=ir.read_text()
    calls=0
    for function,body in re.findall(r'define[^\n]*@(func_\w+)\([^\n]*\{\n(.*?)\n\}',text,re.S):
        targets=re.findall(r'call void @(func_\w+_budget)\(',body)
        for target in targets:
            assert not function.endswith('_budget'),(function,target)
            assert target==function+'_budget',(function,target)
            calls+=1
    assert calls>0,'No wrappers found; IR parser or emission changed'
    declarations=[line for line in text.splitlines() if line.startswith('declare ') and '@ppc_mfspr(' in line]
    assert len(declarations)==1 and re.search(r'i16\s+zeroext',declarations[0])
    executed=subprocess.run([str(build/'test_llvm_execute')],text=True,capture_output=True,check=True)
    print(json.dumps({'opt_in_rejection':'pass','range_table_rejection':'pass',
      'object':'ARM64 Mach-O','wrapper_calls':calls,'cross_chunk_budget_calls':0,
      'mfspr_unsigned_abi':'pass','standalone_execution':'pass',
      'execution_output':executed.stdout+executed.stderr,
      'boundary':'Synthetic standalone CPU tests only; no Galaxy/chassis compatibility or performance claim.'},indent=2))

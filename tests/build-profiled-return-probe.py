"""Build isolated native objects from audited profiled IR; not installed ThinLTO.

Rename the control symbol only AFTER profile application, preserving its
instruction/profile metadata. Never change the actual module or training data.
"""
from pathlib import Path
import hashlib
import json
import subprocess

root=Path(__file__).resolve().parents[1]
audit=root/'generated/return-selector-profile-r445'
report=json.loads((audit/'report.json').read_text())
assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha for path,sha in report['inputs'].items())
assert all(v['function_entry_count']==65272501 for v in report['variants'].values())
out=root/'generated/profiled-return-r446';out.mkdir(exist_ok=False)
result={'guest_start':'0x804b60a0','instructions':1024,'candidate_label':'C-profiled-selector','objects':{},
 'audit_sha256':hashlib.sha256((audit/'report.json').read_bytes()).hexdigest(),
 'boundary':'Profiled IR lowered separately; not the installed ThinLTO link or captured gameplay-state distribution.'}
for variant,name in (('control','c'),('candidate','ir')):
 ir=(audit/variant/'chunk.ll').read_text()
 assert ir.count('@func_804B60A0(')==1
 if variant=='control':ir=ir.replace('@func_804B60A0(','@c_func_804B60A0(')
 path=out/(name+'.ll');path.write_text(ir)
 subprocess.run(['/usr/bin/clang','-O2','-c','-x','ir',str(path),'-o',str(out/(name+'.o'))],check=True)
 obj=out/(name+'.o')
 result['objects'][name]={'bytes':obj.stat().st_size,'sha256':hashlib.sha256(obj.read_bytes()).hexdigest()}
(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

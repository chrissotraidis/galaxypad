"""Execute the actual audit policy block on private synthetic artifacts."""
import os
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
audit=(root/'scripts/audit-module.sh').read_text()
block=audit.split('# Older accepted manifests predate this policy.',1)[1].split('\nfile "$module"',1)[0]
block='# Older accepted manifests predate this policy.'+block
header=(root/'generated/two-range-r358/candidate/RMGE01.h').read_bytes()
with tempfile.TemporaryDirectory(prefix='galaxypad-policy-audit-') as temporary:
    temp=Path(temporary);chunks=temp/'chunks';chunks.mkdir()
    manifest=temp/'manifest.txt'
    def run(policy, expected, size='1024', lookup='indexed', content=header, normalized=header):
        manifest.write_text(policy)
        (temp/'RMGE01.h').write_bytes(content)
        (temp/'generated.h').write_bytes(normalized)
        result=subprocess.run(['bash','-c','set -euo pipefail\n'+block],
            env={**os.environ,'manifest':str(manifest),'chunks_dir':str(chunks),
                 'chunk_instructions':size,'dispatch_lookup':lookup},capture_output=True,text=True)
        assert (result.returncode==0)==expected, result.stderr+result.stdout
    run('',True)
    run('two_range_policy=none\n',True)
    declared='two_range_policy=rmge01-two-range-v1\n'
    run(declared,True)
    run('two_range_policy=unknown\n',False)
    run(declared+declared,False)
    run(declared,False,size='512')
    run(declared,False,lookup='linear')
    run(declared,False,content=header+b'changed')
    run(declared,False,normalized=header+b'changed')
print('Actual audit accepts legacy/exact policy and rejects unknown/duplicate/settings/header/normalized mismatch')

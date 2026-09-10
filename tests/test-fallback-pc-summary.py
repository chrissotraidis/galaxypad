from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
summarize = runpy.run_path(str(root/'scripts/summarize-fallback-pcs.py'))['summarize']
header = '[galaxypad-fallback-pcs] total=5 dropped=1\n'
site = '[galaxypad-fallback-pc] pc=80000500 path=0 count=4\n'
end = '[staticrecomp] shutdown: native=1 fallback=4\n'
valid = header + site + end
result = summarize(valid)
assert result['recorded'] == 4 and result['dropped'] == 1
assert result['paths']['uncovered'] == 4 and not result['complete_pc_coverage']
assert summarize(header.replace('5 dropped=1', '4 dropped=0') + site + end)['complete_pc_coverage']
for invalid in ('', header, header+site, valid+valid, header+site+site+end,
                header+site.replace('path=0', 'path=9')+end,
                header+site.replace('count=4', 'count=0')+end,
                header+site.replace('count=4', 'count=3')+end,
                site+header+end):
    try:
        summarize(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('accepted invalid census')
print('fallback summary: valid/lossy/complete and nine rejection cases pass')

"""Synthetic id/ref and exclusive-leaf regression for the offline profiler tool."""
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('summary', root/'scripts/summarize-cpu-profile.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
xml = ET.fromstring('''<trace-query-result>
<row><thread id="1" fmt="CPU thread (test)"/><core id="2" fmt="P Core"/>
<cycle-weight id="3">10</cycle-weight><tagged-backtrace id="4"><backtrace id="5">
<frame id="6" name="leaf" addr="0x1021"><binary id="7" name="gRMGE01_recomp.dylib" load-addr="0x1000"/></frame>
<frame name="parent" addr="0x1050"><binary ref="7"/></frame>
</backtrace></tagged-backtrace></row>
<row><thread ref="1"/><core ref="2"/><cycle-weight ref="3"/><tagged-backtrace ref="4"/></row>
<row><thread ref="1"/><core ref="2"/><cycle-weight>0</cycle-weight>
<tagged-backtrace><backtrace><frame ref="6"/></backtrace></tagged-backtrace></row>
<row><thread fmt="Main Thread"/></row>
</trace-query-result>''')
result = module.summarize(xml, [('hit', 0x20, 0x24), ('miss', 0x24, 0x28)])
assert result['samples'] == 3 and result['cycles'] == 20
assert result['leaves'] == [dict(name='leaf', samples=3, cycles=20)]
assert result['addresses'] == [dict(name='leaf', raw_offset='0x21', samples=3, cycles=20)]
assert result['ranges'][0]['samples'] == 3 and result['ranges'][1]['samples'] == 0
runner_xml = ET.fromstring('''<trace-query-result>
<row><thread fmt="CPU thread (test)"/><core fmt="P Core"/><cycle-weight>7</cycle-weight>
<tagged-backtrace><backtrace><frame name="run" addr="0x9023">
<binary name="GalaxyPadRunner" load-addr="0x9000"/>
</frame></backtrace></tagged-backtrace></row>
</trace-query-result>''')
assert module.summarize(runner_xml)['addresses'] == []
runner = module.summarize(runner_xml, [('run', 0x20, 0x24)], 'GalaxyPadRunner')
assert runner['address_binary'] == 'GalaxyPadRunner'
assert runner['addresses'] == [dict(name='run', raw_offset='0x23', samples=1, cycles=7)]
assert runner['ranges'][0]['samples'] == 1 and runner['ranges'][0]['cycles'] == 7
assert runner['leaves'] == [dict(name='run', samples=1, cycles=7)]
assert module.summarize(xml, binary_name='GalaxyPadRunner')['addresses'] == []
mobile_xml=ET.fromstring(ET.tostring(runner_xml).replace(b'CPU thread (test)',b'CPU-GPU thread (test)'))
mobile=module.summarize(mobile_xml,binary_name='GalaxyPadRunner',thread_prefix='CPU-GPU thread ')
assert mobile['samples']==1 and mobile['cycles']==7 and mobile['thread_prefix']=='CPU-GPU thread '
for prefix in ('CPU thread ', ''):
    try:
        module.summarize(mobile_xml,thread_prefix=prefix)
    except ValueError:
        pass
    else:
        raise AssertionError('Wrong/empty thread selector must fail')
try:
    module.summarize(ET.fromstring('<trace-query-result/>'))
except ValueError:
    pass
else:
    raise AssertionError('Empty export must fail')
print('CPU profile leaf/reference/range/zero-weight/empty-export checks passed')

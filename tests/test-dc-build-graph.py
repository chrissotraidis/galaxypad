"""Small parser regression for isolated accepted-graph builds; does not link."""
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('dc_build',root/'scripts/build-dc-column-experiment.py')
module=module_from_spec(spec);spec.loader.exec_module(module)
rows=module.parse_graph('''# A bounded CMake/Ninja fixture.
build obj/a.o: C_COMPILER_release /private/a.c || order
  FLAGS = -O3 -O2 -flto=thin
  DEFINES = -DVALUE=1
  INCLUDES = -I/private/include

build library.dylib: C_SHARED_LIBRARY_LINKER_release obj/a.o obj/b.o | exports.txt
  PRE_LINK = :
  POST_BUILD = :
  LINK_LIBRARIES = -lm
''')
assert len(rows)==2
assert rows[0][:3]==('obj/a.o','C_COMPILER_release','/private/a.c || order')
assert rows[0][3]['FLAGS']=='-O3 -O2 -flto=thin'
assert rows[1][2]=='obj/a.o obj/b.o | exports.txt'
assert rows[1][3]=={'PRE_LINK':':','POST_BUILD':':','LINK_LIBRARIES':'-lm'}
assert module.parse_graph('# no build edges\n')==[]
print('Isolated build graph preserves compile flags, order dependencies and linker inputs')

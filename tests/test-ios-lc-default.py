"""Execute the mobile entrypoint's default assignment, preserving inherited values."""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / "apple/ios/main.mm").read_text()
entry = source[source.index("int main(int argc,"):]
match = re.search(r'setenv\("GALAXYPAD_LC_BYTE_FAST",\s*"1",\s*0\);', entry)
assert match and match.start() < entry.index("UIApplicationMain")
assert "GALAXYPAD_LC_PAIR_FAST" not in entry
assert "#if" not in entry
program = r'''
#include <assert.h>
#include <stdlib.h>
#include <string.h>
static void defaults(void) { ASSIGNMENT }
int main(void) {
  const char *values[] = {"0", "1", "", "unexpected"};
  unsetenv("GALAXYPAD_LC_BYTE_FAST");
  unsetenv("GALAXYPAD_LC_PAIR_FAST");
  defaults();
  assert(strcmp(getenv("GALAXYPAD_LC_BYTE_FAST"), "1") == 0);
  assert(getenv("GALAXYPAD_LC_PAIR_FAST") == NULL);
  for (unsigned i = 0; i < sizeof(values)/sizeof(values[0]); ++i) {
    setenv("GALAXYPAD_LC_BYTE_FAST", values[i], 1);
    defaults();
    defaults();
    assert(strcmp(getenv("GALAXYPAD_LC_BYTE_FAST"), values[i]) == 0);
  }
}
'''.replace("ASSIGNMENT", match.group())
with tempfile.TemporaryDirectory(prefix="galaxypad-ios-lc-") as folder:
    path = Path(folder)
    (path / "test.c").write_text(program)
    subprocess.run(["xcrun", "clang", "-Wall", "-Wextra", "-Werror",
                    str(path / "test.c"), "-o", str(path / "test")], check=True)
    subprocess.run([str(path / "test")], check=True)
print("iOS byte-cache default, inherited opt-out, repeat and pair isolation pass")

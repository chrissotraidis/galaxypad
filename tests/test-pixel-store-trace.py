"""Compile the actual diagnostic helper; check opt-in, scope and output cap."""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / "ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Hooks.cpp").read_text()
helper = source.split("void TraceGalaxyPixelStore(", 1)[1].split("\n}\n", 1)[0]
with tempfile.TemporaryDirectory() as directory:
    cpp = Path(directory) / "test.cpp"
    binary = Path(directory) / "test"
    cpp.write_text("#include <cstdio>\n#include <cstdlib>\n#include <cstdint>\n"
                   "using u32=uint32_t; using u8=uint8_t;\nvoid TraceGalaxyPixelStore("
                   + helper + "\n}\nint main(){\n"
                   "TraceGalaxyPixelStore(0,0,1,0,0);\n"
                   "for(int i=0;i<20;++i) TraceGalaxyPixelStore(0x80452A2C,0xE0000000+i,1,0x3D043D04,0x2032);\n}\n")
    subprocess.run(["clang++", "-std=c++17", "-Wall", "-Wextra", "-Werror", str(cpp), "-o", str(binary)], check=True)
    for setting in (None, "0", "true", "10", "1"):
        env = dict(os.environ)
        env.pop("GALAXYPAD_PIXEL_STORE_TRACE", None)
        if setting is not None:
            env["GALAXYPAD_PIXEL_STORE_TRACE"] = setting
        result = subprocess.run([str(binary)], env=env, capture_output=True, text=True, check=True)
        lines = result.stderr.splitlines()
        assert len(lines) == (16 if setting == "1" else 0), (setting, lines)
        if lines:
            assert "sample=1 pc=80452a2c ea=e0000000 size=1 gqr6=3d043d04 msr=00002032" in lines[0]
            assert "sample=16" in lines[-1]
print("Pixel-store trace opt-in/scope/cap tests passed")

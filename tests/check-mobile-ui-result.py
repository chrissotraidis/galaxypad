#!/usr/bin/env python3
"""Check the test contract, not simctl's launcher exit status."""
import pathlib
import sys


def passed(output):
    lines = output.splitlines()
    return lines.count("GALAXYPAD_UI_TEST_PASS") == 1 and not any(
        line.startswith("FAIL:") for line in lines
    )


if __name__ == "__main__":
    output = pathlib.Path(sys.argv[1]).read_text(errors="replace")
    if not passed(output):
        sys.exit("UIKit test failed or did not reach its completion marker; inspect " + sys.argv[1])
    print("UIKit test completion verified: " + sys.argv[1])

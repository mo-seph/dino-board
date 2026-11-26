#!/usr/bin/env python3
"""Run every test_* function in test_dino.py and say what failed. Needs nothing installed.
    python3 software/tests/run_tests.py [part of a test's name]"""
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_dino

want = sys.argv[1] if len(sys.argv) > 1 else ""
tests = [(n, f) for n, f in sorted(vars(test_dino).items()) if n.startswith("test_") and callable(f) and want in n]
failed = 0
for name, fn in tests:
    began = time.time()
    try:
        fn()
        print("ok    %-52s %5.1f s" % (name, time.time() - began))
    except Exception:
        failed += 1
        print("FAIL  %s" % name)
        traceback.print_exc()
print("%d tests, %d failed" % (len(tests), failed))
sys.exit(1 if failed else 0)

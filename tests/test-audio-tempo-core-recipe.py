#!/usr/bin/env python3
"""Regression checks for target-preserving isolated-core policy validation."""
import copy
import importlib.util
import shlex
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('recipe',ROOT/'scripts/prepare-audio-tempo-core-host.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class CompilePolicy(unittest.TestCase):
    def setUp(self):
        self.new=ROOT/'generated/build/test-private-core'
        self.overlay=self.new.parent/'overlay.json'
        source=str(ROOT/'ref/ModernGekko/src/runtime/module.cpp')
        sdl=str(ROOT/'ref/ModernGekko/vendor/dolphin/Externals/SDL/SDL/src/video/uikit/SDL_uikitview.m')
        self.control=[];self.actual=[]
        for source,output in [(source,'runtime/module.o'),(source,'frontend/module.o'),(sdl,'sdl/view.o')]:
            cmd=['clang++','-O3','-fno-fast-math','-o',output,'-c',source]
            self.control.append({'directory':str(m.CORE),'file':source,'command':shlex.join(cmd)})
            count=2 if source.endswith('.m') else 1
            cmd+=['-ivfsoverlay',str(self.overlay)]*count
            self.actual.append({'directory':str(self.new),'file':source,'command':shlex.join(cmd)})
    def validate(self,rows=None):
        return m.validate_compile_commands(self.control,self.actual if rows is None else rows,self.new,self.overlay)
    def test_duplicate_sources_different_targets_survive(self):
        self.assertEqual(self.validate(list(reversed(self.actual))),{'entries':3,'unique_sources':2,'sdl_objc_repeated_overlay_entries':1})
    def test_missing_target_rejected(self):
        with self.assertRaises(SystemExit):self.validate(self.actual[1:])
    def test_repeated_target_rejected(self):
        with self.assertRaises(SystemExit):self.validate(self.actual+[self.actual[0]])
    def test_policy_drift_rejected_for_each_target(self):
        for index in range(3):
            rows=copy.deepcopy(self.actual);rows[index]['command']=rows[index]['command'].replace('-O3','-O2')
            with self.assertRaises(SystemExit):self.validate(rows)
    def test_wrong_overlay_rejected(self):
        rows=copy.deepcopy(self.actual);rows[2]['command']=rows[2]['command'].replace(str(self.overlay),'/tmp/wrong.json',1)
        with self.assertRaises(SystemExit):self.validate(rows)
    def test_missing_overlay_rejected(self):
        rows=copy.deepcopy(self.actual);cmd=shlex.split(rows[2]['command']);rows[2]['command']=shlex.join(cmd[:-2])
        with self.assertRaises(SystemExit):self.validate(rows)
    def test_working_directory_drift_rejected(self):
        rows=copy.deepcopy(self.actual);rows[0]['directory']='/tmp'
        with self.assertRaises(SystemExit):self.validate(rows)

if __name__=='__main__':unittest.main()

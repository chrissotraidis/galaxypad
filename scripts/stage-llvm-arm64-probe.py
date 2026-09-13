#!/usr/bin/env python3
"""Stage a private offline ARM64 LLVM probe; never modify pinned sources.

This is not a production backend patch. It uses the standalone DolRecomp CPU
oracle, disables cross-chunk calls, and does not exercise Galaxy/chassis ABI.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('destination',type=Path)
parser.add_argument('--reservation-fix',action='store_true',help='Include isolated runtime-compatible reservation boundary correction')
parser.add_argument('--memory-state',action='store_true',help='Diagnostic: keep private cached state slots in memory instead of SSA promotion')
parser.add_argument('--context-state',action='store_true',help='Diagnostic: use direct CPU context slots instead of a duplicate private cache')
args=parser.parse_args()
if args.memory_state and args.context_state:
    parser.error('state experiments are mutually exclusive')
original=root/'ref/ModernGekko/vendor/dolphin/DolRecomp'
pin=subprocess.check_output(['git','rev-parse','HEAD'],cwd=original,text=True).strip()
lock=json.loads((root/'config/dependencies.lock.json').read_text())
assert pin==lock['repositories']['dolRecomp']['revision']
out=args.destination.resolve()
out.mkdir(parents=True,exist_ok=False)
for directory in ('src','tests','tools'):
    shutil.copytree(original/directory,out/directory)
for filename in ('CMakeLists.txt','LICENSE'):
    shutil.copy2(original/filename,out/filename)
changes={}
def rewrite(relative, transform):
    path=out/relative
    before=path.read_text()
    after=transform(before)
    assert before!=after
    path.write_text(after)
    changes[relative]={'original_sha256':hashlib.sha256(before.encode()).hexdigest(),
                       'staged_sha256':hashlib.sha256(after.encode()).hexdigest(),
                       'diff':''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=relative,tofile=relative))}
def replace_once(text, old, new):
    assert text.count(old)==1,old
    return text.replace(old,new)

def backend(text):
    text=replace_once(text,'#include <llvm/IR/Module.h>',
                     '#include <llvm/IR/Module.h>\n#include <llvm/IR/Instructions.h>')
    text=replace_once(text,
      '  if (triple.getArch() != llvm::Triple::x86_64 ||\n      (!triple.isOSLinux() && !triple.isOSWindows())) {',
      '''  const char* probe = std::getenv("GALAXYPAD_LLVM_ARM64_PROBE");
  const bool apple_probe = probe && std::strcmp(probe, "1") == 0 &&
      triple.getArch() == llvm::Triple::aarch64 && triple.isMacOSX();
  if (apple_probe && options && options->function_range_count != 0) {
    fprintf(diagnostics, "probe refuses cross-chunk range tables\\n");
    return false;
  }
  if (!apple_probe && (triple.getArch() != llvm::Triple::x86_64 ||
      (!triple.isOSLinux() && !triple.isOSWindows()))) {''')
    verification='  if (llvm::verifyModule(module, &diagnosticStream)) {'
    assert text.count(verification)==2 # pre- and post-optimization verification
    text=text.replace(verification,
      '''  // This pinned helper interface uses only unsigned u8/u16/bool for
  // narrow C ABI values, including indirect external read/write callbacks.
  // Do not generalize this to unknown signed helper signatures.
  if (apple_probe) {
    auto narrow = [](llvm::Type* t) {
      return t->isIntegerTy() && t->getIntegerBitWidth() < 32;
    };
    for (llvm::Function& fn : module) {
      if (fn.isIntrinsic()) continue;
      if (narrow(fn.getReturnType())) fn.addRetAttr(llvm::Attribute::ZExt);
      for (unsigned i = 0; i < fn.arg_size(); ++i)
        if (narrow(fn.getFunctionType()->getParamType(i)))
          fn.addParamAttr(i, llvm::Attribute::ZExt);
      for (llvm::BasicBlock& bb : fn) for (llvm::Instruction& inst : bb) {
        auto* call = llvm::dyn_cast<llvm::CallBase>(&inst);
        if (!call || (call->getCalledFunction() && call->getCalledFunction()->isIntrinsic())) continue;
        if (narrow(call->getType())) call->addRetAttr(llvm::Attribute::ZExt);
        for (unsigned i = 0; i < call->arg_size(); ++i)
          if (narrow(call->getArgOperand(i)->getType()))
            call->addParamAttr(i, llvm::Attribute::ZExt);
      }
    }
  }
  if (llvm::verifyModule(module, &diagnosticStream)) {''',1)
    if args.memory_state:
        anchor='  if (llvm::verifyModule(module, &diagnosticStream)) {'
        assert text.count(anchor)==2
        text=text.replace(anchor,'''  // Diagnostic only: private cached CPU slots, not guest/host memory.
  // Preserve every instruction entry and all state sync/reload boundaries.
  for (llvm::Function& fn : module) for (llvm::BasicBlock& bb : fn)
    for (llvm::Instruction& inst : bb) {
      if (auto* load = llvm::dyn_cast<llvm::LoadInst>(&inst)) {
        auto* slot = llvm::dyn_cast<llvm::AllocaInst>(load->getPointerOperand());
        if (slot && slot->getName().starts_with("state")) load->setVolatile(true);
      }
      if (auto* store = llvm::dyn_cast<llvm::StoreInst>(&inst)) {
        auto* slot = llvm::dyn_cast<llvm::AllocaInst>(store->getPointerOperand());
        if (slot && slot->getName().starts_with("state")) store->setVolatile(true);
      }
    }
'''+anchor,1)
    return text
rewrite('src/backend/llvm/llvm_backend.cpp',backend)

def reservation_fix(text):
    text=replace_once(text,'builder_.CreateXor(reserved, address)',
      'builder_.CreateXor(normalizeAddress(reserved), normalizeAddress(address))')
    text=replace_once(text,
      'void FunctionEmitter::emitGuestStore(Value *address, Value *value, u32 width) {\n  clearReservation(address);',
      'void FunctionEmitter::emitGuestStore(Value *address, Value *value, u32 width) {')
    head,store=text.split('void FunctionEmitter::emitGuestStore',1)
    store=replace_once(store,'  builder_.SetInsertPoint(mem1Block);\n  Value *ram =',
      '  builder_.SetInsertPoint(mem1Block);\n  clearReservation(address);\n  Value *ram =')
    store=replace_once(store,'  builder_.SetInsertPoint(mem2Block);\n  Value *mem2Offset =',
      '  builder_.SetInsertPoint(mem2Block);\n  clearReservation(address);\n  Value *mem2Offset =')
    text=head+'void FunctionEmitter::emitGuestStore'+store
    text=replace_once(text,
      '  builder_.CreateCall(\n      functionType, fn,\n      {offset, builder_.getInt32(width), builder_.CreateLoad(ptr, user)});',
      '''  // The journal observes the cleared reservation and may update it.
  // Keep the already acquired RAM pointer for the current store.
  syncState(DOLIR_STATE_RESERVE_VALID);
  syncState(DOLIR_STATE_RESERVE_ADDR);
  builder_.CreateCall(
      functionType, fn,
      {offset, builder_.getInt32(width), builder_.CreateLoad(ptr, user)});
  reloadState(DOLIR_STATE_RESERVE_VALID);
  reloadState(DOLIR_STATE_RESERVE_ADDR);''')
    return text
if args.reservation_fix:
    rewrite('src/backend/llvm/llvm_memory_lowering.cpp',reservation_fix)

if args.context_state:
    rewrite('src/backend/llvm/llvm_function_emitter.h',lambda text: replace_once(text,
      'std::array<llvm::AllocaInst *, DOLIR_STATE_COUNT> state_{};',
      'std::array<llvm::Value *, DOLIR_STATE_COUNT> state_{};'))
    def context_state(text):
        return replace_once(text,
          '''    state_[slot] = builder_.CreateAlloca(type(dolir_state_type(stateSlot)),
                                         nullptr, "state");
    builder_.CreateStore(loadContext(stateSlot), state_[slot]);''',
          '''    // Isolated direct-context experiment: helpers share this storage.
    state_[slot] = bytePtr(stateOffset(stateSlot));''')
    rewrite('src/backend/llvm/llvm_function_emitter.cpp',context_state)

def emitter_test(text):
    text=replace_once(text,'    options.function_ranges = ranges;\n    options.function_range_count = 2;',
      '''    // Prove supplied direct-call ranges fail closed in this probe.
    options.function_ranges = ranges;
    options.function_range_count = 2;
    CHECK(!dolllvm_emit_object(&module, argv[1], &options, stderr));
    options.function_ranges = nullptr;
    options.function_range_count = 0;''')
    text=replace_once(text,'#if defined(_WIN32)\n    CHECK(magic',
      '''#if defined(__APPLE__)
    CHECK(magic[0] == 0xcf && magic[1] == 0xfa && magic[2] == 0xed && magic[3] == 0xfe);
#elif defined(_WIN32)
    CHECK(magic''')
    return text
rewrite('tests/test_llvm_backend.cpp',emitter_test)

def execution_test(text):
    text=replace_once(text,'void func_80002D00(CPUState* cpu);',
      'void func_80002D00(CPUState* cpu);\nvoid func_80002E00(CPUState* cpu);')
    return replace_once(text,
      '    CHECK(cpu.pc == 0x80002D00u || cpu.pc == 0x80002E00u);\n    CHECK(cpu.downcount <= -128 && cpu.downcount >= -512);',
      '''    // Cross-chunk branches return before executing the other body.
    CHECK(cpu.pc == 0x80002E00u);
    CHECK(cpu.downcount < 0 && cpu.downcount > -16);
    const s64 first_downcount = cpu.downcount;
    func_80002E00(&cpu);
    CHECK(cpu.pc == 0x80002D00u);
    CHECK(cpu.downcount < first_downcount && cpu.downcount > -32);''')
rewrite('tests/test_llvm_execute.c',execution_test)
(out/'probe-provenance.json').write_text(json.dumps({'pin':pin,'changes':changes,
  'boundary':'Offline standalone CPU oracle only; no object cache reuse, no Galaxy/chassis ABI or performance acceptance.'},indent=2))
for relative,data in changes.items():
    assert hashlib.sha256((original/relative).read_bytes()).hexdigest()==data['original_sha256']
print('Staged offline probe:',out)

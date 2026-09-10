#pragma once

#include "plan.h"

namespace galaxypad::vector_experiment
{
// A bounded table of existing interpreter function pointers, not emitted code.
// Construct once outside execution; never retain an instruction fetched from guest RAM.
// Only the opcode dispatch is replaced. The caller still owns the complete
// SingleStepInner fetch, HLE, exception, PC, tracing, cycle and monitor chassis.
template <typename Interpreter, typename GuestInstruction>
class Dispatch
{
public:
  using Operation = typename Interpreter::Instruction;

  Dispatch()
  {
    for (std::size_t i = 0; i < kGeneric.size(); ++i)
      m_generic[i] = Interpreter::GetInterpreterOp(GuestInstruction{kGeneric[i]});
    for (std::size_t i = 0; i < kSystemCall.size(); ++i)
      m_system[i] = Interpreter::GetInterpreterOp(GuestInstruction{kSystemCall[i]});
  }

  Operation Lookup(std::uint32_t pc, GuestInstruction fetched) const
  {
    const auto instruction = Recognize(pc, fetched.hex);
    if (!instruction)
      return nullptr;
    return instruction->system_call ? m_system[instruction->index] :
                                      m_generic[instruction->index];
  }

private:
  std::array<Operation, kGeneric.size()> m_generic{};
  std::array<Operation, kSystemCall.size()> m_system{};
};
} // namespace galaxypad::vector_experiment

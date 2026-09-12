#!/usr/bin/env python3
"""Copy the production mixer and replace only DMA input with the isolated tempo stage."""
import argparse, difflib, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'ref/ModernGekko/vendor/dolphin/Source/Core/AudioCommon'
def replace(s,a,b):
 assert s.count(a)==1, (a[:80],s.count(a))
 return s.replace(a,b)
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert ROOT/'generated/experiments' in out.parents
 out.mkdir(parents=True,exist_ok=False)
 h=(SRC/'Mixer.h').read_text();c=(SRC/'Mixer.cpp').read_text();oldh=h;oldc=c
 h=replace(h,'#include "AudioCommon/SurroundDecoder.h"','#include "AudioCommon/AudioTempo.h"\n#include "AudioCommon/SurroundDecoder.h"')
 h=replace(h,'    Granule m_front, m_back;','    Granule m_front{}, m_back{};')
 h=replace(h,'    void Enqueue();','    static void ApplyGranuleWindow(Granule* output, const Granule& input, std::size_t start);\n    void FlushTempoOnConsumer();\n    void Enqueue();')
 h=replace(h,'  MixerFifo m_dma_mixer{','''  // DMA only: no second queued granule FIFO and no eleven unused tempo rings.
  galaxypad::experiment::AudioTempo m_dma_tempo;
  std::array<galaxypad::experiment::AudioTempo::Frame, 128> m_dma_tempo_previous{};
  std::array<galaxypad::experiment::AudioTempo::Frame, 1536> m_dma_tempo_callback{};
  std::size_t m_dma_tempo_callback_index = 0;
  std::atomic<bool> m_dma_tempo_failed{false};
  std::atomic<bool> m_dma_tempo_flush_requested{false};
  bool m_dma_tempo_was_running = true;  // consumer only; first startup retains input
  std::size_t m_dma_tempo_real_input_remainder = 0;  // producer only

  MixerFifo m_dma_mixer{''')
 # Share the exact existing (DPSS-derived, not Hann) window with both input sources.
 start=c.index('  // import numpy as np',c.index('void Mixer::MixerFifo::Enqueue()'))
 end=c.index('\n  const std::size_t head',start)
 window=c[start:end]
 c=c[:start]+c[end:]
 c=replace(c,'void Mixer::MixerFifo::Enqueue()', '''void Mixer::MixerFifo::ApplyGranuleWindow(Granule* output, const Granule& input,
                                             std::size_t start)
{
'''+window+'''
  for (std::size_t i = 0; i < GRANULE_SIZE; ++i)
    (*output)[i] = input[(i + start) & GRANULE_MASK] * GRANULE_WINDOW[i];
}

void Mixer::MixerFifo::FlushTempoOnConsumer()
{
  m_mixer->m_dma_tempo.FlushOnConsumer();
  m_mixer->m_dma_tempo_previous = {};
  m_front = {}; m_back = {}; m_current_index = 0;
  m_quantization_error = {}; m_fade_volume = 1.0f;
  m_queue_fading.store(false, std::memory_order_relaxed);
  m_queue_looping.store(false, std::memory_order_relaxed);
}

void Mixer::MixerFifo::Enqueue()''')
 c=replace(c,'''  const std::size_t start_index = m_next_buffer_index;
  for (std::size_t i = 0; i < GRANULE_SIZE; ++i)
    m_queue[head][i] = m_next_buffer[(i + start_index) & GRANULE_MASK] * GRANULE_WINDOW[i];''','''  ApplyGranuleWindow(&m_queue[head], m_next_buffer, m_next_buffer_index);''')
 # Bypass old DMA reserve and variable pitch correction; all other FIFOs unchanged.
 a0=c.index('#if defined(__APPLE__)',c.index('void Mixer::MixerFifo::Mix('));a1=c.index('#endif',a0)+len('#endif')
 c=c[:a0]+'''  if (this == &m_mixer->m_dma_mixer)
  {
    const bool running = Core::GetState(Core::System::GetInstance()) == Core::State::Running;
    const bool flush = m_mixer->m_dma_tempo_flush_requested.exchange(false, std::memory_order_acq_rel);
    if (flush || running != m_mixer->m_dma_tempo_was_running)
      FlushTempoOnConsumer();
    m_mixer->m_dma_tempo_was_running = running;
    if (!running || m_mixer->m_dma_tempo_failed.load(std::memory_order_acquire))
    {
      FlushTempoOnConsumer();
      return;
    }
    in_sample_rate = 32000.0;
  }
'''+c[a1:]
 c=replace(c,"  constexpr u32 INDEX_HALF = 0x80000000;","""  if (this == &m_mixer->m_dma_mixer && num_samples > 2048)
  {
    // Fixed callback workspace; oversized backend requests are processed in
    // bounded pieces immediately, without a second queue or allocations.
    while (num_samples)
    {
      const auto count = std::min<std::size_t>(num_samples, 2048);
      Mix(samples, count); samples += count * 2; num_samples -= count;
    }
    return;
  }
  constexpr u32 INDEX_HALF = 0x80000000;""")
 c=replace(c,"  const u32 index_jump = std::lround(base * in_sample_rate / out_sample_rate);","""  const u32 index_jump = std::lround(base * in_sample_rate / out_sample_rate);
  if (this == &m_mixer->m_dma_mixer)
  {
    const auto hops = (u64(m_current_index & (INDEX_HALF-1)) + u64(index_jump)*num_samples) / INDEX_HALF;
    const auto tempo_frames = hops * GRANULE_OVERLAP;
    if (tempo_frames > m_mixer->m_dma_tempo_callback.size())
    {
      m_mixer->m_dma_tempo_failed.store(true, std::memory_order_release);
      FlushTempoOnConsumer();
      return;
    }
    const auto before = m_mixer->m_dma_tempo.ReadStatistics().unavailableWindows;
    m_mixer->m_dma_tempo.Pull(m_mixer->m_dma_tempo_callback.data(), tempo_frames);
    const auto after = m_mixer->m_dma_tempo.ReadStatistics().unavailableWindows;
    for (auto failed = before; failed < after; ++failed)
      GalaxyPadDiagnostics::RecordDmaUnderrun();
    m_mixer->m_dma_tempo_callback_index = 0;
  }""")
 # Consumer source conversion preserves window/interpolator/volume/quantization.
 c=replace(c,'''bool Mixer::MixerFifo::Dequeue(Granule* granule)
{''','''bool Mixer::MixerFifo::Dequeue(Granule* granule)
{
  if (this == &m_mixer->m_dma_mixer)
  {
    std::array<galaxypad::experiment::AudioTempo::Frame, GRANULE_OVERLAP> current;
    std::copy_n(m_mixer->m_dma_tempo_callback.data() + m_mixer->m_dma_tempo_callback_index,
                current.size(), current.data());
    m_mixer->m_dma_tempo_callback_index += current.size();
    Granule raw;
    for (std::size_t i = 0; i < GRANULE_OVERLAP; ++i)
    {
      const auto previous = m_mixer->m_dma_tempo_previous[i];
      raw[i] = {previous.left, previous.right};
      raw[i + GRANULE_OVERLAP] = {current[i].left, current[i].right};
    }
    ApplyGranuleWindow(granule, raw, 0);
    m_mixer->m_dma_tempo_previous = current;
    return false;
  }
''')
 c=replace(c,'''    const s16* ptr = samples;
    for (std::size_t i = 0; i != num_samples; ++i)
    {
      m_dma_mixer.PushSample(Common::swap16(ptr[1]), Common::swap16(ptr[0]));
      ptr += 2;
    }''','''    if (!m_dma_tempo_failed.load(std::memory_order_acquire))
    {
      std::array<galaxypad::experiment::AudioTempo::Frame, 128> converted;
      for (std::size_t offset = 0; offset < num_samples;)
      {
        const auto count = std::min(converted.size(), num_samples - offset);
        for (std::size_t i = 0; i < count; ++i)
          converted[i] = {float(static_cast<s16>(Common::swap16(samples[2*(offset+i)+1]))),
                          float(static_cast<s16>(Common::swap16(samples[2*(offset+i)])))};
        const auto accepted = m_dma_tempo.Push(converted.data(), count);
        if (accepted != count)
          GalaxyPadDiagnostics::RecordDmaQueueFullDrop();
        m_dma_tempo_real_input_remainder += accepted;
        while (m_dma_tempo_real_input_remainder >= 128)
        {
          m_dma_tempo_real_input_remainder -= 128;
          const auto now = std::chrono::steady_clock::now().time_since_epoch();
          // Existing enqueues continue to mean 128 newly accepted input frames.
          GalaxyPadDiagnostics::RecordDmaEnqueue(
              m_dma_tempo.BufferedInputFramesOnProducer() / 128,
              std::chrono::duration_cast<std::chrono::nanoseconds>(now).count());
        }
        offset += count;
      }
    }''')
 c=replace(c,'''void Mixer::MixerFifo::SetInputSampleRateDivisor(u32 rate_divisor)
{
  m_input_sample_rate_divisor = rate_divisor;''','''void Mixer::MixerFifo::SetInputSampleRateDivisor(u32 rate_divisor)
{
  if (this == &m_mixer->m_dma_mixer && rate_divisor != FIXED_SAMPLE_RATE_DIVIDEND / 32000)
  {
    // Explicit isolated-candidate failure before changing the interpretation of
    // any queued sample. Keep the process alive; recreate the stream to recover.
    m_mixer->m_dma_tempo_failed.store(true, std::memory_order_release);
    ERROR_LOG_FMT(AUDIO, "GalaxyPad tempo candidate requires 32 kHz DMA; rejecting divisor {}",
                  rate_divisor);
    return;
  }
  m_input_sample_rate_divisor = rate_divisor;''')
 c=replace(c,'''  p.Do(m_input_sample_rate_divisor);
  p.Do(m_LVolume);''','''  u32 rate_divisor = m_input_sample_rate_divisor;
  p.Do(rate_divisor);
  if (p.IsReadMode())
  {
    SetInputSampleRateDivisor(rate_divisor);
    if (this == &m_mixer->m_dma_mixer)
      m_mixer->m_dma_tempo_flush_requested.store(true, std::memory_order_release);
  }
  p.Do(m_LVolume);''')
 tempo=(ROOT/'experiments/audio-tempo/AudioTempo.h').read_text()
 tempo=replace(tempo,'  std::size_t Push(const Frame* source, std::size_t count) {','''  // Producer-only diagnostic snapshot. Head cannot advance on another thread;
  // loading tail first also avoids subtracting a newer tail from an older head.
  std::size_t BufferedInputFramesOnProducer() const {
    const auto tail = m_tail.load(std::memory_order_acquire);
    return m_head.load(std::memory_order_relaxed) - tail;
  }

  std::size_t Push(const Frame* source, std::size_t count) {''')
 for name,old,new in [('Mixer.cpp',oldc,c),('Mixer.h',oldh,h)]:
  (out/name).write_text(new)
  (out/(name+'.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='control/'+name,tofile='candidate/'+name)))
 (out/'AudioTempo.h').write_text(tempo)
 (out/'manifest.json').write_text(json.dumps({name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['Mixer.cpp','Mixer.h','AudioTempo.h']},indent=2)+'\n')
 print(out)
if __name__=='__main__':main()

// Diagnostic-only, application-owned post-mixer capture. Not a production audio path.
#pragma once
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace galaxypad::diagnostic {
class PcmCapture {
public:
  static constexpr uint32_t Rate = 48000, Channels = 2, Capacity = Rate * 120;
  static_assert(std::atomic<uint32_t>::is_always_lock_free);
  // Start/Finish require the audio callback to be quiescent. This object supports
  // one serial RemoteIO callback producer; it never changes the audio itself.
  bool Start(const char* path, uint32_t rate, uint32_t capacity = Capacity) {
    if (m_pcm || !path || !*path || rate != Rate || !capacity || capacity > Capacity)
      return false;
    m_pcm = static_cast<int16_t*>(std::calloc(capacity * Channels, sizeof(int16_t)));
    if (!m_pcm) return false;
    // calloc may lazily map pages: explicitly touch before the realtime callback.
    volatile int16_t* touched = m_pcm;
    for (uint32_t i = 0; i < capacity * Channels; i += 1024) touched[i] = 0;
    m_path = path; m_capacity = capacity; m_used.store(0, std::memory_order_relaxed);
    m_callbacks = m_frames = m_omitted = m_short = m_invalid = 0;
    m_min = UINT32_MAX; m_max = 0; m_first_host = m_last_host = 0;
    return true;
  }
  void Record(const int16_t* pcm, uint32_t requested, uint32_t mixed, uint64_t host_time) {
    if (!m_pcm) return;
    ++m_callbacks;
    m_min = std::min(m_min, requested); m_max = std::max(m_max, requested);
    if (m_callbacks == 1) m_first_host = host_time;
    m_last_host = host_time;
    if (mixed < requested) ++m_short;
    if (!pcm || mixed > requested) { ++m_invalid; return; }
    m_frames += mixed;
    const uint32_t used = m_used.load(std::memory_order_relaxed);
    const uint32_t count = std::min(mixed, m_capacity - used);
    if (count) std::memcpy(m_pcm + used * Channels, pcm, count * Channels * sizeof(int16_t));
    m_omitted += mixed - count;
    m_used.store(used + count, std::memory_order_release);
  }
  bool Finish() {
    if (!m_pcm) return true;
    const uint32_t frames = m_used.load(std::memory_order_acquire), bytes = frames * 4;
    // Exclusive creation preserves earlier recordings. Both writes happen only
    // after AudioOutputUnitStop and AudioUnitUninitialize, never in Record.
    FILE* wav = std::fopen(m_path.c_str(), "wbx");
    bool ok = wav != nullptr;
    if (wav) {
      unsigned char h[44]{};
      std::memcpy(h, "RIFF", 4); U32(h+4, 36+bytes); std::memcpy(h+8,"WAVEfmt ",8);
      U32(h+16,16); U16(h+20,1); U16(h+22,Channels); U32(h+24,Rate);
      U32(h+28,Rate*4); U16(h+32,4); U16(h+34,16); std::memcpy(h+36,"data",4); U32(h+40,bytes);
      ok = std::fwrite(h,1,sizeof(h),wav)==sizeof(h);
      ok = (std::fwrite(m_pcm,1,bytes,wav)==bytes) && ok;
      ok = (std::fclose(wav)==0) && ok;
    }
    FILE* meta = std::fopen((m_path+".json").c_str(), "wx");
    if (meta) {
      const int written = std::fprintf(meta,
        "{\n  \"diagnostic_only\": true,\n  \"source\": \"GalaxyPad Mixer output before RemoteIO volume\",\n"
        "  \"format\": \"stereo interleaved signed 16-bit little-endian WAV\",\n"
        "  \"sample_rate\": 48000,\n  \"channels\": 2,\n  \"capacity_frames\": %u,\n"
        "  \"captured_frames\": %u,\n  \"observed_mixed_frames\": %llu,\n  \"omitted_after_limit_frames\": %llu,\n"
        "  \"callbacks\": %llu,\n  \"callback_requested_min\": %u,\n  \"callback_requested_max\": %u,\n"
        "  \"short_callbacks\": %llu,\n  \"invalid_callbacks\": %llu,\n"
        "  \"first_host_time\": %llu,\n  \"last_host_time\": %llu,\n  \"wav_write_ok\": %s,\n"
        "  \"wall_clock_pause_gaps_included\": false\n}\n",
        m_capacity,frames,(unsigned long long)m_frames,(unsigned long long)m_omitted,
        (unsigned long long)m_callbacks,m_callbacks?m_min:0,m_max,
        (unsigned long long)m_short,(unsigned long long)m_invalid,
        (unsigned long long)m_first_host,(unsigned long long)m_last_host,ok?"true":"false");
      const bool closed = std::fclose(meta)==0;
      ok = written > 0 && closed && ok;
    } else ok = false;
    std::fprintf(stderr,"[GalaxyPad PCM diagnostic] capture %s: %u frames, %llu omitted, %s\n",
      ok?"written":"WRITE FAILED",frames,(unsigned long long)m_omitted,m_path.c_str());
    std::free(m_pcm); m_pcm=nullptr; m_path.clear(); return ok;
  }
private:
  static void U16(unsigned char* p, uint16_t x) { p[0]=x; p[1]=x>>8; }
  static void U32(unsigned char* p, uint32_t x) { for (unsigned i=0;i<4;++i) p[i]=x>>(i*8); }
  int16_t* m_pcm=nullptr;
  std::string m_path;
  uint32_t m_capacity=0, m_min=UINT32_MAX, m_max=0;
  std::atomic<uint32_t> m_used{0};
  uint64_t m_callbacks=0,m_frames=0,m_omitted=0,m_short=0,m_invalid=0,m_first_host=0,m_last_host=0;
};
}

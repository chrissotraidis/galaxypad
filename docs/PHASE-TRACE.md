# Frame-phase trace

Status: **default-off instrumentation validated; matched active Metal trace complete**

The remaining G6 stutter is scene-dependent and CPU-bound. A 10-second sample in the post-attack Star Festival plaza placed 5,932 of 7,000 CPU-thread samples in `StaticRecompCore::Run`, with 5,336 below `chassis_dispatch`. The video thread was waiting in 4,166 of 7,011 samples. Its synchronous EFB-depth wait appeared in only 48 samples, while the active remainder covered draw submission, vertex work, render-pass setup, and EFB copies. This does not make rendering free, but it rules out a continuously saturated Metal thread as the main cause of the observed slowdown.

Visible cadence in the same live progression ranged from approximately 40–50 FPS in the attacked plaza and Bowser airship effects to 59.9 FPS in sparse views. The original approximately 18 FPS report remains valid for the earlier heavy transition, but the defect is not a universal fixed-rate cap.

## Instrumentation

Set `GALAXYPAD_PHASE_TRACE` to an ignored CSV path before starting `moderngekko-run`. The runtime records:

```text
ordinal,steady_ns,event,value
```

The event vocabulary is:

- `vi_end_field`: emulated VI field completion on the CPU thread;
- `frame_begin`: first host draw call for a frame;
- `frame_end`: XFB-copy frame completion;
- `present_queue` and `present_done`: host presentation boundaries;
- `input_sample`: emulated P1 sample, with the button mask in `value`;
- `dma_enqueue`: 128-frame main-DSP production, with queue depth in `value`;
- `audio_callback`: host callback, with requested frames in `value`.

The trace uses a shared steady-clock epoch and serial ordinal across threads. It is line-buffered and mutex-protected so a stopped run remains analyzable, but this intentionally adds overhead and must never be used as an acceptance-performance result. Without the environment variable, each call returns before taking a timestamp or lock.

## Validation

The initial Null/headless smoke produced 31,408 event rows: 2,298 VI fields, 2,208 frame begin/end pairs, 2,286 presentation queues, 2,205 presentation completions, 6,870 input samples, 9,571 DMA enqueues, and 3,762 audio callbacks. It overlapped an earlier live game process and therefore validates collection/CSV integrity only; it is not performance evidence.

A sequential matched Metal pair then used copied Star Festival state, Cubeb, native-class 1× rendering, the accepted indexed module, and the exact 44-transition fixture. Tracing produced 54.397 Hz graphics and 29.091 kHz DMA; its uninstrumented control produced 54.649 Hz and 29.279 kHz. Observer cost was only 0.46%/0.64%, so the trace is valid for diagnosis. Frame intervals were 17.002/22.645/23.504 ms median/p95/p99; 29.21% were at least 20 ms. Nearest present queue-to-completion was only 0.119/0.167/0.953 ms, while first-draw-to-frame-end was 13.064/21.177/22.237 ms. The final active 120 seconds fell to 47.932 VI fields/s, 47.670 frame ends/s, and 47.873 presents/s. The dominant deficit is therefore before presentation in generated execution and FIFO/render preparation, not the swap itself.

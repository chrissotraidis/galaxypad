# R813: cross-product experiment parked; fresh plaza CPU sample retained

Reverse baseline51179 reached the same neutral starting plaza. Screenshots
cross-reverse-r813-plaza.png and -after.png confirm scene/position. After15s
settling,45s capture1418 completed exit0. Seven complete windows contain996
after_frame_events over36.801155s:27.06437events/sec. Capture artifact:
generated/cross-reverse-r813-capture.json. No profiler ran during capture.

Observed order: baseline25.92818, candidate26.63122, candidate26.00536,
baseline27.06437. The second candidate window is from the same candidate
process, not an independent restart. This small experiment does not establish
zero possible benefit, but clearly does not meet repeatable material game-speed
promotion criteria. Park the six-instruction cross-product candidate. Do not
keep tuning its guards, expand it based on isolated timings, or change defaults.
Correctness/NI tests remain useful evidence, not performance acceptance.

## Next bottleneck evidence

Only after the final speed capture, took a separate10s/1ms sample of the same
baseline plaza (sample2750 exit0). File generated/plaza-cpu-r813.sample.txt,
SHA25675e6af070664ee39133134592ad99846c3541c207330b832cfe4db327aeef5eb.
CPU thread has6004 observations. Its largest branch is4748 observations beneath
StaticRecompCore::Run+2516, including4070 beneath chassis_dispatch+152. These
are inclusive sampled stacks, not self CPU percentages. Among that dispatch
branch,220 observations wait for a float future;138 are in the entire generated
chunk func_804B60A0. Neither identifies the six-instruction region's CPU share.

The process-wide leaf summary includes Run698, GPU loop413, chassis_dispatch242,
ModManager::Dispatch227, VertexLoader::RunVertices194 and indexed normal-reader
167. Counts across different threads must not be summed as CPU-thread shares;
waiting threads dominate the global summary. Next classify the CPU/GPU thread
stacks separately and map sampled offsets in Run/dispatch and vertex decoding
to actual source before choosing another implementation. Compare with retained
closed dispatch experiments; do not reopen an old tiny variant from symbol
counts alone. A broad per-frame cost must justify the next expensive build.

Runtime terminate/console61573 and Simulator shutdown75840 exit0. Save remains
99d432... unchanged. No native clean-stop callback or audio/hardware completion
claim. No Simulator or build remains running. Full original PRD, SunPad UI,
gameplay, movie/audio, stability and physical-device objectives stay active.

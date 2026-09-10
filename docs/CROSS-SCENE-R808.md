# R808: NI-capable candidate reaches the Star Festival plaza

R807 build session29185 completed successfully. Private module SHA256:
5895a90db1c4da381c019ce39d7ecd94810e5af43e565434af3c4b7e89e7358d.
Simulator platform/signature validation passed; normal module remains unchanged.

Strengthened the exact-source regression to require more than10000 accepted
cases separately for NI0 and NI1. R808 exact diagnostic source passes262144
complete-state/status cases, with24129 fast cases in each mode. The NI builder
now requests this assertion explicitly. Counter-summary tests and Python syntax
checks pass. Logs: generated/cross-ni-coverage-r808.log/.err.

One iPad Simulator, DE8E956F-6B29-4FF3-AF4A-77034CE8588A, launched the private
module with the unchanged R791 THP host. Pre-run GameData.bin backup is retained
in generated/candidates/cross-diagnostic-r807/GameData.before.bin, SHA256
99d432d517b92b19da0c403819b91288b10c7063c3ce61f5000347ef823ab64f.

Screenshots cross-r808-scene.png and cross-r808-move.png visibly show the Star
Festival plaza and Mario responding to a short movement/jump snapshot. These
are diagnostic inputs, not touch-control acceptance. The existing portrait
letterboxing/control layout issue remains open; no UI fix is claimed.

The scene-specific counter window starts at log line7753, after the plaza
screenshot. Source log: generated/cross-runtime-r808.log. Diagnostic timing is
not an uninstrumented speed A/B, and accepted-path frequency is not CPU share.

## Result and next decision

Window7753..8019 contains245 observations:999424 calls,991598 fast,0 mode
rejections,7623 range rejections,203 ties. Fast fraction99.21695%. Retained
summary: generated/cross-eligibility-r808-plaza.json. Final log SHA256:
5ee77872d827436ae29f74b8bafe58daef6a0d10d4598800945474e1949f84c2.

Instrumentation frame-event windows remain slow,16.60..26.04 FPS; audio DMA
underruns continue (2220 to2450 between retained audio observations). This is
not an A/B or proof of audible output. No end-to-end gain is claimed.

Terminate and Simulator shutdown completed successfully (console70780 and
shutdown35880 exit0); no native clean-stop callback is claimed. Save still
matches the pre-run99d432... hash. Normal module still3acdcd...; no promotion.

Next build a distinct uninstrumented candidate using the same verified control
and object inventory, then compare matched plaza windows sequentially. The
observed rejection mix justifies that experiment; it does not justify expanding
this optimization to more routines or declaring performance solved. Preserve
the original PRD, SunPad UI, movie/audio, stability and physical-device gates.

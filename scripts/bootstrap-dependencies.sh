#!/usr/bin/env bash
# Reproduce GalaxyPad's public, ignored source references at reviewed revisions.
# This script never searches for or downloads game data.
set -euo pipefail

root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
ref="$root/ref"
mkdir -p "$ref"

ensure_checkout() {
  local url=$1 path=$2 revision=$3
  if [[ ! -d "$path/.git" ]]; then
    git clone --filter=blob:none "$url" "$path"
    git -C "$path" checkout --detach "$revision"
  fi

  local actual
  actual="$(git -C "$path" rev-parse HEAD)"
  if [[ "$actual" != "$revision" ]]; then
    echo "reference checkout mismatch: $path" >&2
    echo "  expected: $revision" >&2
    echo "  actual:   $actual" >&2
    exit 1
  fi
  git -C "$path" remote set-url --push origin DISABLED
}

require_clean() {
  local checkout=$1
  if [[ -n "$(git -C "$checkout" status --porcelain --untracked-files=all)" ]]; then
    echo "unexpected local changes in reference checkout: $checkout" >&2
    exit 1
  fi
}

apply_patch_once() {
  local checkout=$1 patch_file=$2 expected_sha=$3
  local actual_sha
  actual_sha="$(shasum -a 256 "$patch_file" | awk '{print $1}')"
  [[ "$actual_sha" == "$expected_sha" ]] || {
    echo "patch identity mismatch: $patch_file" >&2
    exit 1
  }
  if git -C "$checkout" apply --reverse --check "$patch_file" >/dev/null 2>&1; then
    return
  fi
  if ! git -C "$checkout" apply --check "$patch_file"; then
    echo "Neither forward nor reverse patch matches: $patch_file" >&2
    git -C "$checkout" apply --reverse --check "$patch_file" || true
    exit 1
  fi
  git -C "$checkout" apply "$patch_file"
}

verify_patch_scope() {
  local checkout=$1 extra_allowed=$2
  shift 2
  local changed allowed patch_file
  allowed=""
  for patch_file in "$@"; do
    allowed+="$(awk '/^diff --git / {sub(/^b\//, "", $4); print $4} /^\+\+\+ b\// {sub(/^b\//, "", $2); print $2}' "$patch_file")"$'\n'
  done
  while IFS= read -r changed; do
    [[ -z "$changed" || "$changed" == "$extra_allowed" ]] && continue
    grep -Fqx "$changed" <<<"$allowed" || {
      echo "unexpected local dependency change: $checkout/$changed" >&2
      exit 1
    }
  done < <(git -C "$checkout" status --porcelain --untracked-files=all | sed -E 's/^.. //')
}

ensure_checkout \
  https://github.com/chrissotraidis/sunpad.git \
  "$ref/sunpad-reviewed" \
  efd42ca45457af5950e0558c66703cb766959e11
ensure_checkout \
  https://github.com/SMGCommunity/Petari.git \
  "$ref/petari" \
  845164b4faec4703002eb99b4b75ee1788204230
ensure_checkout \
  https://github.com/ExpansionPak/ModernGekko.git \
  "$ref/ModernGekko" \
  0514d9f03f8602809f66fc92fdca87d30e752997
ensure_checkout \
  https://github.com/ExpansionPak/ModernGekko-Template.git \
  "$ref/ModernGekko-Template" \
  1ee85bb5e09c38f493a09f5fa6e9dc8228b23e42

require_clean "$ref/sunpad-reviewed"
require_clean "$ref/petari"
require_clean "$ref/ModernGekko-Template"

git -C "$ref/ModernGekko" submodule update --init vendor/dolphin
actual_vendor="$(git -C "$ref/ModernGekko/vendor/dolphin" rev-parse HEAD)"
if [[ "$actual_vendor" != 13e492094902644b0d113c586300d358640f9e19 ]]; then
  echo "unexpected ModernGekko vendor revision: $actual_vendor" >&2
  exit 1
fi
git -C "$ref/ModernGekko/vendor/dolphin" remote set-url --push origin DISABLED

git -C "$ref/ModernGekko/vendor/dolphin" submodule update --init DolRecomp
actual_dolrecomp="$(git -C "$ref/ModernGekko/vendor/dolphin/DolRecomp" rev-parse HEAD)"
if [[ "$actual_dolrecomp" != fa0cf619e8d7eb8cba7eaf55267a12caaebb46aa ]]; then
  echo "unexpected DolRecomp revision: $actual_dolrecomp" >&2
  exit 1
fi
git -C "$ref/ModernGekko/vendor/dolphin/DolRecomp" remote set-url --push origin DISABLED

required_dolphin_submodules=(
  Externals/SDL/SDL Externals/SFML/SFML Externals/bzip2/bzip2
  Externals/cpp-optparse/cpp-optparse Externals/cubeb/cubeb
  Externals/curl/curl Externals/enet/enet Externals/fmt/fmt
  Externals/glslang/glslang Externals/hidapi/hidapi-src
  Externals/imgui/imgui Externals/implot/implot Externals/libspng/libspng
  Externals/libusb/libusb Externals/lz4/lz4
  Externals/minizip-ng/minizip-ng Externals/pugixml/pugixml
  Externals/spirv_cross/SPIRV-Cross Externals/tinygltf/tinygltf
  Externals/watcher/watcher Externals/xxhash/xxHash
  Externals/zlib-ng/zlib-ng Externals/zstd/zstd
)
git -C "$ref/ModernGekko/vendor/dolphin" submodule update --init \
  "${required_dolphin_submodules[@]}"
git -C "$ref/ModernGekko/vendor/dolphin/Externals/cubeb/cubeb" \
  submodule update --init --recursive

apple_patch="$ref/sunpad-reviewed/patches/ModernGekko/0001-sunpad-apple-runtime.patch"
dolphin_patch="$ref/sunpad-reviewed/patches/ModernGekko-dolphin/0001-sunpad-ios-runtime.patch"
headless_patch="$root/patches/ModernGekko/0002-headless-no-shader-wait.patch"
diagnostics_patch="$root/patches/ModernGekko/0003-runner-graphics-diagnostics.patch"
io_diagnostics_patch="$root/patches/ModernGekko/0004-runner-io-diagnostics.patch"
headless_audio_patch="$root/patches/ModernGekko/0005-headless-explicit-audio.patch"
cadence_diagnostics_patch="$root/patches/ModernGekko/0006-runner-cadence-diagnostics.patch"
rmge01_idle_patch="$root/patches/ModernGekko/0007-rmge01-staticrecomp-idle.patch"
module_cache_options_patch="$root/patches/ModernGekko/0008-module-cache-codegen-options.patch"
efb_frame_correlation_patch="$root/patches/ModernGekko/0009-efb-frame-correlation.patch"
phase_trace_hooks_patch="$root/patches/ModernGekko/0010-phase-trace-hooks.patch"
pgo_module_build_patch="$root/patches/ModernGekko/0011-profile-guided-module-build.patch"
native_resolution_default_patch="$root/patches/ModernGekko/0012-native-resolution-default.patch"
frontend_controls_patch="$root/patches/ModernGekko/0013-galaxypad-frontend-controls.patch"
frontend_progress_patch="$root/patches/ModernGekko/0027-frontend-launch-progress.patch"
frontend_progress_peeled=false
builtin_mods_patch="$root/patches/ModernGekko/0028-builtin-mod-descriptors.patch"
builtin_mods_peeled=false
[[ "$(shasum -a 256 "$builtin_mods_patch" | awk '{print $1}')" == \
  d198a24f168fd5b589552bcc9474468c70225ec2ec83a93bfdabe58f5eab37c9 ]] || exit 1
[[ "$(shasum -a 256 "$frontend_progress_patch" | awk '{print $1}')" == \
  c150fe4fd3feafa8583e23861872737a8e4b60972494a47f3c0b56b044635703 ]] || exit 1
module_source_patch="$root/patches/ModernGekko/0014-module-source-identity.patch"
fprf_policy_patch="$root/patches/ModernGekko/0015-rmge01-fprf-policy.patch"
thp_policy_patch="$root/patches/ModernGekko/0016-rmge01-thp-kernels.patch"
dcbz_policy_patch="$root/patches/ModernGekko/0021-dcbz-loop-policy.patch"
two_range_policy_patch="$root/patches/ModernGekko/0025-rmge01-two-range-policy.patch"
runtime_directories_patch="$root/patches/ModernGekko/0026-runtime-user-directories.patch"
runtime_directories_peeled=false
psq_scale_patch="$root/patches/ModernGekko-dolphin/0022-psq-store-scale.patch"
psq_scale_peeled=false
pointer_reacquisition_patch="$root/patches/ModernGekko-dolphin/0023-pointer-reacquisition.patch"
pointer_reacquisition_peeled=false
[[ "$(shasum -a 256 "$pointer_reacquisition_patch" | awk '{print $1}')" == \
  8310e45ac65c4743924f1edf902dc056da4d54fc8eee925a474d157c1443233d ]] || exit 1
audio_events_patch="$root/patches/experiments/audio-phase-events.patch"
audio_events_peeled=false
efb_context_patch="$root/patches/experiments/efb-live-read-context.patch"
efb_context_peeled=false
efb_dispatch_patch="$root/patches/experiments/efb-dispatch-timing.patch"
efb_dispatch_peeled=false
[[ "$(shasum -a 256 "$efb_dispatch_patch" | awk '{print $1}')" == \
  5226881b8ce0f00b0b2673b68f40040fa4490771d170aade1289db00ae19b638 ]] || exit 1
[[ "$(shasum -a 256 "$efb_context_patch" | awk '{print $1}')" == \
  4d5782faa59f0dc77bdc31c3bef75c2e8215088b427a308337bbfe21d410b775 ]] || exit 1
[[ "$(shasum -a 256 "$audio_events_patch" | awk '{print $1}')" == \
  d0f1d941e552e4baa85b9fe623922dcf8ded804d393708d3f4e321276d99bc89 ]] || exit 1
[[ "$(shasum -a 256 "$psq_scale_patch" | awk '{print $1}')" == \
  74ca7e8c82bf32d25af12bde4cf1b4318ceb7a34ad7e0925540e415227fd7486 ]] || exit 1
[[ "$(shasum -a 256 "$runtime_directories_patch" | awk '{print $1}')" == \
  eae4e6f3b8476354b5b05e9e006646cbca8ce1e4fe17597d2b6628f498aeb6a2 ]] || exit 1
[[ "$(shasum -a 256 "$two_range_policy_patch" | awk '{print $1}')" == \
  1a8378b059fc3ef9ff00285c23d491200ed404a2245ac789e90d8413c4d169bc ]] || exit 1
[[ "$(shasum -a 256 "$dcbz_policy_patch" | awk '{print $1}')" == \
  ef5ce417866cd67f6fd314f8585a6ea7716e50bcf824a044c4b8d4020c3c0e3b ]] || exit 1
vi_timing_patch="$root/patches/ModernGekko/0017-vi-timing-recorder.patch"
idle_recorder_patch="$root/patches/ModernGekko/0018-idle-wait-recorder.patch"
idle_wait_patch="$root/patches/ModernGekko-dolphin/0016-idle-wait-timing.patch"
completion_recorder_patch="$root/patches/ModernGekko/0019-completion-recorder.patch"
completion_timing_patch="$root/patches/ModernGekko-dolphin/0017-completion-timing.patch"
flight_runtime_patch="$root/patches/ModernGekko/0020-completion-flight.patch"
flight_core_patch="$root/patches/ModernGekko-dolphin/0018-completion-flight.patch"
dvd_runtime_patch="$root/patches/ModernGekko/0022-dvd-wait-recorder.patch"
dvd_core_patch="$root/patches/ModernGekko-dolphin/0019-dvd-wait-timing.patch"
dvd_runtime_peeled=false
dvd_core_peeled=false
gather_core_patch="$root/patches/ModernGekko-dolphin/0020-gather-wait-timing.patch"
gather_core_peeled=false
gather_runtime_patch="$root/patches/ModernGekko/0023-gather-wait-recorder.patch"
gather_runtime_peeled=false
wakeup_core_patch="$root/patches/ModernGekko-dolphin/0021-wakeup-notification-timing.patch"
wakeup_core_peeled=false
wakeup_runtime_patch="$root/patches/ModernGekko/0024-wakeup-recorder.patch"
wakeup_runtime_peeled=false
[[ "$(shasum -a 256 "$wakeup_runtime_patch" | awk '{print $1}')" == \
  2fab078afc255d0f278c476a3b86c67bef901aadc97962737c34f51558916350 ]] || exit 1
[[ "$(shasum -a 256 "$wakeup_core_patch" | awk '{print $1}')" == \
  a5478ac7b988642fe57a7f38d7ab242dacdfe6f66a9fe21806b589faf42c8bdd ]] || exit 1
[[ "$(shasum -a 256 "$gather_runtime_patch" | awk '{print $1}')" == \
  c8e58096449a7cb60843d21d38946d486ca484c35b63f060f4cdd189b93ca3e0 ]] || exit 1
[[ "$(shasum -a 256 "$gather_core_patch" | awk '{print $1}')" == \
  e17a99eb10881d6a68713806b4cdf1f1b38a49d483d65026b1bede8d4c6eadc9 ]] || exit 1
[[ "$(shasum -a 256 "$dvd_runtime_patch" | awk '{print $1}')" == \
  9ce037d4df807985ad626afa2fc6b967b07cc079998b3867c76d2b118c33bcd6 ]] || exit 1
[[ "$(shasum -a 256 "$dvd_core_patch" | awk '{print $1}')" == \
  22f1385f2d2ca5e667354b08daa8e33e3bb3e5ca85a6346fac617eec3a7caeba ]] || exit 1
empty_rel_patch="$root/patches/experiments/lc-empty-rel.patch"
[[ "$(shasum -a 256 "$empty_rel_patch" | awk '{print $1}')" == \
  94a970ed151b50fc1820f2850fcfce7f6164386240fa2fc68862a2dc312eb067 ]] || exit 1
[[ "$(shasum -a 256 "$flight_runtime_patch" | awk '{print $1}')" == \
  c72c94b29bb419f423218deb4a8d3fcb2762b911273dc0d64df20c187d6d3172 ]] || exit 1
[[ "$(shasum -a 256 "$flight_core_patch" | awk '{print $1}')" == \
  c40a8223d07fa85f0dccb33f13ed886f9c53b15ca60af5f1813598b31968466b ]] || exit 1
[[ "$(shasum -a 256 "$completion_recorder_patch" | awk '{print $1}')" == \
  01c931eb6103d5e0c0437231ee386a6ed5802dfca5c5c574dcd5006178e71186 ]] || exit 1
[[ "$(shasum -a 256 "$completion_timing_patch" | awk '{print $1}')" == \
  cba14f51f95284ab097a1b0d5aef6f99bb8dd6571bd7b7e8b39efd56bc5933c4 ]] || exit 1
[[ "$(shasum -a 256 "$idle_recorder_patch" | awk '{print $1}')" == \
  fd268ed85ae8ad14624ac402cc399b9a38f440b116a2bfa44322e30490c75967 ]] || exit 1
[[ "$(shasum -a 256 "$idle_wait_patch" | awk '{print $1}')" == \
  63970dcc657af8239d2ccf64da74cf88395721e5aaec945fedf88f9388e776c1 ]] || exit 1
[[ "$(shasum -a 256 "$vi_timing_patch" | awk '{print $1}')" == \
  c5a2da36a4de45e3a6c440ccd03593971649f9109f0cafa64cdae81536a02b6e ]] || exit 1
cpu_throttle_counter_patch="$root/patches/ModernGekko-dolphin/0015-cpu-throttle-counter.patch"
[[ "$(shasum -a 256 "$thp_policy_patch" | awk '{print $1}')" == \
  ef25620e8ec254b1c5eecf2bfa386ad60c06f085ac3cca0a1996cba611cf8f6f ]] || exit 1
fprf_helpers_patch="$root/patches/ModernGekko-dolphin/0014-deferred-fprf-helpers.patch"
[[ "$(shasum -a 256 "$fprf_policy_patch" | awk '{print $1}')" == \
  881996463a31728375b651b5cdf96f165f5a087ccc5c85d94851fc4a21421488 ]] || exit 1
[[ "$(shasum -a 256 "$fprf_helpers_patch" | awk '{print $1}')" == \
  661f2a2452e2240018140fedae6baaeea3b5c3e723d9266e3644f42581d1d019 ]] || exit 1
[[ "$(shasum -a 256 "$module_source_patch" | awk '{print $1}')" == \
  d3640ee79866a4a48482d90b44410a83d538c4b8be7fa72cc30b192e33278431 ]] || exit 1
dolphin_diagnostics_patch="$root/patches/ModernGekko-dolphin/0002-galaxypad-runtime-diagnostics.patch"
dolphin_diagnostics_header_patch="$root/patches/ModernGekko-dolphin/0003-galaxypad-diagnostics-header.patch"
dolphin_audio_reserve_patch="$root/patches/ModernGekko-dolphin/0004-apple-staticrecomp-audio-reserve.patch"
dolphin_indexed_tables_patch="$root/patches/ModernGekko-dolphin/0005-indexed-module-tables.patch"
dolphin_efb_frame_trace_patch="$root/patches/ModernGekko-dolphin/0006-efb-frame-trace.patch"
dolphin_phase_trace_patch="$root/patches/ModernGekko-dolphin/0007-phase-trace.patch"
dolphin_window_close_patch="$root/patches/ModernGekko-dolphin/0008-macos-window-close-shutdown.patch"
dolphin_pause_indicator_patch="$root/patches/ModernGekko-dolphin/0009-macos-pause-indicator.patch"
dolphin_sys_platform_patch="$root/patches/ModernGekko-dolphin/0010-apple-sys-platform.patch"
lc_pair_host_patch="$root/patches/experiments/lc-pair-host.patch"
[[ "$(shasum -a 256 "$lc_pair_host_patch" | awk '{print $1}')" == \
  87d3d595ff69f2619ce0a7dc90b290e6882b36e7dba5eb16f4946db9b4b950a1 ]] || exit 1

# The root overlays touch files introduced by the reviewed patches. Peel them
# briefly so each lower patch's idempotency check remains exact.
audio_output_patch="$root/patches/ModernGekko-dolphin/0030-remoteio-output-counters.patch"
[[ "$(shasum -a 256 "$audio_output_patch" | awk '{print $1}')" == \
  496f03aadca777baaefb46cf30842400c7051eeab54393b9dd9a475203448514 ]] || exit 1
audio_output_peeled=false
simulator_fetch_patch="$root/patches/ios-simulator-framebuffer-fetch.patch"
[[ "$(shasum -a 256 "$simulator_fetch_patch" | awk '{print $1}')" == \
  e64cd61170da314bd222f290647e67090195e384dcc54661a743f21179573447 ]] || exit 1
simulator_fetch_peeled=false
run_cost_patch="$root/patches/ModernGekko-dolphin/0029-sampled-run-cost.patch"
[[ "$(shasum -a 256 "$run_cost_patch" | awk '{print $1}')" == \
  8db2920cc54c923ff07bcda7b878308702db1e734023ea77e159fa6b72f5185c ]] || exit 1
run_cost_peeled=false
xf_origin_patch="$root/patches/ModernGekko-dolphin/0028-malformed-xf-origin.patch"
[[ "$(shasum -a 256 "$xf_origin_patch" | awk '{print $1}')" == \
  4f6eaad058addedd2ed7dd55123a9a6863cc90e6d8a652681ecc2986677411ec ]] || exit 1
xf_origin_peeled=false
direct_boundary_patch="$root/patches/ModernGekko-dolphin/0026-guarded-direct-call-boundary.patch"
fallback_pc_patch="$root/patches/ModernGekko-dolphin/0027-fallback-pc-histogram.patch"
direct_boundary_peeled=false
fallback_pc_peeled=false
headless_peeled=false
io_diagnostics_peeled=false
headless_audio_peeled=false
cadence_diagnostics_peeled=false
rmge01_idle_peeled=false
efb_frame_correlation_peeled=false
phase_trace_hooks_peeled=false
pgo_module_build_peeled=false
native_resolution_default_peeled=false
dolphin_diagnostics_peeled=false
dolphin_diagnostics_header_peeled=false
dolphin_audio_reserve_peeled=false
dolphin_efb_frame_trace_peeled=false
dolphin_phase_trace_peeled=false
dolphin_sys_platform_peeled=false
lc_pair_host_peeled=false
module_source_peeled=false
fprf_policy_peeled=false
thp_policy_peeled=false
dcbz_policy_peeled=false
two_range_policy_peeled=false
fprf_helpers_peeled=false
vi_timing_peeled=false
idle_recorder_peeled=false
idle_wait_peeled=false
completion_recorder_peeled=false
completion_timing_peeled=false
flight_runtime_peeled=false
flight_core_peeled=false
empty_rel_peeled=false
restore_overlay_patches() {
  if [[ "$dolphin_sys_platform_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$dolphin_sys_platform_patch" || true
  fi
  if [[ "$native_resolution_default_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$native_resolution_default_patch" || true
  fi
  if [[ "$frontend_controls_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$frontend_controls_patch" || true
  fi
  if [[ "$frontend_progress_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$frontend_progress_patch" || true
  fi
  if [[ "$pgo_module_build_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$pgo_module_build_patch" || true
  fi
  if [[ "$phase_trace_hooks_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$phase_trace_hooks_patch" || true
  fi
  if [[ "$headless_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$headless_patch" || true
  fi
  if [[ "$io_diagnostics_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$io_diagnostics_patch" || true
  fi
  if [[ "$headless_audio_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$headless_audio_patch" || true
  fi
  if [[ "$cadence_diagnostics_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$cadence_diagnostics_patch" || true
  fi
  if [[ "$rmge01_idle_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$rmge01_idle_patch" || true
  fi
  if [[ "$efb_frame_correlation_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$efb_frame_correlation_patch" || true
  fi
  if [[ "$dolphin_diagnostics_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$dolphin_diagnostics_patch" || true
  fi
  if [[ "$dolphin_diagnostics_header_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$dolphin_diagnostics_header_patch" || true
  fi
  if [[ "$dolphin_audio_reserve_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$dolphin_audio_reserve_patch" || true
  fi
  if [[ "$dolphin_efb_frame_trace_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$dolphin_efb_frame_trace_patch" || true
  fi
  if [[ "$dolphin_phase_trace_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$dolphin_phase_trace_patch" || true
  fi
  if [[ "$lc_pair_host_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$lc_pair_host_patch" || true
  fi
  if [[ "$module_source_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$module_source_patch" || true
  fi
  if [[ "$fprf_policy_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$fprf_policy_patch" || true
  fi
  if [[ "$thp_policy_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$thp_policy_patch" || true
  fi
  if [[ "$fprf_helpers_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$fprf_helpers_patch" || true
  fi
  if [[ "$vi_timing_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$vi_timing_patch" || true
  fi
  if [[ "$idle_recorder_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$idle_recorder_patch" || true
  fi
  if [[ "$idle_wait_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$idle_wait_patch" || true
  fi
  if [[ "$completion_timing_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$completion_timing_patch" || true
  fi
  if [[ "$completion_recorder_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$completion_recorder_patch" || true
  fi
  if [[ "$flight_core_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$flight_core_patch" || true
  fi
  if [[ "$flight_runtime_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$flight_runtime_patch" || true
  fi
  if [[ "$empty_rel_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$empty_rel_patch" || true
  fi
  if [[ "$dcbz_policy_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$dcbz_policy_patch" || true
  fi
  if [[ "$two_range_policy_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$two_range_policy_patch" || true
  fi
  if [[ "$dvd_runtime_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$dvd_runtime_patch" || true
  fi
  if [[ "$dvd_core_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$dvd_core_patch" || true
  fi
  if [[ "$gather_core_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$gather_core_patch" || true
  fi
  if [[ "$gather_runtime_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$gather_runtime_patch" || true
  fi
  if [[ "$wakeup_core_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$wakeup_core_patch" || true
  fi
  if [[ "$wakeup_runtime_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$wakeup_runtime_patch" || true
  fi
  if [[ "$runtime_directories_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$runtime_directories_patch" || true
  fi
  if [[ "$psq_scale_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$psq_scale_patch" || true
  fi
  if [[ "$pointer_reacquisition_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$pointer_reacquisition_patch" || true
  fi
  if [[ "$audio_events_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$audio_events_patch" || true
  fi
  if [[ "$efb_context_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$efb_context_patch" || true
  fi
  if [[ "$efb_dispatch_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$efb_dispatch_patch" || true
  fi
  if [[ "$builtin_mods_peeled" == true ]]; then
    git -C "$ref/ModernGekko" apply "$builtin_mods_patch" || true
  fi
  if [[ "$direct_boundary_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$direct_boundary_patch" || true
  fi
  if [[ "$fallback_pc_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$fallback_pc_patch" || true
  fi
  if [[ "$xf_origin_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$xf_origin_patch" || true
  fi
  if [[ "$run_cost_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$run_cost_patch" || true
  fi
  if [[ "$audio_output_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$audio_output_patch" || true
  fi
  if [[ "$simulator_fetch_peeled" == true ]]; then
    git -C "$ref/ModernGekko/vendor/dolphin" apply "$simulator_fetch_patch" || true
  fi
}
frontend_controls_peeled=false
trap restore_overlay_patches EXIT
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$simulator_fetch_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$simulator_fetch_patch"
  simulator_fetch_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$audio_output_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$audio_output_patch"
  audio_output_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$run_cost_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$run_cost_patch"
  run_cost_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$xf_origin_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$xf_origin_patch"
  xf_origin_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$fallback_pc_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$fallback_pc_patch"
  fallback_pc_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$direct_boundary_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$direct_boundary_patch"
  direct_boundary_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$builtin_mods_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$builtin_mods_patch"
  builtin_mods_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$pointer_reacquisition_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$pointer_reacquisition_patch"
  pointer_reacquisition_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$efb_dispatch_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$efb_dispatch_patch"
  efb_dispatch_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$efb_context_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$efb_context_patch"
  efb_context_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$audio_events_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$audio_events_patch"
  audio_events_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$psq_scale_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$psq_scale_patch"
  psq_scale_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$frontend_progress_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$frontend_progress_patch"
  frontend_progress_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$runtime_directories_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$runtime_directories_patch"
  runtime_directories_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$wakeup_runtime_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$wakeup_runtime_patch"
  wakeup_runtime_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$wakeup_core_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$wakeup_core_patch"
  wakeup_core_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$gather_runtime_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$gather_runtime_patch"
  gather_runtime_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$gather_core_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$gather_core_patch"
  gather_core_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$dvd_runtime_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$dvd_runtime_patch"
  dvd_runtime_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$dvd_core_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$dvd_core_patch"
  dvd_core_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$two_range_policy_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$two_range_policy_patch"
  two_range_policy_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$dcbz_policy_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$dcbz_policy_patch"
  dcbz_policy_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$empty_rel_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$empty_rel_patch"
  empty_rel_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$flight_runtime_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$flight_runtime_patch"
  flight_runtime_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$flight_core_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$flight_core_patch"
  flight_core_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$completion_recorder_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$completion_recorder_patch"
  completion_recorder_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$completion_timing_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$completion_timing_patch"
  completion_timing_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$idle_recorder_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$idle_recorder_patch"
  idle_recorder_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$idle_wait_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$idle_wait_patch"
  idle_wait_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$vi_timing_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$vi_timing_patch"
  vi_timing_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$thp_policy_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$thp_policy_patch"
  thp_policy_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$fprf_policy_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$fprf_policy_patch"
  fprf_policy_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$fprf_helpers_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$fprf_helpers_patch"
  fprf_helpers_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$module_source_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$module_source_patch"
  module_source_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$lc_pair_host_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$lc_pair_host_patch"
  lc_pair_host_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$frontend_controls_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$frontend_controls_patch"
  frontend_controls_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$dolphin_sys_platform_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$dolphin_sys_platform_patch"
  dolphin_sys_platform_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$native_resolution_default_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$native_resolution_default_patch"
  native_resolution_default_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$pgo_module_build_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$pgo_module_build_patch"
  pgo_module_build_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$phase_trace_hooks_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$phase_trace_hooks_patch"
  phase_trace_hooks_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$efb_frame_correlation_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$efb_frame_correlation_patch"
  efb_frame_correlation_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$rmge01_idle_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$rmge01_idle_patch"
  rmge01_idle_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$cadence_diagnostics_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$cadence_diagnostics_patch"
  cadence_diagnostics_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$headless_audio_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$headless_audio_patch"
  headless_audio_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$io_diagnostics_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$io_diagnostics_patch"
  io_diagnostics_peeled=true
fi
if git -C "$ref/ModernGekko" apply --reverse --check "$headless_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko" apply --reverse "$headless_patch"
  headless_peeled=true
fi

apply_patch_once "$ref/ModernGekko" "$apple_patch" \
  aa06ac920002fc94f8f96f684309f291e6b8cb882c694f894a9226d100abadbe
apply_patch_once "$ref/ModernGekko" "$headless_patch" \
  60d60d41d792c426f428fc3aaf2fce57962d870cefb181cee7fba90846948ce0
apply_patch_once "$ref/ModernGekko" "$diagnostics_patch" \
  db85b6f6eceab1e3f0d9663f04f0dc5fc5745993d6ee546242865c1fc06978f0
apply_patch_once "$ref/ModernGekko" "$io_diagnostics_patch" \
  69a455e348f79246519a511944b8ed691660d3eea5fae0fd42dfdf7aacfdd79d
apply_patch_once "$ref/ModernGekko" "$headless_audio_patch" \
  ca5b3908ecc2312cf04a0295274d8a3155d0f7013b17dd947f9616ffa7a73ef7
apply_patch_once "$ref/ModernGekko" "$cadence_diagnostics_patch" \
  73dbe799b0d878edba640ffced0bcb9a0d1451427719371e2d7761c3001d57eb
apply_patch_once "$ref/ModernGekko" "$rmge01_idle_patch" \
  f432d83b07ffbb11a66d3ef4da10ff7d8a01718099def9a3cb6b3578a55d53d7
apply_patch_once "$ref/ModernGekko" "$module_cache_options_patch" \
  03de37c00dee2d4920be17b9489834556c86676606a6b8ce85c3f8da7a714845
apply_patch_once "$ref/ModernGekko" "$efb_frame_correlation_patch" \
  4acf23252cc91ed60fd6e69a6ec740f4da882aa42764c576f5bbda63ea6a1531
apply_patch_once "$ref/ModernGekko" "$phase_trace_hooks_patch" \
  fc402fa49ba044a70db2ad91bab83d952669c23afa71d5efd70a77dd36e83a81
apply_patch_once "$ref/ModernGekko" "$pgo_module_build_patch" \
  da9578771b6ccfe1c70918ecd973c19e7c76925601a082b2826e8e1ef5fe7c0f
apply_patch_once "$ref/ModernGekko" "$native_resolution_default_patch" \
  9078f60d32584fb7c79ab3757a790674f7712e03e415425f4c19c27c8d6b13c9
apply_patch_once "$ref/ModernGekko" "$frontend_controls_patch" \
  8304632c1cc9dbb81e1c56dbc87f328a91c2bef824737127a6cfa1bf78653891
frontend_controls_peeled=false

# Startup feedback layers on the nonblocking frontend child monitor.
apply_patch_once "$ref/ModernGekko" "$frontend_progress_patch" \
  c150fe4fd3feafa8583e23861872737a8e4b60972494a47f3c0b56b044635703
frontend_progress_peeled=false

# Source fingerprint overlays the port's existing codegen/profile cache key.
apply_patch_once "$ref/ModernGekko" "$module_source_patch" \
  d3640ee79866a4a48482d90b44410a83d538c4b8be7fa72cc30b192e33278431
module_source_peeled=false
apply_patch_once "$ref/ModernGekko" "$fprf_policy_patch" \
  881996463a31728375b651b5cdf96f165f5a087ccc5c85d94851fc4a21421488
fprf_policy_peeled=false
apply_patch_once "$ref/ModernGekko" "$thp_policy_patch" \
  ef25620e8ec254b1c5eecf2bfa386ad60c06f085ac3cca0a1996cba611cf8f6f
thp_policy_peeled=false
apply_patch_once "$ref/ModernGekko" "$dcbz_policy_patch" \
  ef5ce417866cd67f6fd314f8585a6ea7716e50bcf824a044c4b8d4020c3c0e3b
dcbz_policy_peeled=false
apply_patch_once "$ref/ModernGekko" "$two_range_policy_patch" \
  1a8378b059fc3ef9ff00285c23d491200ed404a2245ac789e90d8413c4d169bc
two_range_policy_peeled=false
headless_peeled=false
apply_patch_once "$ref/ModernGekko" "$vi_timing_patch" \
  c5a2da36a4de45e3a6c440ccd03593971649f9109f0cafa64cdae81536a02b6e
vi_timing_peeled=false
apply_patch_once "$ref/ModernGekko" "$idle_recorder_patch" \
  fd268ed85ae8ad14624ac402cc399b9a38f440b116a2bfa44322e30490c75967
idle_recorder_peeled=false
apply_patch_once "$ref/ModernGekko" "$completion_recorder_patch" \
  01c931eb6103d5e0c0437231ee386a6ed5802dfca5c5c574dcd5006178e71186
completion_recorder_peeled=false
apply_patch_once "$ref/ModernGekko" "$flight_runtime_patch" \
  c72c94b29bb419f423218deb4a8d3fcb2762b911273dc0d64df20c187d6d3172
flight_runtime_peeled=false
io_diagnostics_peeled=false
apply_patch_once "$ref/ModernGekko" "$dvd_runtime_patch" \
  9ce037d4df807985ad626afa2fc6b967b07cc079998b3867c76d2b118c33bcd6
dvd_runtime_peeled=false
apply_patch_once "$ref/ModernGekko" "$gather_runtime_patch" \
  c8e58096449a7cb60843d21d38946d486ca484c35b63f060f4cdd189b93ca3e0
gather_runtime_peeled=false
apply_patch_once "$ref/ModernGekko" "$wakeup_runtime_patch" \
  2fab078afc255d0f278c476a3b86c67bef901aadc97962737c34f51558916350
wakeup_runtime_peeled=false
headless_audio_peeled=false
cadence_diagnostics_peeled=false
rmge01_idle_peeled=false
efb_frame_correlation_peeled=false
phase_trace_hooks_peeled=false
pgo_module_build_peeled=false
native_resolution_default_peeled=false
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$dolphin_phase_trace_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$dolphin_phase_trace_patch"
  dolphin_phase_trace_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$dolphin_efb_frame_trace_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$dolphin_efb_frame_trace_patch"
  dolphin_efb_frame_trace_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$dolphin_audio_reserve_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$dolphin_audio_reserve_patch"
  dolphin_audio_reserve_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$dolphin_diagnostics_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$dolphin_diagnostics_patch"
  dolphin_diagnostics_peeled=true
fi
if git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse --check "$dolphin_diagnostics_header_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin" apply --reverse "$dolphin_diagnostics_header_patch"
  dolphin_diagnostics_header_peeled=true
fi
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_patch" \
  b872dfe002d3d106af92f5dbc3dfcd3d20c43358e7681084ad41ee367cad214a
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_diagnostics_header_patch" \
  e4498014739c15a102ce0e86729f69d7b06e4b1c97fb3ba8a93b47f3bc1757af
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_diagnostics_patch" \
  17b48cebc5eb1e5f372dda98d0885705bb47d2329ce84ccfa1b809104b118dd0
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_audio_reserve_patch" \
  984481b78034018c67ed2f0ed79c8b86833045a159f47ab924c17af483bffbfe
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_indexed_tables_patch" \
  6afff9e65b5ef0664e8a71e11d359f8abb772c806f6b35a96765630c577810c8
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_efb_frame_trace_patch" \
  e21fdd2bc2c01df20c671e0e2fdf452e7c2f75a1e7acb76df659a20500498cd2
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_phase_trace_patch" \
  a9b9ad03be58554a984e91310bcecd996fa90e3c9bea43fee97915ea28f18d55
dolphin_diagnostics_peeled=false
dolphin_diagnostics_header_peeled=false
dolphin_audio_reserve_peeled=false
dolphin_efb_frame_trace_peeled=false
dolphin_phase_trace_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_window_close_patch" \
  11b547780a986bc3fc7ec1078491ddb7b3e48b40cd92a14d3d4b97452cde9f0f
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_pause_indicator_patch" \
  a23f92e1a6a4a00aeaa4107c2952a63bbff0905315945f058e9e9515386f0d5c
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dolphin_sys_platform_patch" \
  9c065043c15f941a73705d7809ab5e0a90a145ad7bd304346507aad80150b6d9
dolphin_sys_platform_peeled=false
pixel_store_trace_patch="$root/patches/ModernGekko-dolphin/0011-pixel-store-trace.patch"
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$pixel_store_trace_patch" \
  5f49e731e9c72d6231fe2030c31db7b9a5b60e77a9d16b456597987e1118e023
lc_byte_fast_patch="$root/patches/ModernGekko-dolphin/0012-lc-byte-fast.patch"
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$lc_byte_fast_patch" \
  d980680c30fda3e54593930d6815d78ead4c78cd26a9b074f77fbac77394f126
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$lc_pair_host_patch" \
  87d3d595ff69f2619ce0a7dc90b290e6882b36e7dba5eb16f4946db9b4b950a1
lc_pair_host_peeled=false
apply_patch_once "$ref/ModernGekko" "$root/patches/ModernGekko/0029-mod-address-fast-reject.patch" \
  53a3823a06ac00a090065f54a030915110ffbdf997398d36242b52d69845e6c1
apply_patch_once "$ref/ModernGekko" "$root/patches/ModernGekko/0030-mod-dispatch-fast-reject.patch" \
  bba8bb0eaab1664fd78230e979d7baa1d559d37606f99802b6da07b467de349e
verify_patch_scope "$ref/ModernGekko" vendor/dolphin \
  "$root/patches/ModernGekko/0030-mod-dispatch-fast-reject.patch" \
  "$root/patches/ModernGekko/0029-mod-address-fast-reject.patch" \
  "$builtin_mods_patch" \
  "$frontend_progress_patch" \
  "$apple_patch" "$runtime_directories_patch" "$two_range_policy_patch" "$headless_patch" "$diagnostics_patch" "$io_diagnostics_patch" \
  "$headless_audio_patch" "$cadence_diagnostics_patch" "$rmge01_idle_patch" \
  "$module_cache_options_patch" "$efb_frame_correlation_patch" "$phase_trace_hooks_patch" \
  "$pgo_module_build_patch" "$native_resolution_default_patch" "$frontend_controls_patch" "$module_source_patch" "$fprf_policy_patch" "$thp_policy_patch" "$vi_timing_patch" "$idle_recorder_patch" "$completion_recorder_patch" "$flight_runtime_patch" "$dcbz_policy_patch" "$dvd_runtime_patch" "$gather_runtime_patch" "$wakeup_runtime_patch"
lc_pair_runtime_patch="$root/patches/ModernGekko-dolphin/0013-lc-pair-runtime.patch"
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$lc_pair_runtime_patch" \
  d05dda85e73b20f41f7042b1a6df2476fc30c971664c922ccfd7bd6f66483975
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$fprf_helpers_patch" \
  661f2a2452e2240018140fedae6baaeea3b5c3e723d9266e3644f42581d1d019
fprf_helpers_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$cpu_throttle_counter_patch" \
  15ae34e6ad58c5d3995aa1b8591b041f5bc405ddc7ab901366bcac3d8a47f68f
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$idle_wait_patch" \
  63970dcc657af8239d2ccf64da74cf88395721e5aaec945fedf88f9388e776c1
idle_wait_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$completion_timing_patch" \
  cba14f51f95284ab097a1b0d5aef6f99bb8dd6571bd7b7e8b39efd56bc5933c4
completion_timing_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$flight_core_patch" \
  c40a8223d07fa85f0dccb33f13ed886f9c53b15ca60af5f1813598b31968466b
flight_core_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$dvd_core_patch" \
  22f1385f2d2ca5e667354b08daa8e33e3bb3e5ca85a6346fac617eec3a7caeba
dvd_core_peeled=false
[[ "$(shasum -a 256 "$ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu.c" | awk '{print $1}')" == \
  1350d1196b38b147477890ef0dc59d5d9e389a55a169d51913fc033be34edb69 ]] || exit 1
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$empty_rel_patch" \
  94a970ed151b50fc1820f2850fcfce7f6164386240fa2fc68862a2dc312eb067
empty_rel_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$gather_core_patch" \
  e17a99eb10881d6a68713806b4cdf1f1b38a49d483d65026b1bede8d4c6eadc9
gather_core_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$wakeup_core_patch" \
  a5478ac7b988642fe57a7f38d7ab242dacdfe6f66a9fe21806b589faf42c8bdd
wakeup_core_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$psq_scale_patch" \
  74ca7e8c82bf32d25af12bde4cf1b4318ceb7a34ad7e0925540e415227fd7486
psq_scale_peeled=false
[[ "$(shasum -a 256 "$ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu.c" | awk '{print $1}')" == \
  05e221c01bead6801c51217f84398bd10f22e1b810f6d06977e04d8a801436ea ]] || exit 1
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$audio_events_patch" \
  d0f1d941e552e4baa85b9fe623922dcf8ded804d393708d3f4e321276d99bc89
audio_events_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$efb_context_patch" \
  4d5782faa59f0dc77bdc31c3bef75c2e8215088b427a308337bbfe21d410b775
efb_context_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$efb_dispatch_patch" \
  5226881b8ce0f00b0b2673b68f40040fa4490771d170aade1289db00ae19b638
efb_dispatch_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$pointer_reacquisition_patch" \
  8310e45ac65c4743924f1edf902dc056da4d54fc8eee925a474d157c1443233d
pointer_reacquisition_peeled=false
xf_context_patch="$root/patches/ModernGekko-dolphin/0024-malformed-xf-context.patch"
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$xf_context_patch" \
  8ae3658143fc2f7cfaf3e2f35f48a1921d81b09088ebbf8e4607429902d94ab4
checkpoint_undo_patch="$root/patches/ModernGekko-dolphin/0025-development-checkpoint-undo-release.patch"
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$checkpoint_undo_patch" \
  d35867c46664e050bd3184672e5811a544f36781020fe53ea68c8add0b6dcb9e
direct_boundary_patch="$root/patches/ModernGekko-dolphin/0026-guarded-direct-call-boundary.patch"
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$direct_boundary_patch" \
  f9c905b4e0f23e5a39989825bd583c678dd3c0a114315a56c25079c2ce34f408
direct_boundary_peeled=false
fallback_pc_patch="$root/patches/ModernGekko-dolphin/0027-fallback-pc-histogram.patch"
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$fallback_pc_patch" \
  0d46c23073de589bf9fcb8e28c59e5dd3634301feab58197d6b8f7122f640cd4
fallback_pc_peeled=false
xf_origin_patch="$root/patches/ModernGekko-dolphin/0028-malformed-xf-origin.patch"
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$xf_origin_patch" \
  4f6eaad058addedd2ed7dd55123a9a6863cc90e6d8a652681ecc2986677411ec
xf_origin_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$run_cost_patch" \
  8db2920cc54c923ff07bcda7b878308702db1e734023ea77e159fa6b72f5185c
run_cost_peeled=false
apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$audio_output_patch" \
  496f03aadca777baaefb46cf30842400c7051eeab54393b9dd9a475203448514
audio_output_peeled=false
cmp "$root/apple/shared/GalaxyPadAudioOutputCounters.h" \
  "$ref/ModernGekko/vendor/dolphin/Source/Core/Common/GalaxyPadAudioOutputCounters.h"
if [[ "$simulator_fetch_peeled" == true ]]; then
  apply_patch_once "$ref/ModernGekko/vendor/dolphin" "$simulator_fetch_patch" \
    e64cd61170da314bd222f290647e67090195e384dcc54661a743f21179573447
  simulator_fetch_peeled=false
fi
verify_patch_scope "$ref/ModernGekko/vendor/dolphin" "DolRecomp" \
  "$simulator_fetch_patch" "$audio_output_patch" "$run_cost_patch" "$xf_origin_patch" "$fallback_pc_patch" "$direct_boundary_patch" "$checkpoint_undo_patch" "$xf_context_patch" \
  "$wakeup_core_patch" "$psq_scale_patch" "$audio_events_patch" "$pointer_reacquisition_patch" \
  "$efb_context_patch" \
  "$efb_dispatch_patch" \
  "$dolphin_patch" "$dolphin_diagnostics_patch" "$dolphin_diagnostics_header_patch" \
  "$dolphin_audio_reserve_patch" "$dolphin_indexed_tables_patch" \
  "$dolphin_efb_frame_trace_patch" "$dolphin_phase_trace_patch" "$dolphin_window_close_patch" \
  "$dolphin_pause_indicator_patch" "$dolphin_sys_platform_patch" "$pixel_store_trace_patch" \
  "$lc_byte_fast_patch" "$lc_pair_host_patch" "$lc_pair_runtime_patch" "$fprf_helpers_patch" "$cpu_throttle_counter_patch" "$idle_wait_patch" "$completion_timing_patch" "$flight_core_patch" "$empty_rel_patch" "$dvd_core_patch" "$gather_core_patch"
cntlzw_patch="$root/patches/DolRecomp/0001-cntlzw-intrinsic.patch"
# R86 did not justify promoting this experiment. Migrate an existing experimental
# checkout back to the pinned emitter; preserve and reject any unrelated edits.
[[ "$(shasum -a 256 "$cntlzw_patch" | awk '{print $1}')" == \
  93a3d55a6a3a28380abe351d7528fb059a2d2fee2f0d4b96aac9e5ce7fd3b551 ]] || exit 1
if git -C "$ref/ModernGekko/vendor/dolphin/DolRecomp" apply --reverse --check "$cntlzw_patch" >/dev/null 2>&1; then
  git -C "$ref/ModernGekko/vendor/dolphin/DolRecomp" apply --reverse "$cntlzw_patch"
fi
midblock_cycles_patch="$root/patches/DolRecomp/0002-midblock-entry-cycles.patch"
# Cycle accounting is a correctness fix, separate from the rejected CNTLZW
# experiment. The running package stays unchanged until candidate validation.
apply_patch_once "$ref/ModernGekko/vendor/dolphin/DolRecomp" "$midblock_cycles_patch" \
  99b2e3b16dd5df387f2fdcaa57250de717657eadd717598b0cf22bc9cbf7e11e
verify_patch_scope "$ref/ModernGekko/vendor/dolphin/DolRecomp" "" "$midblock_cycles_patch"

apply_patch_once "$ref/ModernGekko" "$runtime_directories_patch" \
  eae4e6f3b8476354b5b05e9e006646cbca8ce1e4fe17597d2b6628f498aeb6a2
runtime_directories_peeled=false
apply_patch_once "$ref/ModernGekko" "$builtin_mods_patch" \
  d198a24f168fd5b589552bcc9474468c70225ec2ec83a93bfdabe58f5eab37c9
builtin_mods_peeled=false
trap - EXIT
echo "GalaxyPad public references are pinned and the reviewed Apple patches are applied."

# Candidate-only extension; no changes to the shared upstream module template.
function(galaxypad_add_native_observer)
  if(NOT TARGET gRMGE01_recomp OR NOT GALAXYPAD_OBSERVER_ROOT)
    message(FATAL_ERROR "GalaxyPad observer requires the exact candidate target/root")
  endif()
  target_sources(gRMGE01_recomp PRIVATE
    "${GALAXYPAD_OBSERVER_ROOT}/apple/shared/GalaxyPadNativeObserver.c")
  set_source_files_properties(
    "${GALAXYPAD_OBSERVER_ROOT}/apple/shared/GalaxyPadNativeObserver.c" PROPERTIES
    COMPILE_DEFINITIONS "GALAXYPAD_OBSERVER_CPU_HEADER=\"core/cpu.h\";GALAXYPAD_OBSERVER_CPU_ABI=GXRUNTIME_CPU_ABI_VERSION")
endfunction()
cmake_language(DEFER CALL galaxypad_add_native_observer)

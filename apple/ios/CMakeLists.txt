cmake_minimum_required(VERSION 3.22)
project(GalaxyPadIOS LANGUAGES C CXX OBJCXX)
get_filename_component(ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
string(TOLOWER "${CMAKE_OSX_SYSROOT}" SDK_ROOT_LOWER)
if(SDK_ROOT_LOWER MATCHES "iphonesimulator")
  set(GALAXYPAD_SDK iphonesimulator)
  set(GALAXYPAD_LANE ios-simulator)
elseif(SDK_ROOT_LOWER MATCHES "iphoneos")
  set(GALAXYPAD_SDK iphoneos)
  set(GALAXYPAD_LANE ios-device)
else()
  message(FATAL_ERROR "GalaxyPad requires an iPhoneOS or iPhoneSimulator SDK")
endif()
set(CORE_BUILD "${ROOT}/generated/build/${GALAXYPAD_LANE}-core")
file(READ "${ROOT}/config/galaxypad-disc.json" DISC_IDENTITY)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${ROOT}/config/galaxypad-disc.json")
string(JSON GALAXYPAD_IMAGE_SHA256 GET "${DISC_IDENTITY}" container sha256)
string(JSON GALAXYPAD_IMAGE_BYTES GET "${DISC_IDENTITY}" container sizeBytes)
string(JSON GALAXYPAD_DOL_SHA256 GET "${DISC_IDENTITY}" executables 0 sha256)
configure_file(../shared/GalaxyPadDiscIdentity.h.in GalaxyPadDiscIdentity.h @ONLY)
add_executable(GalaxyPad MACOSX_BUNDLE main.mm GalaxyPadCoreHost.mm GalaxyPadMetalView.mm
  ../shared/GalaxyPadInputDevice.cpp GalaxyPadGameOverlay.mm ../shared/GalaxyPadSettings.mm
  ../shared/GalaxyPadDiagnostics.mm GalaxyPadReportViewController.mm GalaxyPadAboutViewController.mm GalaxyPadControllers.mm
  ../shared/GalaxyPadControllerMappingStore.mm GalaxyPadDiscExtractor.mm GalaxyPadImportTransaction.mm)
option(GALAXYPAD_ENABLE_NATIVE_THP "Compile private opt-in native THP candidate" OFF)
if(GALAXYPAD_ENABLE_NATIVE_THP)
  if(NOT GALAXYPAD_SDK STREQUAL "iphonesimulator")
    message(FATAL_ERROR "Native THP candidate is currently Simulator validation only")
  endif()
  set(THP_DEP "${ROOT}/generated/tools/ffmpeg-thp-${GALAXYPAD_SDK}/ffmpeg-8.0.1")
  foreach(lib avcodec avutil)
    if(NOT EXISTS "${THP_DEP}/lib${lib}/lib${lib}.a")
      message(FATAL_ERROR "Run scripts/build-thp-dependency.sh first")
    endif()
    target_link_libraries(GalaxyPad PRIVATE "${THP_DEP}/lib${lib}/lib${lib}.a")
  endforeach()
  target_sources(GalaxyPad PRIVATE ../shared/GalaxyPadTHPDecoder.c
    ../shared/GalaxyPadTHPGuest.c ../shared/GalaxyPadTHPPatch.c
    ../shared/GalaxyPadTHPTransform.c ../shared/GalaxyPadTHPMod.c)
  # FFmpeg's root has a file named "version"; never shadow C++ <version>.
  target_include_directories(GalaxyPad PRIVATE "$<$<COMPILE_LANGUAGE:C>:${THP_DEP}>")
  target_compile_definitions(GalaxyPad PRIVATE GALAXYPAD_ENABLE_NATIVE_THP=1)
endif()
# Local diagnostic builds only. Explicit object precedes the core archive so
# its Metal definitions are used instead of pulling the original archive member.
set(GALAXYPAD_DIAGNOSTIC_METAL_OBJECT "" CACHE FILEPATH "Optional isolated Metal staging probe object")
set(GALAXYPAD_DIAGNOSTIC_TRACKER_OBJECT "" CACHE FILEPATH "Optional isolated Metal completion handler probe object")
foreach(probe IN ITEMS GALAXYPAD_DIAGNOSTIC_METAL_OBJECT GALAXYPAD_DIAGNOSTIC_TRACKER_OBJECT)
if(${probe})
  if(NOT EXISTS "${${probe}}")
    message(FATAL_ERROR "Missing diagnostic Metal object")
  endif()
  target_sources(GalaxyPad PRIVATE "${${probe}}")
  target_link_options(GalaxyPad PRIVATE "-Wl,-map,${CMAKE_CURRENT_BINARY_DIR}/metal-probe-link.map")
endif()
endforeach()
set_target_properties(GalaxyPad PROPERTIES
  CXX_STANDARD 23 OBJCXX_STANDARD 23
  CXX_STANDARD_REQUIRED YES OBJCXX_STANDARD_REQUIRED YES
  MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/Info.plist.in")
if(CMAKE_OSX_ARCHITECTURES STREQUAL "arm64")
  # CoreHost's diagnostic CPU-state reader uses the same header ABI as the core.
  set_property(SOURCE GalaxyPadCoreHost.mm APPEND PROPERTY COMPILE_DEFINITIONS
    _ARCH_64=1 _M_ARM_64=1)
endif()
target_compile_options(GalaxyPad PRIVATE $<$<COMPILE_LANGUAGE:OBJCXX>:-fobjc-arc>
  -fblocks -Wall -Wextra)
target_include_directories(GalaxyPad PRIVATE
  "${CMAKE_CURRENT_BINARY_DIR}"
  "${ROOT}/ref/ModernGekko/include"
  "${ROOT}/ref/ModernGekko/vendor/dolphin/GXRuntime/include"
  "${ROOT}/ref/ModernGekko/vendor/dolphin/Source/Core"
  "${ROOT}/ref/ModernGekko/vendor/dolphin/Externals/fmt/fmt/include"
  "${CORE_BUILD}/vendor/dolphin/Source/Core")
target_link_libraries(GalaxyPad PRIVATE
  "${ROOT}/generated/ios/${GALAXYPAD_SDK}/libs/libGalaxyPadCore.a"
  z bz2 iconv resolv compression)
foreach(FRAMEWORK UIKit Foundation Metal MetalKit GameController CoreGraphics
  QuartzCore CoreText Security AudioToolbox SystemConfiguration CoreMedia
  CoreVideo CoreMotion CoreHaptics UniformTypeIdentifiers AVFAudio)
  target_link_libraries(GalaxyPad PRIVATE "-framework ${FRAMEWORK}")
endforeach()
# Public Dolphin runtime resources, not extracted game assets. The iOS platform
# resolves Sys relative to the app bundle (including post-processing shaders).
add_custom_target(GalaxyPadResources ALL
  COMMAND "${CMAKE_COMMAND}" -E copy_directory
    "${ROOT}/ref/ModernGekko/vendor/dolphin/Data/Sys"
    "$<TARGET_BUNDLE_DIR:GalaxyPad>/Sys"
  DEPENDS GalaxyPad)

# Compile the original universal icon for both device families before signing.
# Run on incremental builds too, so artwork edits cannot leave stale icons.
find_package(Python3 REQUIRED COMPONENTS Interpreter)
add_custom_target(GalaxyPadIcons ALL
  COMMAND "${Python3_EXECUTABLE}" "${ROOT}/scripts/compile-ios-icons.py"
    --bundle "$<TARGET_BUNDLE_DIR:GalaxyPad>" --sdk "${GALAXYPAD_SDK}"
  DEPENDS GalaxyPad
  VERBATIM)

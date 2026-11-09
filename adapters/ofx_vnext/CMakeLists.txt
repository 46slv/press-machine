cmake_minimum_required(VERSION 3.20)
project(PressMachineVNext LANGUAGES CXX RC)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
set(RESOLVE_OFX_SDK "C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/OpenFX" CACHE PATH "Resolve bundled OpenFX SDK")
set(SUPPORT "${RESOLVE_OFX_SDK}/Support")
set(LIBRARY
 "${SUPPORT}/Library/ofxsCore.cpp" "${SUPPORT}/Library/ofxsImageEffect.cpp"
 "${SUPPORT}/Library/ofxsInteract.cpp" "${SUPPORT}/Library/ofxsLog.cpp"
 "${SUPPORT}/Library/ofxsMultiThread.cpp" "${SUPPORT}/Library/ofxsParams.cpp"
 "${SUPPORT}/Library/ofxsProperty.cpp" "${SUPPORT}/Library/ofxsPropertyValidation.cpp")
set(PTX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../vnext/generated/Kernel.ptx")
configure_file(src/KernelResource.rc.in "${CMAKE_CURRENT_BINARY_DIR}/KernelResource.rc" @ONLY)
add_library(PressMachineVNext MODULE src/Plugin.cpp src/CudaRunner.cpp ${LIBRARY} "${CMAKE_CURRENT_BINARY_DIR}/KernelResource.rc")
target_include_directories(PressMachineVNext PRIVATE "${RESOLVE_OFX_SDK}/OpenFX-1.4/include" "${SUPPORT}/include" "../vnext/generated")
target_compile_definitions(PressMachineVNext PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
target_compile_options(PressMachineVNext PRIVATE /fp:strict /O2 /W3)
set_target_properties(PressMachineVNext PROPERTIES PREFIX "" OUTPUT_NAME "PressMachineVNext" SUFFIX ".ofx"
 RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/PressMachineVNext.ofx.bundle/Contents/Win64"
 LIBRARY_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/PressMachineVNext.ofx.bundle/Contents/Win64"
 RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/PressMachineVNext.ofx.bundle/Contents/Win64"
 LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/PressMachineVNext.ofx.bundle/Contents/Win64")
target_link_libraries(PressMachineVNext PRIVATE shell32 ole32)
add_library(PressMachineVNextParity SHARED tests/Native.cpp)
target_include_directories(PressMachineVNextParity PRIVATE "../vnext/generated")
target_compile_options(PressMachineVNextParity PRIVATE /fp:strict /O2 /W3)
add_library(PressMachineVNextCudaAdapterTest SHARED tests/CudaAdapterHarness.cpp src/CudaRunner.cpp "${CMAKE_CURRENT_BINARY_DIR}/KernelResource.rc")
target_include_directories(PressMachineVNextCudaAdapterTest PRIVATE "../vnext/generated")
target_compile_definitions(PressMachineVNextCudaAdapterTest PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
target_compile_options(PressMachineVNextCudaAdapterTest PRIVATE /fp:strict /O2 /W3)

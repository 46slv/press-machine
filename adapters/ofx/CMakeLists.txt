cmake_minimum_required(VERSION 3.20)
project(PressMachineV3CurveDev LANGUAGES CXX RC)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
set(RESOLVE_OFX_SDK "C:/ProgramData/Blackmagic Design/DaVinci Resolve/Support/Developer/OpenFX" CACHE PATH "Resolve bundled OpenFX SDK")
set(SUPPORT "${RESOLVE_OFX_SDK}/Support")
set(LIBRARY
 "${SUPPORT}/Library/ofxsCore.cpp" "${SUPPORT}/Library/ofxsImageEffect.cpp"
 "${SUPPORT}/Library/ofxsInteract.cpp" "${SUPPORT}/Library/ofxsLog.cpp"
 "${SUPPORT}/Library/ofxsMultiThread.cpp" "${SUPPORT}/Library/ofxsParams.cpp"
 "${SUPPORT}/Library/ofxsProperty.cpp" "${SUPPORT}/Library/ofxsPropertyValidation.cpp")
configure_file(THIRD_PARTY_NOTICES.txt "${CMAKE_BINARY_DIR}/PressMachineV3CurveDev.ofx.bundle/Contents/Resources/THIRD_PARTY_NOTICES.txt" COPYONLY)
set(PTX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/generated/Kernel.ptx")
configure_file(src/KernelResource.rc.in "${CMAKE_CURRENT_BINARY_DIR}/KernelResource.rc" @ONLY)
add_library(PressMachine MODULE src/Plugin.cpp src/CudaRunner.cpp ${LIBRARY} "${CMAKE_CURRENT_BINARY_DIR}/KernelResource.rc")
target_include_directories(PressMachine PRIVATE "${RESOLVE_OFX_SDK}/OpenFX-1.4/include" "${SUPPORT}/include")
target_compile_definitions(PressMachine PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
target_compile_options(PressMachine PRIVATE /fp:strict /O2 /W3)
set_target_properties(PressMachine PROPERTIES PREFIX "" OUTPUT_NAME "PressMachineV3CurveDev" SUFFIX ".ofx"
 RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/PressMachineV3CurveDev.ofx.bundle/Contents/Win64"
 LIBRARY_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/PressMachineV3CurveDev.ofx.bundle/Contents/Win64"
 RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/PressMachineV3CurveDev.ofx.bundle/Contents/Win64"
 LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/PressMachineV3CurveDev.ofx.bundle/Contents/Win64")
add_library(PressMachineParity SHARED tests/NativeV3.cpp)
target_compile_options(PressMachineParity PRIVATE /fp:strict /O2 /W3)

add_library(PressMachineCudaAdapterTest SHARED tests/CudaAdapterHarness.cpp src/CudaRunner.cpp "${CMAKE_CURRENT_BINARY_DIR}/KernelResource.rc")
target_compile_definitions(PressMachineCudaAdapterTest PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
target_compile_options(PressMachineCudaAdapterTest PRIVATE /fp:strict /O2 /W3)

target_link_libraries(PressMachine PRIVATE shell32 ole32)
add_executable(PressMachineTraceTests tests/TraceTests.cpp)
target_include_directories(PressMachineTraceTests PRIVATE "${RESOLVE_OFX_SDK}/OpenFX-1.4/include")
target_compile_definitions(PressMachineTraceTests PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
target_compile_options(PressMachineTraceTests PRIVATE /W3)
target_link_libraries(PressMachineTraceTests PRIVATE shell32 ole32)

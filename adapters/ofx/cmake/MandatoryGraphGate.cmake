# No option to disable: this is a dependency of the product even in direct builds.
function(pressmachine_require_graph target source_root)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)
  add_custom_target(PressMachineGraphGate
    COMMAND "${Python3_EXECUTABLE}" "${source_root}/tests/verify_graph_gate.py" --root "${source_root}"
    COMMENT "Checking mandatory OFX Graph wiring"
    VERBATIM)
  add_dependencies(${target} PressMachineGraphGate)
endfunction()

# Explicit bundle root; fixed path is checked against the actual linked target.
function(pressmachine_bind_graph_package target source_root bundle_root)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)
  add_custom_command(TARGET ${target} POST_BUILD
    COMMAND "${Python3_EXECUTABLE}" "${source_root}/tests/graph_package_binding.py"
      --root "${source_root}" --bundle "${bundle_root}" --target "$<TARGET_FILE:${target}>"
    COMMENT "Binding Graph source gate to the linked product binary"
    VERBATIM)
endfunction()

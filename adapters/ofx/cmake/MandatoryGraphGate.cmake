# No option to disable: this is a dependency of the product even in direct builds.
function(pressmachine_require_graph target source_root)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)
  add_custom_target(PressMachineGraphGate
    COMMAND "${Python3_EXECUTABLE}" "${source_root}/tests/verify_graph_gate.py" --root "${source_root}"
    COMMENT "Checking mandatory OFX Graph wiring"
    VERBATIM)
  add_dependencies(${target} PressMachineGraphGate)
endfunction()

cat > generated.wait_runs_and_export_system.tcl << EOF 
open_project build_system/system.xpr

wait_on_runs impl_1

file copy -force ./build_system/system.gen/sources_1/bd/system/hw_handoff/system.hwh ./generated.system.$struct_id.hwh
file copy -force ./build_system/system.runs/impl_1/system_wrapper.bit ./generated.system.$struct_id.bit

exit
EOF

vivado -mode tcl -source generated.wait_runs_and_export_system.tcl -nojournal -log generated.wait_and_export_system.log

rm generated.wait_runs_and_export_system.tcl

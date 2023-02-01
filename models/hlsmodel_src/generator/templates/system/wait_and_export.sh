cat > generated.wait_runs_and_export_system.tcl << EOF 
open_project build_system/system.xpr

wait_on_runs impl_1

write_hw_platform -fixed -include_bit -force -file ./generated.system.$struct_id.xsa

exit
EOF

vivado -mode tcl -source generated.wait_runs_and_export_system.tcl -nojournal -log wait_and_export_system.log

rm generated.wait_runs_and_export_system.tcl

# ============================================================
#  Toy Saturnin — APN_ANF S-box Synthesis Script
#  Synthesizes APN_ANF.v to gate-level netlist
#  Generates reports for area, power, and timing
# ============================================================

# ---------- Library Setup ----------
# set_db lib_search_path {/home/sahiba/test/Downloads}
set_db library uk65lscllmvbbh_120c25_tc.lib
set_db hdl_search_path /


# ---------- Read Design ----------
read_hdl APN_ANF.v
elaborate APN_ANF
current_design APN_ANF

# ---------- Synthesis ----------
# High-effort mapping and optimization
synthesize -to_mapped -effort high

# ---------- Output Directory ----------
file mkdir reports
file mkdir netlist

# ---------- Write Netlist ----------
write_hdl > netlist/APN_ANF_netlistT.v

# ---------- Reports ----------
report area            > reports/APN_ANF_areaT.rep
report power           > reports/APN_ANF_powerT.rep
report timing -unconstrained > reports/APN_ANF_timingT.rep
report messages        > reports/APN_ANF_messageT.rep

# ---------- Optional: Save Design Database ----------
write_db netlist/APN_ANF_synth.db

# ---------- Summary ----------
puts "\n=============================================="
puts "✅ Synthesis Completed for APN_ANF"
puts "   Netlist:  netlist/APN_ANF_netlistT.v"
puts "   Reports:  reports/"
puts "==============================================\n"

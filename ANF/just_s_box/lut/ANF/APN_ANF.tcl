#set_db lib_search_path /home/sahiba/test/Downloads
set_db library uk65lscllmvbbh_120c25_tc.lib
set_db hdl_search_path /


read_hdl APN_ANF.v
elaborate APN_ANF
current_design APN_ANF
synthesize APN_ANF -to_mapped -effort high
write_hdl > APN_ANF_netlistT.v
report area  > APN_ANF_areaT.rep
report power > APN_ANF_powerT.rep
report messages > APN_ANF_messageT.rep
report timing -unconstrained > APN_ANF_timingT.rep




##########################################################################################
# CONFIGS.PY
#
# User configurations. Edit LOG_DIR and DATA_DIR to reflect preferences on the local
# filesystem.
##########################################################################################
LOG_DIR = "/Users/leecarlaw/scripts/bufkit/logs"            # Log file location
DATA_DIR = "/Users/leecarlaw/scripts/bufkit/data"           # BUFKIT data location

##########################################################################################
# Static configurations. Generally do not edit.
##########################################################################################
QUERY_URL = "https://meteor.geol.iastate.edu/~ckarsten/bufkit/data"
run_info = {
    'RAP': [3, 9, 15, 21],
    'HRRR': [0, 6, 12, 18]
}

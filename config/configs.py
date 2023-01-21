##########################################################################################
# CONFIGS.PY
#
# User configurations. Edit LOG_DIR and DATA_DIR to reflect preferences on the local
# filesystem.
##########################################################################################
LOG_DIR = "/Users/leecarlaw/scripts/bufkit-extended/logs"            # Log file location
DATA_DIR = "/Users/leecarlaw/scripts/bufkit-extended/data"           # BUFKIT data location

##########################################################################################
# Static configurations. Generally do not edit.
##########################################################################################
QUERY_URL = {
    "rap": {
        "IEM": "https://meteor.geol.iastate.edu/~ckarsten/bufkit/data/rap/rap_kord.buf",
        "PSU": "http://www.meteo.psu.edu/bufkit/data/RAP/latest/rap_kord.buf"
    },
    
    "hrrr": {
        "IEM": "https://meteor.geol.iastate.edu/~ckarsten/bufkit/data/hrrr/hrrr_kord.buf",
        "PSU": "http://www.meteo.psu.edu/bufkit/data/HRRR/latest/hrrr_kord.buf"
    }   
}

URLS = {
    "IEM": "https://mtarchive.geol.iastate.edu", 
    "PSU": "http://www.meteo.psu.edu/bufkit/data"
}

run_info = {
    'RAP': [3, 9, 15, 21],
    'HRRR': [0, 6, 12, 18]
}

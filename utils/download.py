from datetime import datetime, timedelta
import time
import socket
try:
    import urllib2 as requests           # Python 2.x
    from urllib2 import HTTPError, URLError
    type_ = 'py2'
except ImportError:
    import urllib.request as requests    # Python 3.x
    from urllib.error import HTTPError, URLError
    type_ = 'py3'
import re

from utils.log import logfile
from config.configs import DATA_DIR, QUERY_URL, run_info

log = logfile('download.log')
def read_header(url):
    """
    Read the STID, STNM, and TIME line from a .buf file at a specific URL and return the
    model cycle time.

    Parameters:
    -----------
    url: string
        URL to a .buf file

    Returns:
    --------
    cycle: datetime
        The cycle time of this .buf file. If not found, returns a None object.

    """
    cycle = None
    reg_string = "TIME = [\d]{6}\/[\d]{4}"
    try:
        data = requests.urlopen(url, timeout=1).read(300)
        data = data.decode('utf-8')
        cycle_string = re.findall(reg_string, data)
        if len(cycle_string) > 0:
            cycle = datetime.strptime(cycle_string[0][-11:], '%y%m%d/%H00')
        else:
            log.error("Missing data for: %s" % (url))
    except HTTPError:
        log.error("Error accessing: %s" % (url))
    except URLError:
        log.error("Socket timed out accessing: %s" % (url))
    except socket.timeout as e:
        log.error("Socket error %s" % (e))
    except socket.error as e:
        log.error("Socket error %s" % (e))
    return cycle

def find_closest_cycle(latest_cycle, extended_cycles):
    """
    Find the closest extended model cycle.

    Parameters:
    -----------
    latest_cycle: datetime
        The current BUFKIT model cycle available
    extended_cycles: list
        List of hours corresponding to the extended runs for this particular model.
        Defined in configs.config.py in `run_info` variable

    Returns:
    --------
    dt: datetime
        The closest extended model cycle to latest_cycle.

    """
    # Probably a cleaner way to do this. Too lazy to figure it out and only performed
    # once each download cycle.
    delta = 0
    nearest_found = False
    while delta <= 24 and not nearest_found:
        dt = latest_cycle - timedelta(hours=delta)
        if dt.hour in extended_cycles:
            nearest_found = True
        delta += 1
    return dt

def execute_download(url):
    """
    Helper function to download the requested data. Passed into pool.map for parallel
    thredded processes.

    Parameters:
    -----------
    url: string
        URL to BUFKIT data for downloading.

    """
    # Since Python 2.x doesn't support the pool.starmap function, instead of passing
    # multiple arguments, parse out the model and site id from the requested url.
    sep = url.rfind('_')
    dot = url.rfind('.')
    slash = url.rfind('/')
    id_ = url[sep+1:dot]
    model = url[slash+1:sep]
    filename = "%s/%sLONG_%s.buf" % (DATA_DIR, model.upper(), id_)

    if type_ == 'py3':
        requests.urlretrieve(url, filename)
    elif type_ == 'py2':
        filedata = requests.urlopen(url).read()
        with open(filename, 'wb') as f: f.write(filedata)
    time.sleep(0.25)

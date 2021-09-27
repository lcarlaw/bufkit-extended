import argparse
from multiprocessing import Pool, freeze_support
from functools import partial
from datetime import datetime, timedelta
import os
try:
    from shutil import which
except ImportError:
    from distutils.spawn import find_executable as which

from utils.download import read_header, find_closest_cycle, execute_download
from utils.log import logfile
from utils.timing import timeit
from config.configs import DATA_DIR, QUERY_URL, run_info
from config.sites import IDS

log = logfile('download.log')
curr_pwd = os.path.dirname(os.path.realpath(__file__))

@timeit
def download_bufkit(model='RAP', num_procs=1):
    """
    Query the PSU BUFKIT Data Distribution System for the latest available extended run
    of the RAP or HRRR. If data is found, download to the local filesystem.

    Parameters:
    -----------
    model: string
        Model to download extended BUFKIT data form. Default, RAP
    num_procs: int
        Number of parallel processes to use for downloading. Default, 1

    """
    model = model.lower()
    extended_cycles = run_info[model.upper()]
    curr_time = datetime.utcnow()

    # Vanguard site to test latest available model cycle
    latest_cycle = read_header("%s/%s/%s_kord.buf" % (QUERY_URL, model, model))
    log.info("Latest available %s cycle: %s" % (model, latest_cycle))

    # Determine the closest extended run and check to see if this exists locally already
    target_cycle = find_closest_cycle(latest_cycle, extended_cycles)
    log.info("target_cycle extended cycle is: %s" % (target_cycle))
    download_flag = True
    try:
        with open("%s/latest_%s.txt" % (curr_pwd, model), 'r') as f:
            local_cycle = f.readlines()[0]
            if local_cycle == target_cycle.strftime("%Y%m%d%H"):
                download_flag = False
                log.info("Data exists locally. Exiting download.")
    except (OSError, IOError):
        log.info("latest_%s file not found. Continuing with download" % (model))

    if download_flag:
        urls = []
        for id in IDS:
            id = id.lower()
            filename = "%s/%sLONG_%s.buf" % (DATA_DIR, model.upper(), id)
            url_1 = "%s/%s/%s/%s_%s.buf" % ('http://www.meteo.psu.edu/bufkit/data',
                                             model.upper(), target_cycle.strftime('%H'),
                                             model, id)
            url_2 = "%s/%s/bufkit/%s/%s/%s_%s.buf" % ('https://mtarchive.geol.iastate.edu',
                                                       target_cycle.strftime('%Y/%m/%d'),
                                                       target_cycle.strftime('%H'),
                                                       model, model, id)

            # URL status checking. Primary (PSU) and Secondary (IEM) webfarms
            status = read_header(url_1)
            if status is not None:
                urls.append(url_1)
                log.info("Good URL status for: %s" % (id))
            else:
                status = read_header(url_2)
                if status is not None:
                    urls.append(url_2)
                    log.info("Good secondary URL status for: %s" % (id))

            # Write information about the latest long term run to the local filesystem
            if status is not None:
                with open("%s/latest_%s.txt" % (curr_pwd, model.lower()), 'w') as f:
                    f.write(target_cycle.strftime('%Y%m%d%H'))

        # Send to processing pool for downloading.
        pool = Pool(num_procs)
        pool.map(execute_download, urls)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-m', '--model', dest='model', default='RAP', help='Model to download\
                    bufkit `long range` data for. [Options: RAP | HRRR]')
    ap.add_argument('-n', '--num_procs', dest='num_procs', default=1,
                    help='Number of parallel processes to launch.')
    args = ap.parse_args()

    log.info("----> New download processing")
    download_bufkit(model=args.model, num_procs=int(args.num_procs))

if __name__ == '__main__':
    freeze_support()                # For multiprocessing.pool to run
    main()

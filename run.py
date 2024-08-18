import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
#from multiprocessing import Pool, freeze_support
import os, sys
from datetime import datetime 

from utils.download import read_header, find_closest_cycle, execute_download
from utils.log import logfile
from utils.timing import timeit
from config.configs import QUERY_URL, URLS, run_info
from config.sites import IDS

log = logfile(f"{datetime.utcnow().strftime('%Y%m%d')}.log")
curr_pwd = os.path.dirname(os.path.realpath(__file__))

def make_url(source, model, target_cycle, id_):
    """
    Returns the url string for a given source, model type, id, and runtime. Cleaning up
    the code a bit. 
    """
    url = (
        f"{URLS['PSU']}/{model.upper()}/{target_cycle.strftime('%H')}/"
        f"{model}_{id_}.buf"
    )
    if source == "IEM":
        url = (
            f"{URLS['IEM']}/{target_cycle.strftime('%Y/%m/%d')}/bufkit/"
            f"{target_cycle.strftime('%H')}/{model}/{model}_{id_}.buf"
        )
    return url 

@timeit
def download_bufkit(model='RAP', num_threads=20):
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
    current_time = datetime.utcnow()
    model = model.lower()
    extended_cycles = run_info[model.upper()]

    # Vanguard site to test latest available model cycle and set the download source
    log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    log.info("Determining download source")
    log.info(f"Testing the PSU datafeed and looking for latest available run")
    latest_cycle_psu = read_header(QUERY_URL[model]['PSU'], current_time)
    log.info(f"Latest PSU cycle: {latest_cycle_psu}")

    log.info(f"Testing the IEM datafeed and looking for latest available run")
    latest_cycle_iem = read_header(QUERY_URL[model]['IEM'], current_time)
    log.info(f"Latest IEM cycle: {latest_cycle_iem}")

    # Test both the PSU and IEM datafeeds for existence of the closest target extended 
    # datafiles
    latest_extended_psu = None 
    latest_extended_iem = None
    if latest_cycle_psu is not None:
        latest_extended_psu = find_closest_cycle(latest_cycle_psu, extended_cycles)
        url = make_url('PSU', model, latest_extended_psu, 'kord')
        latest_extended_psu = read_header(url, current_time)
    if latest_cycle_iem is not None:
        latest_extended_iem = find_closest_cycle(latest_cycle_iem, extended_cycles)
        url = make_url('IEM', model, latest_extended_iem, 'kord')
        latest_extended_iem = read_header(url, current_time)
        
    # Both sites return good status
    if latest_extended_psu is not None and latest_extended_iem is not None: 
        latest_cycle, source = latest_extended_psu, "PSU"
        if latest_extended_iem > latest_extended_psu:
            latest_cycle, source = latest_extended_iem, "IEM"
    
    # PSU returns bad status
    elif latest_extended_psu is None and latest_extended_iem is not None:
        latest_cycle, source = latest_extended_iem, "IEM"
    
    # IEM returns bad status
    elif latest_extended_psu is not None and latest_extended_iem is None:
        latest_cycle, source = latest_extended_psu, "PSU"
    
    # Both bad status
    else:
        log.error(
            f"Unable to access both the IEM nad PSU datafeeds. "
            f"Script will exit now. Sorry. NO BUFKIT DATA FOR YOU!"
        )
        sys.exit(1)
    
    ####################################################################################
    # Begin download process
    ####################################################################################
    # Determine the closest extended run and check to see if this exists locally
    target_cycle = find_closest_cycle(latest_cycle, extended_cycles)
    log.info(f"target_cycle extended cycle is: {target_cycle} from: {source}")
    download_flag = True

    latest_file = f"{curr_pwd}/latest_{model}.txt"
    if Path(latest_file).is_file():
        with open(f"{curr_pwd}/latest_{model}.txt", 'r') as f:
            local_cycle = f.readlines()[0]
            if local_cycle == target_cycle.strftime("%Y%m%d%H"):
                download_flag = False
                log.info("Data exists locally. Exiting download.")
    else: 
        log.info(f"latest_{model} file not found. Continuing with download")

    '''
    # Check which source (if any) has the desired extended model cycle.
    if download_flag:
        if latest_cycle != target_cycle:
            sources = list(URLS.keys())
            if sources[0] != source: sources.reverse()
            for source in sources:
                log.info(f"Testing the {source} feed for the {target_cycle} {model} run")
                url = make_url(source, model, target_cycle, 'kord')
                status = read_header(url, current_time)
                if status == target_cycle:
                    log.info(f"[GOOD] status for {source}")
                    break
                else:
                    log.info(f"[BAD] status for {source}")
        
            if status is not None:
                log.info(f"Using {source} feed for BUFKIT download. Proceeding.")
            else:
                log.error(f"[BAD] status for both IEM & PSU sources for {target_cycle}")
                log.error("Scripts exiting in error.")
                sys.exit(1)
    '''
    log.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    urls = []
    if download_flag:
        for id_ in IDS:
            id_ = id_.lower()
            urls.append(make_url(source, model, target_cycle, id_))

        # Write information about the latest long term run to the local filesystem
        with open("%s/latest_%s.txt" % (curr_pwd, model.lower()), 'w') as f:
            f.write(target_cycle.strftime('%Y%m%d%H'))

        # Send to processing pool for downloading. 
        log.info(f"Initializing {num_threads} threads via ThreadPoolExecutor")
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            executor.map(execute_download, urls)
            executor.shutdown(wait=True)

        # Multiprocessing...was much slower. 
        #pool = Pool(num_procs)
        #pool.map(execute_download, urls)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-m', '--model', dest='model', default='RAP', help='Model to download\
                    bufkit `long range` data for. [Options: RAP | HRRR]')
    ap.add_argument('-n', '--num_threads', dest='num_threads', default=20,
                    help='Number of parallel threads to launch. Default is 20')
    args = ap.parse_args()

    log.info("########################################################################")
    log.info(f"New download processing by user: {os.getlogin()}")
    download_bufkit(model=args.model, num_threads=int(args.num_threads))

if __name__ == '__main__':
    #freeze_support()
    main()

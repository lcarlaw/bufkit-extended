# bufkit-extended
This repo downloads bufkit files for the extended runs of the HRRR and RAP from the PSU BUFKIT Data Distribution System (backup is IEM). This allows forecasters to continue using this extended guidance even after new "regular" runs come in which would otherwise overwrite these.

## Codebase
The codebase is setup as follows:

```bash
├── bufkit-extended
│   ├── config
│   │   ├── configs.py  --> General configurations
│   │   ├── sites.py    --> Sites to download
│   ├── utils
│   │   ├── download.py --> Downloading/header check and error logging functions
│   │   ├── log.py      --> Logging function
│   │   ├── timing.py   --> Simple timing decorator function
├── run.py              --> Driver script
```

## Setup and Usage Notes
Either clone this repository or download the zipped folder from github. To clone of your local machine:

```
git clone https://github.com/lcarlaw/bufkit-extended.git
```

In the `config/configs.py` file, change the `LOG_DIR` and `DATA_DIR` variables to reflect where log files and downloaded `.buf` files will be stored on the local filesystem. You'll be greeted with various runtime errors if these paths aren't set correctly. 

In the `config/sites.py` file, add site identifiers for the files to be downloaded. There is a poorly-written helper function in `config` called `id_finder.py` that will look for sites within a pre-set lat/lon box. Not optimized, so it's very slow. 

### Running
Command-line usage is as follows:

```
python run.py [ -m MODEL ] [ -n NUM_THREADS ]
```

* `MODEL` is one of either `RAP` or `HRRR` (upper or lower case) or blank. Not specifying the `-m` flag will default to downloading RAP files.
* `NUM_THREADS` represents the number of parallel threads to launch. Defaults to 20 without the `-n` flag.

For example, specifying:

```
python run.py -m HRRR 
````

will spawn 20 processes to download bufkit files for the latest extended run of the HRRR for all sites listed in the `configs/sites.py` file.

In order to avoid re-downloading data that already exists (i.e. when script is on a cron), after a successful download, a file called `latest_RAP.txt` or `latest_HRRR.txt` will be output to the scripts top-level directory storing the latest available run on the filesystem.

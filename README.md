# bufkit-extended
This repo downloads bufkit files for the extended runs of the HRRR and RAP from the PSU BUFKIT Data Distribution System (backup is IEM). This allows forecasters to continue using this extended guidance even after new "regular" runs come in.

Codebase is compatible with both `urllib2` (Python 2.x) and `urllib.requests` (Python 3.x). Probably better to build in support for WGET and/or cURL.

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
└── .gitignore
```

## Setup and Usage Notes
Either clone this repository or download the zipped folder from github. To clone of your local machine:

```
git clone https://github.com/lcarlaw/bufkit-extended.git
```

In the `config/configs.py` file, change the `LOG_DIR` and `DATA_DIR` variables to reflect where log files and downloaded `.buf` files will be stored on the local filesystem. You'll be greeted with various runtime errors if these paths aren't set correctly. 

In the `config/sites.py` file, add site identifiers for the files to be downloaded.

### Running
Command-line usage is as follows:

```
python run.py [ -m MODEL ] [ -n NUM_PROCS ]
```

* `MODEL` is one of either `RAP` or `HRRR` (upper or lower case) or blank. Not specifying the `-m` flag will default to downloading RAP files.
* `NUM_PROCS` represents the number of parallel processes to launch. Defaults to 1 without the `-n` flag.

For example, specifying:

```
python run.py -m HRRR -n 8
````

will spawn 8 processes to download bufkit files for the latest extended run of the HRRR for all sites listed in the `configs/sites.py` file.

In order to avoid re-downloading data that already exists (i.e. when script is on a cron), after a successful download, a file called `latest_RAP.txt` or `latest_HRRR.txt` will be output to the scripts top-level directory storing the latest available run on the filesystem.

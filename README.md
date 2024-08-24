This script changes runway numbers directly in MSFS 2020 BGL files.

List runway changes in `runways.csv`, configure the script, then run `python rename_runways.py`.

#### Configuration
Set via command argument or in the top section of `rename_runways.py`  
`-x` / `TEST_MODE` : when true only outputs details without actually changing the BGL files  
`-r` / `MSFS_ROOT` : root path of the MSFS data folder (the folder that contains the `Official` and `Community` folders)  
`-b` / `BACKUP_DIR` : backups BGLs in this directory if they are inside the MSFS data folder and no backup already exists at the backup directory. Use `""` / `None` to disable backup

`runways.csv` format (separated by `;`):
* path to BGL file (can use the placeholder <msfs>, which will be substituted with the configered root path of the MSFS data folder)
* ICAO ident of the airport
* Old runway number, incl. optional designator and leading 0 (e.g. `03L`, `15`)
* New runway number, incl. optional designator and leading 0 (e.g. `03L`, `15`)

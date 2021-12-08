#### Installation
From the command line:
```bash
pip install git+https://github.com/dag-hammarskjold-library/ods-api
```

#### Classes
> #### ODS
Usage (Python):
```python
from ods_api import ODS

# Download and save to disk
ODS.download('A/RES/74/1', 'E', 'saved_as.pdf')

# Download into memory and get the file object
fileobj = ODS.download('A/RES/74/1', 'E')
```

#### Scripts
> #### ods-dlx
Gets files from ODS and imports them into DLX. 

Credentials do not need to be supplied if AWS cerentials are found locally.

Usage (command line):
```bash
ods-dlx --help
```
```bash
ods-dlx --symbol A/RES/74/1
```
```bash
ods-dlx --list list_of_symbols.txt
```
```bash
# the symbol in ODS differs from the symbol in UNBIS:
ods-dlx --symbol A/74/PV.1 --ods_symbol A/74/PV.1(OR)
```

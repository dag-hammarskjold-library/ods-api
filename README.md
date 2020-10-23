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
Gets files from ODS and imports them into DLX

Usage (command line):
```bash
ods-dlx --help
```
```bash
ods-dlx --symbol=A/RES/74/1 --dlx_connect=<MDB connection string> --s3_key=<AWS key> --s3_key_id=<AWS key id> --s3_bucket=undl-files
```
```bash
ods-dlx --list=list_of_symbols.txt --dlx_connect=<MDB connection string> --s3_key=<AWS key> --s3_key_id=<AWS key id> --s3_bucket=undl-files
```

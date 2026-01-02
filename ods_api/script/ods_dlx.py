import os, logging, re, time
from datetime import datetime, timedelta
from boto3 import client as aws_client
from argparse import ArgumentParser
from pymongo.collation import Collation
from dlx import DB as DLX
from dlx.marc import Bib, Query, Condition, Or
from dlx.file import File, Identifier, S3, FileExists, FileExistsLanguageConflict, FileExistsIdentifierConflict
from dlx.util import ISO6391
from ods_api import ODS, FileNotFound

logging.basicConfig(level=logging.INFO)

LANG = {'A': 'AR', 'C': 'ZH', 'E': 'EN', 'F': 'FR', 'R': 'RU', 'S': 'ES', 'O': 'DE'} 

def get_args():
    ap = ArgumentParser()

    m = ap.add_mutually_exclusive_group(required=True)
    m.add_argument('--symbol', help='The official symbol (as written in UNBIS)')
    m.add_argument('--list', help='Text file with a list of symbols')
    
    ap.add_argument('--ods_symbol', help='The symbol used by ODS if it differs from the official symbol')
    ap.add_argument('--language', help='ODS language code')
    ap.add_argument('--overwrite', action='store_true')
    ap.add_argument('--skip_check', action='store_true')
    
    # get from AWS if not provided
    ssm = aws_client('ssm', region_name='us-east-1')
    
    def param(name):
        return None if os.environ.get('DLX_DL_TESTING') else ssm.get_parameter(Name=name)['Parameter']['Value']
        
    c = ap.add_argument_group('credentials', description='these arguments are automatically supplied by AWS SSM if AWS credentials are configured')
    c.add_argument('--connect', default=param('prodISSU-admin-connect-string'), help='MongoDB connection string')
    c.add_argument('--database', default=param('prodISSU-admin-database-name'), help='Database name')
    c.add_argument('--s3_bucket', default=param('dlx-s3-bucket'), help='S3 bucket')
    
    return ap.parse_args()

def run():
    args = get_args()
    
    DLX.connect(args.connect, database=args.database)
    S3.connect(bucket=args.s3_bucket)
    
    symbols = [args.symbol] if args.symbol else [re.split('\t', x)[0].strip() for x in open(args.list).readlines()]
    langs = [args.language] if args.language else LANG.keys()
    
    for sym in symbols:
        bib = Bib.from_query(Query(Or(Condition('191', {'a': sym}), Condition('191', {'z': sym}))))

        if not bib and not args.skip_check:
            logging.warning(f'Bib for document {sym} not found. Skipping.')
            continue
        elif bib and not args.skip_check:
            # capture symbols from the bib record
            ids = bib.get_values('191', 'a') + bib.get_values('191', 'z')
        else:
            logging.warning(f'Bib for document {sym} not found with --skip_check enabled. Using {sym} as identifier')
            ids = symbols
        
        for lang in langs:
            started = datetime.now()
            logging.info(f'Getting {sym} {lang} ...')
                
            try:
                fh = ODS.download(sym if not args.ods_symbol else args.ods_symbol, lang)
            except FileNotFound:
                logging.warning(f'{sym} {lang} not found in ODS')
                time.sleep(.5)
                continue
            except Exception as e:
                logging.warning(e)
                time.sleep(.5)
                continue
                
            isolang = LANG[lang]
            
            try:
                result = File.import_from_handle(
                    fh,
                    filename=File.encode_fn(sym, isolang, 'pdf'),
                    identifiers=[Identifier('symbol', s) for s in ids],
                    languages=[isolang],
                    mimetype='application/pdf',
                    source='ods-importx',
                    overwrite=args.overwrite
                )
                logging.info(f'OK - {result.id}')
            except FileExistsLanguageConflict as e:
                logging.warning(f'{e.message} X {isolang}')
            except FileExistsIdentifierConflict as e:
                logging.warning(f'{e.message} X {ids}')
            except FileExists:
                logging.info('Already in the system')
            except:
                raise
        
            #if (datetime.now() - started) < timedelta(seconds=.5):
            #    time.sleep(.5)
    
###

if __name__ == '__main__':
    run()
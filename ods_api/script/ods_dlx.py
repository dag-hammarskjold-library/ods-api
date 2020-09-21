import logging
from argparse import ArgumentParser
from dlx import DB as DLX
from dlx.file import File, Identifier, S3, FileExists, FileExistsLanguageConflict, FileExistsIdentifierConflict
from dlx.util import ISO6391
from ods_api import ODS, FileNotFound

logging.basicConfig(level=logging.INFO)

LANG = {'A': 'AR', 'C': 'ZH', 'E': 'EN', 'F': 'FR', 'R': 'RU', 'S': 'ES', 'O': 'DE'} 

def get_args():
    ap = ArgumentParser()
    
    ap.add_argument('--dlx_connect', required=True)
    ap.add_argument('--s3_key_id', required=True)
    ap.add_argument('--s3_key', required=True)
    ap.add_argument('--s3_bucket', required=True)
    ap.add_argument('--symbol')
    ap.add_argument('--list')
    ap.add_argument('--language', help='ODS language code')
    ap.add_argument('--overwrite', action='store_true')
    
    return ap.parse_args()

def run():
    args = get_args()
    
    DLX.connect(args.dlx_connect)
    S3.connect(args.s3_key_id, args.s3_key, args.s3_bucket)
    
    symbols = [args.symbol] if args.symbol else [f.strip() for f in open(args.list).readlines()]
    langs = [args.language] if args.language else LANG.keys()
    
    for sym in symbols:
        for lang in langs:
            
            logging.info(f'Getting {sym} {lang} ...')
                
            try:
                fh = ODS.download(sym, lang)
            except FileNotFound:
                logging.warning(f'{sym} {lang} not found in ODS')
                continue
            except Exception as e:
                raise e
                
            isolang = LANG[lang]
                
            try:
                result = File.import_from_handle(
                    fh,
                    filename=File.encode_fn(sym, isolang, 'pdf'),
                    identifiers=[Identifier('symbol', sym)],
                    languages=[isolang],
                    mimetype='application/pdf',
                    source='ods-importx',
                    overwrite=args.overwrite
                )
                logging.info(f'OK - {result.id}')
            except FileExistsLanguageConflict as e:
                logging.warning(e.message)
            except FileExistsIdentifierConflict as e:
                logging.warning(e.message)
            except FileExists:
                logging.info('Already in the system')
            except:
                raise
    
###

if __name__ == '__main__':
    run()
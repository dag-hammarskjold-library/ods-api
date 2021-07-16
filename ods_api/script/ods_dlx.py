import logging, re
from argparse import ArgumentParser
from pymongo.collation import Collation
from dlx import DB as DLX
from dlx.marc import Bib, Query, Condition
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
    ap.add_argument('--skip_check', action='store_true')
    
    return ap.parse_args()

def run():
    args = get_args()
    
    DLX.connect(args.dlx_connect)
    S3.connect(args.s3_key_id, args.s3_key, args.s3_bucket)
    
    symbols = [args.symbol] if args.symbol else [re.split('\t', x)[0].strip() for x in open(args.list).readlines()]
    langs = [args.language] if args.language else LANG.keys()
    
    for sym in symbols:
        bib = Bib.from_query(Condition('191', {'a': sym}).compile(), collation=Collation(locale='en', strength=2))
        
        if not bib and not args.skip_check:
            logging.warning(f'Bib for document {sym} not found. Skipping.')
            continue
        elif bib and not args.skip_check:
            # capture symbols from the bib record (exclude those beginning with brackets)
            ids = list(filter(lambda x: x[0] != '[', (bib.get_values('191', 'a') + bib.get_values('191', 'z'))))
        else:
            logging.warning(f'Bib for document {sym} not found with --skip_check enabled. Using {sym} as identifier')
            ids = symbols
        
        for lang in langs:
            logging.info(f'Getting {sym} {lang} ...')
                
            try:
                fh = ODS.download(sym, lang)
            except FileNotFound:
                logging.warning(f'{sym} {lang} not found in ODS')
                continue
            except Exception as e:
                logging.warning(e)
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
    
###

if __name__ == '__main__':
    run()
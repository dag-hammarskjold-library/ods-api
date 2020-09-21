import re
from tempfile import TemporaryFile
from requests import Session

class FileNotFound(Exception):
    pass

class ODS():
    session = Session()
    cookie_url = 'https://documents.un.org'
    base_url = 'http://daccess-ods.un.org/access.nsf/Get'
    
    @classmethod
    def download(cls, symbol, language, save_path=None):        
        symbol = symbol.replace(' ', '%20')
        
        if 'sessionID' not in cls.session.cookies.get_dict():
            cls.session.get(cls.cookie_url)
            
        url = '{}?Open&DS={}&Lang={}'.format(cls.base_url, symbol, language)
        response = cls.session.get(url)
        
        if response.status_code == 200: 
            html = response.content.decode('utf-8')
            match = re.search(r'URL=(.*)"', html)
        
            if not match:
                raise FileNotFound()
        else:
            raise Exception('Request failed to {}'.format(url))
                
        url = 'http://daccess-ods.un.org' + match.group(1)
        response = cls.session.get(url)
        
        if response.status_code == 200: 
            html = response.content.decode('utf-8') 
        
            html = response.content.decode('utf-8')
            match = re.search(r'URL=(.*)\?', html)
        
            if not match:
                raise Exception('TMP redirect not found')
        else:
            raise Exception('Request failed to {}'.format(url))
        
        url = match.group(1)
        response = cls.session.get(url, stream=True)
        
        if response.status_code == 200:
            if save_path:
                fh = open(save_path, 'wb+')
            else:
                fh = TemporaryFile()
                
            for chunk in response.iter_content(8192):
                fh.write(chunk)
            
            fh.seek(0)
            
            if '%PDF' not in fh.read(8192).decode('iso8859'):
                raise Exception('Target file doesn\'t look like a PDF')
            else:
                fh.seek(0)
                return fh
                
        else:
            raise Exception('Request failed to {}'.format(url))

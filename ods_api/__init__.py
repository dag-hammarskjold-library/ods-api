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
        """
        Downloads a file from ODS
        
        Postional arguments
        ---------
        symbol : str
        language: str
            The single character code used by ODS for language (A, C, E, F, R, S, O)
        save_path : str (optional)
            If provided, the downloaded file is saved to this path

        Returns
        -------
        File object
        """

        symbol = symbol.replace(' ', '%20')
        
        if 'sessionID' not in cls.session.cookies.get_dict():
            cls.session.get(cls.cookie_url)
            
        url = '{}?Open&DS={}&Lang={}'.format(cls.base_url, symbol, language)
        response = cls.session.get(url)
        
        if response.status_code == 200:
            if save_path:
                fileobj = open(save_path, 'wb+')
            else:
                fileobj = TemporaryFile()
                
            for chunk in response.iter_content(8192):
                fileobj.write(chunk)
            
            fileobj.seek(0)
            
            if '%PDF' not in fileobj.read(8192).decode('iso8859'):
                raise Exception('Target file doesn\'t look like a PDF')
            else:
                fileobj.seek(0)
                return fileobj
        else:
            raise Exception('Request failed to {}'.format(url))

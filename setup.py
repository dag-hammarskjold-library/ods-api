import sys
from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()
    
with open("requirements.txt") as f:
    requirements = list(filter(None,f.read().split('\n')))

setup(
    name = 'ods_api',
    version = '1.0',
    url = None,
    author = 'United Nations Dag Hammarskjöld Library',
    author_email = 'library-ny@un.org',
    license = 'http://www.opensource.org/licenses/bsd-license.php',
    packages = find_packages(exclude=['test']),
    #test_suite = 'test',
    #install_requires = requirements,
    description = 'Download files from ODS',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    python_requires = '>=3.5',
    entry_points = {
        'console_scripts': [
            'ods-dlx=ods_api.script.ods_dlx:run'
        ]
    }
)


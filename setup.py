try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Folder synchronization over (S)FTP',
    'author': 'Marc Carré',
    'url': 'https://github.com/marccarre/sftpsync',
    'download_url': 'https://github.com/marccarre/sftpsync',
    'author_email': 'carre.marc@gmail.com',
    'version': '0.1',
    'install_requires': comma_separated_dependencies(),
    'packages': ['sftpsync'],
    'scripts': [],
    'name': 'sftpsync'
}

def comma_separated_dependencies(exclusions=('nose', 'unittest2')):
    with open('requirements.txt', 'r') as f:
        return ','.join(dep.strip() for dep in f if all(not dep.startswith(e) for e in exclusions))

setup(**config)

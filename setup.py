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
    'install_requires': ['nose'],
    'packages': ['sftpsync'],
    'scripts': [],
    'name': 'sftpsync'
}

setup(**config)


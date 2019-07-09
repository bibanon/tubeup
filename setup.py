from setuptools import setup
import re
import ast


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('tubeup/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='tubeup',
    version=version,
    url='https://github.com/bibanon/tubeup',
    license='GPL 3',
    author='Bibliotheca Anonoma',
    description='Youtube (and other video site) to Internet Archive Uploader',
    packages=[
        'tubeup',
    ],
    entry_points={
        'console_scripts': [
            'tubeup = tubeup.__main__:main',
        ],
    },
    install_requires=[
        'internetarchive',
        'docopt==0.6.2',
        'youtube-dl',
    ]
)

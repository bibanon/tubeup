from setuptools import setup


setup(
    name='tubeup',
    version='0.0.1.dev1',
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
        'internetarchive>=1.0.0',
        'docopt',
        'youtube-dl',
    ]
)

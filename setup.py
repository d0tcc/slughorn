from setuptools import setup, find_packages

setup(
    name="slughorn",
    version='0.1',
    packages=find_packages(),
    package_data={'slughorn.processor': ['models/lid.176.ftz', 'models/nltk_german_classifier_data.pkl'],
                  'slughorn.processor.external_libraries.germalemma': ['data/lemmata.pkl'],
                  'slughorn': ['logging.conf']},
    py_modules=['slughorn'],
    install_requires=[
        'lxml >= 4.1.1',
        'fake-useragent >= 0.1.10',
        'fastText >= 0.8.22',
        'click >= 6.7',
        'beautifulsoup4 >= 4.6.0',
        'facebook-sdk >= 2.0.0',
        'requests >= 2.18.2',
        'selenium >= 3.8.0',
        'click-spinner >= 0.1.7',
        'pycountry >= 17.9.23',
        'nltk >= 3.2.5',
        'wordfreq >= 1.6.1',
        'pyphen >= 0.9.4'
    ],
    dependency_links=['git+https://github.com/facebookresearch/fastText.git@master#egg=fastText-0.8.22'],
    entry_points='''
        [console_scripts]
        slughorn=slughorn.cli:cli
    ''',
)
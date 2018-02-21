from setuptools import setup

setup(
    name="slughorn",
    version='0.1',
    packages=['lib', 'lib.scraper', 'lib.scraper.webdriver',
              'lib.processor', 'lib.processor.external_libraries', 'lib.processor.external_libraries.germalemma',
              'lib.processor.external_libraries.germalemma.data',
              'lib.processor.external_libraries.ClassifierBasedGermanTagger'],
    py_modules=['slughorn'],
    install_requires=[
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
        slughorn=slughorn:cli
    ''',
)
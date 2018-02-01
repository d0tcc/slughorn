from setuptools import setup

setup(
    name="slughorn",
    version='0.1',
    packages=['lib', 'lib.scraper', 'lib.scraper.webdriver', 'lib.processor'],
    py_modules=['slughorn'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        slughorn=slughorn:cli
    ''',
)
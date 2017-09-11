from setuptools import setup
setup(
    name = 'uce',
    version = '1.0.0',
    description='export course table uestc into a ics file that can be import into a calendar ',
    author='louiechan',
    packages = ['uce'],
    install_requires=[
        'requests',
        'BeautifulSoup4',
        'lxml'
        ],
    entry_points = {
        'console_scripts': [
            'uce = uce.__main__:main'
        ]
    })
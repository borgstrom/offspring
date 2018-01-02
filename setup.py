from setuptools import setup, find_packages

setup(
    name='offspring',
    version='0.1.1',
    install_requires=[],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    author='Evan Borgstrom',
    author_email='evan.borgstrom@gmail.com',
    license='Apache 2',
    url='https://github.com/borgstrom/offspring',
    description='Objects and patterns for working with processes in Python using the multiprocessing library',
    long_description=open('README.rst').read(),
)

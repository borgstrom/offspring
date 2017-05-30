from setuptools import setup, find_packages

with open('VERSION') as version_fd:
    version = version_fd.read().strip()

install_requires = [
]

setup(
    name='offspring',
    version=version,
    install_requires=install_requires,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    author='Evan Borgstrom',
    author_email='evan.borgstrom@gmail.com',
    license='Apache 2',
    description='Objects and patterns for working with processes in Python using the multiprocessing library'
)

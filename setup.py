from setuptools import setup, find_packages
import versioneer

setup(
    name='tetrad',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    # package_data={'tetrad':[]},
    url='',
    license='',
    author='Graham Voysey',
    author_email='gvoysey@bu.edu',
    description='A tool for discovering antigen targets for AML',
    install_requires=[
        'attrs'

        ,'numpy', 'pandas', 'anytree', 'sympy'

    ]
)

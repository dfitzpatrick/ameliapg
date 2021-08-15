from distutils.core import setup

__version__ = '0.1.2'

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

setup(
    name='ameliapg',
    author='Derek Fitzpatrick',
    version=__version__,
    description="Data bindings for the amelia bot",
    long_description=readme,
    install_requires=requirements,
    python_requires='>3.8.0',
    packages = [
        'ameliapg',
        'ameliapg.models',
        'ameliapg.server',
        'ameliapg.autorole',
        'ameliapg.metar',
        'ameliapg.station',
        'ameliapg.taf'
    ],
)


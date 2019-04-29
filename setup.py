from setuptools import setup, find_packages
from os import path

NAME='fxsignal'

_here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(_here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

version = {}
with open(path.join(_here, NAME, 'version.py')) as f:
    exec(f.read(), version)

setup(
    name='fxsignal',
    version=version['__version__'],
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='An example python package',
    long_description=long_description,
    install_requires=['numpy', 'pandas', 'fxcmpy'],
    # extras_require={":python_version<'3.3'": "fxcmpy"},
    url='https://github.com/jaaknt/fxsignal',
    python_requires='>=3.6.0',
    author='Jaak Niit',
    author_email='jaak.niit@gmail.com',
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3'
    ]
)

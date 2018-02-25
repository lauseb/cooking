from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='cooking',
    version='1.0.0',
    description='Recipes and grocery list manager',
    long_description=long_description,
    url='https://github.com/lauseb/cooking',
    author='lauseb',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=['flask',
                      "flask-bootstrap",
                      "flask-login",
                      "flask-migrate",
                      "flask-sqlalchemy",
                      "flask-wtf",
                      "text-unidecode",
                      "requests",
                      "python-dotenv",
                      ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)

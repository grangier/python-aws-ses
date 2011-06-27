from setuptools import setup, find_packages
import os

from ses import __version__

setup(name='ses',
    version=__version__,
    description="Python interface to AWS SES, django AWS SES backend",
    long_description="",
    keywords='',
    author='Xavier Grangier',
    author_email='grangier@gmail.com',
    url='',
    license='GPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'lxml',
        'restkit',
    ]
)
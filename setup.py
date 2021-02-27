# !/usr/bin/env python

import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name='python-gcp-etl',
    packages=setuptools.find_packages(),
    version='0.1.0',
    description='Templates for building Cloud Function ETL processes',
    long_description=long_description,
    author='Steven Sutton',
    license='BSD',
    author_email='admin@theeverydayfuture.com',
    url='https://github.com/Steamboat/python-gcp-etl',
    keywords=['postgres', 'etl', 'gcp', ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
    ],
)

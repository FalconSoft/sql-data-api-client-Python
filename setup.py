"""Setup script for sql-data-api-client"""

import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="sql-data-api-client",
    version="1.0.0",
    description="Python SQL Data Api client",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/FalconSoft/sql-data-api-client-Python",
    author="FalconSoft Ltd",
    author_email="ppaska@falconsoft-ltd.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    packages=["sql_data_api"],
    include_package_data=True,
    install_requires=[
        "requests", "json"
    ],
    entry_points={"console_scripts": ["sql-data-api-client=sql_data_api.__main__:main"]}
)
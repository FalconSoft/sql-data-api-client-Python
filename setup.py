"""
Setup script for sql-data-api-client
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SqlDataApi",
    version="0.1.17",
    author="FalconSoft Ltd",
    author_email="ppaska@falconsoft-ltd.com",
    description="Python library for Sql Data Api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FalconSoft/sql-data-api-client-Python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

"""
## to publish new version
1:/> python setup.py sdist bdist_wheel
2:/> python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

https://pypi.org/project/SqlDataApi

"""
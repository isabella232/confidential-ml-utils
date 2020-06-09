"""
Setup script for this Python package.
https://docs.python.org/3/distutils/setupscript.html
"""


import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / ".." / "README.md").read_text()

setup(
    name="confidential-ml-utils",
    version="0.0.0",
    description="Utilities for confidential machine learning",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Azure/confidential-ml-utils",
    author="AML Data Science",
    author_email="aml-ds@microsoft.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["confidential_ml_utils"],
    include_package_data=True,
    install_requires=[],
    # https://stackoverflow.com/a/48777286
    python_requires="~=3.6",
)
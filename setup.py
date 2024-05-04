#! /usr/bin/env python3.9

from setuptools import setup, find_packages

found_packages = find_packages(where="src")
print("Found packages:", found_packages)

setup(
    name="orison_ai",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(
        where="src"
    ),  # Automatically find all packages and sub-packages
    install_requires=[],
    author="Orison AI",
    author_email="core@orison.ai",
    description="Orison core software",
    url="http://orison.ai",
    classifiers=[
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",  # Minimum version requirement of Python
)

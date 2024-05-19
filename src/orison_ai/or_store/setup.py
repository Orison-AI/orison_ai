from setuptools import setup, find_packages


def load_requirements(filename="requirements.txt"):
    with open(filename, "r") as file:
        requirements = file.read().splitlines()
    return requirements


setup(
    name="or_store",
    version="0.1.0",
    packages=find_packages(),
    description="All the data storage and retrieval logic for the Orison AI.",
    author="Orison AI",
    author_email="admin@orison.ai",
    url="www.orison.ai",
    install_requires=load_requirements(),  # Include the dependencies read from the requirements.txt
    python_requires=">=3.10",
)

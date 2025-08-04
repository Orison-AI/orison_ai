#! /usr/bin/env python3.11

from setuptools import setup, find_packages

setup(
    name="orison-ai",
    version="1.0.0",
    description="Modern, optimized AI gateway for document processing, summarization, and Google Scholar operations",
    author="Orison AI",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "numpy",
        "fastapi",
        "openai",
        "scholarly",
        "functions-framework",
        "requests",
        "firebase_admin",
        "google-cloud-firestore",
        "mongoengine",
        "pymongo",
        "google-cloud-secret-manager",
        "langchain>=0.3.0",
        "langchain-community>=0.3.0",
        "langchain-openai>=0.2.0",
        "langchain-core>=0.3.0",
        "langsmith>=0.1.0",
        "langgraph>=0.2.0",
        "qdrant_client>=1.11.0",
        "langchain_qdrant>=0.1.0",
        "pypdf",
        "unstructured",
        "markdown",
        "python-docx",
        "pytest",
        "pytest-asyncio",
    ],
)

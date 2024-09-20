import os
from setuptools import setup, find_packages

# Get the absolute path of the directory containing this script
base_dir = os.path.abspath(os.path.dirname(__file__))

# Read the README.md file
with open(os.path.join(base_dir, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements.txt file
with open(os.path.join(base_dir, "requirements.txt"), "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="constellation-api",
    version="1.0.0",
    author="Mason Lee",
    author_email="mason_lee@brown.edu",
    description="A robust and scalable FastAPI application for managing pipelines, blocks, edges, and audit logs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/constellation-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "constellation-api=app.main:main",
        ],
    },
)

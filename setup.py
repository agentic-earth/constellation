from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="constellation-api",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
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

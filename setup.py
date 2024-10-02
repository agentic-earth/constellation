from setuptools import setup, find_packages
import os
import sys

# Add the api/backend directory to the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'api', 'backend'))
sys.path.insert(0, backend_path)

setup(
    name="constellation-backend",
    version="0.1.0",
    packages=find_packages(include=['api', 'api.*']),
    package_data={'': ['*.yaml', '*.json', '*.sql']},
    include_package_data=True,
    python_requires=">=3.7",s
    install_requires=[
        # List your dependencies here
    ],
)
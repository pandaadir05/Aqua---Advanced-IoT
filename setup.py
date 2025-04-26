"""
Setup script for Aqua - Next Generation IoT Security Scanner.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aqua",
    version="1.0.0",
    author="Adir",
    author_email="adir@example.com",
    description="Aqua - Next Generation IoT Security Scanner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pandaadir05/aqua",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-nmap>=0.7.1",
        "scapy>=2.5.0",
        "pyshark>=0.6.0",
        "paramiko>=3.1.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.4.2",
        "rich>=13.5.0",
        "typer>=0.9.0",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "aqua=aqua.cli:app",
        ],
    },
) 
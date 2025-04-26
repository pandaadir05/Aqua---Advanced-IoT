from setuptools import setup, find_packages

setup(
    name="aqua-security",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'aqua=aqua.cli:main',
        ],
    },
    install_requires=[
        "fastapi>=0.103.1",
        "uvicorn>=0.23.2",
        "jinja2>=3.1.2",
        "aiofiles>=23.1.0",
        "python-multipart>=0.0.6",
    ],
    python_requires='>=3.7',
)
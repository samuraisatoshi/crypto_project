"""
Setup script for projeto_ml_trade package.
"""
from setuptools import setup, find_packages
import os

def read_requirements(filename):
    """Read requirements from file."""
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def create_required_directories():
    """Create required directories if they don't exist."""
    directories = [
        'data/raw/binance/spot',
        'data/raw/binance/futures',
        'data/dataset/native',
        'data/dataset/finrl',
        'data/enriched',
        'logs',
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Create required directories
create_required_directories()

setup(
    name='projeto_ml_trade',
    version='0.1.0',
    description='Cryptocurrency trading analysis and backtesting platform',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('requirements-dev.txt'),
    },
    entry_points={
        'console_scripts': [
            'ml_trade=app_streamlit:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    include_package_data=True,
    package_data={
        'projeto_ml_trade': [
            'attribs.env.example',
        ],
    },
)

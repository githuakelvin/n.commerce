#!/usr/bin/env python
"""
Setup script for Kenya Commerce E-Commerce Platform
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="kenya-commerce",
    version="1.0.0",
    author="Kenya Commerce Team",
    author_email="info@kenyacommerce.co.ke",
    description="A fully functional e-commerce website for the Kenyan market",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kenya-commerce",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/kenya-commerce/issues",
        "Documentation": "https://kenyacommerce.co.ke/docs",
        "Source Code": "https://github.com/yourusername/kenya-commerce",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-django>=4.0",
            "coverage>=5.0",
            "black>=21.0",
            "flake8>=3.8",
            "isort>=5.0",
        ],
        "production": [
            "gunicorn>=20.0",
            "psycopg2-binary>=2.9",
            "redis>=4.0",
            "celery>=5.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ecommerce, kenya, mpesa, django, python",
    entry_points={
        "console_scripts": [
            "kenya-commerce=kenya_commerce.manage:main",
        ],
    },
)


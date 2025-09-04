#!/usr/bin/env python3
"""
Setup script for Crystal Quest
Enables pip installation and packaging
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="crystal-quest",
    version="1.0.0",
    author="Crystal Quest Development Team",
    author_email="dev@crystalquest.game",
    description="A challenging 2D platformer game built with Python and Pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crystal-quest",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Arcade",
        "Topic :: Games/Entertainment :: Side-Scrolling/Arcade Games",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pyinstaller>=4.0",
            "black",
            "flake8",
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "crystal-quest=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "game": ["*.py"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/crystal-quest/issues",
        "Source": "https://github.com/yourusername/crystal-quest",
        "Documentation": "https://github.com/yourusername/crystal-quest/blob/main/README.md",
    },
)

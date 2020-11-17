import os

from setuptools import setup

__version__ = "0.1.3"


def read(fp):
    return open(os.path.join(os.path.dirname(__file__), fp)).read()


setup(
    name="pygicord",
    author="Davide Tacchini",
    url="https://github.com/davidetacchini/pygicord",
    project_urls={
        "GitHub repo": "https://github.com/davidetacchini/pygicord",
        "GitHub issues": "https://github.com/davidetacchini/pygicord/issues",
    },
    version=__version__,
    packages=["pygicord"],
    description="An easy-to-use pagination wrapper for discord.py",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=read("requirements.txt"),
    extras_require={"dev": ["black", "isort", "flake8"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)

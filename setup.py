import os
import re

from setuptools import setup

version = ""
with open("pygicord/__init__.py") as fp:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fp.read(), re.MULTILINE
    ).group(1)


if not version:
    raise RuntimeError("Cannot set the version.")


def read(fp):
    return open(os.path.join(os.path.dirname(__file__), fp)).read()


setup(
    name="pygicord",
    author="Davide Tacchini",
    url="https://github.com/davidetacchini/pygicord",
    version=version,
    license="MIT",
    packages=["pygicord"],
    keywords=["discord.py", "paginator"],
    description="A pagination wrapper for discord.py",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=read("requirements.txt"),
    python_requires=">=3.7.0",
    extras_require={"dev": ["black", "isort", "flake8"]},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)

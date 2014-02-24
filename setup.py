import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "coolmit",
    version = "0.0.1",
    author = "Adam Wentz",
    author_email = "awentz@theonion.com",
    description = ("Don't just commit; coolmit.",),
    long_description = read("README.md"),
    license = "MIT",
    keywords = "git cool commit",
    url = "https://github.com/awentzonline/coolmit",
    packages=["coolmit"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "coolmit = coolmit:run_commandline",
        ]
    }
)
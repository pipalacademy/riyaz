from setuptools import setup, find_packages


setup(
    name="riyaz",
    version="0.1.0",
    description="CLI tool to create, update, and download courses using Riyaz",
    author="Pipal Academy",
    install_requires=["click"],
    url="https://github.com/pipalacademy/riyaz-cli",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "riyaz = riyaz:main"
        ]
    }
)

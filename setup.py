from setuptools import setup, find_packages


setup(
    name="riyaz",
    version="0.1.0",
    description="CLI tool to create, update, and download courses using Riyaz",
    author="Pipal Academy",
    install_requires=[
        "click>=8.1.3",
        "pydantic>=1.9.2",
        "PyYAML>=6.0",
        "python-frontmatter==1.0.0"
    ],
    url="https://github.com/pipalacademy/riyaz",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "riyaz = riyaz.cli:main"
        ]
    }
)

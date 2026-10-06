from setuptools import setup, find_packages

setup(
    name="calculator",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
)

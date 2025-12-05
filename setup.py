from setuptools import find_packages, setup

setup(
    name="dictify_js",
    version="0.1.0",
    description="Extract Python dictionaries from JS/TS object literals.",
    packages=find_packages(include=["dictify_js", "dictify_js.*"]),
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
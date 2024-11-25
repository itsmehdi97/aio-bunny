import os
from setuptools import setup, find_packages
from importlib.machinery import SourceFileLoader


module = SourceFileLoader(
    "version", os.path.join("aio_bunny", "version.py")
).load_module()


setup(
    name="aio-bunny",
    version=module.__version__,
    author=module.__author__,
    author_email=module.team_email,
    license=module.package_license,
    description=module.package_info,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms="all",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=find_packages(exclude=["tests"]),
    package_data={"co": ["py.typed"]},
    install_requires=["aio-pika>=6.8.0,<10", ],
    python_requires=">=3.10, <4",
    extras_require={
        "develop": [
            "aio-pika",
            "async_generator",
            "coverage!=4.3",
            "coveralls",
            "pylama",
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "tox>=2.4",
        ],
    },
    project_urls={
        "Documentation": "https://aio-bunny.readthedocs.org/",
        "Source": "https://github.com/itsmehdi97/aio-bunny",
    },
)

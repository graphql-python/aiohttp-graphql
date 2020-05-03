from setuptools import setup, find_packages

setup(
    name="aiohttp-graphql",
    version="1.1.0",
    description="Adds GraphQL support to your aiohttp application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/graphql-python/aiohttp-graphql",
    download_url="https://github.com/graphql-python/aiohttp-graphql/releases",
    author="Devin Fee",
    author_email="devin@devinfee.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="api graphql protocol aiohttp",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "graphql-core>=2.3,<3",
        "graphql-server-core>=1.2,<2",
        "aiohttp>=3,<4",
    ],
    extras_require={
        "test": [
            "pytest>=5.4,<5.5",
            # Note: tests do not work with pytest-asyncio 0.11, see
            # https://github.com/pytest-dev/pytest-asyncio/issues/158
            "pytest-asyncio>=0.10,<0.11",
            "pytest-cov>=2.8,<3",
            "jinja2>=2.11,<3",
            "yarl>1.4,<1.5",
        ],
    },
    include_package_data=True,
    platforms="any",
)

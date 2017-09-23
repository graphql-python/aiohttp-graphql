from setuptools import setup, find_packages

setup(
    name='aiohttp-graphql',
    version='1.0.0',
    description='Adds GraphQL support to your aiohttp application',
    long_description=open('README.md').read(),
    url='https://github.com/dfee/aiohttp-graphql',
    download_url='https://github.com/dfee/aiohttp-graphql/releases',
    author='Devin Fee',
    author_email='devin@devinfee.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='api graphql protocol aiohttp',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'graphql-core>=2.0.dev',
        'graphql-server-core>=1.0.dev',
        'aiohttp>=2.0.0',
        'pytest-runner',
    ],
    extras_require={
        'test': [
            'pylint>=1.7.2',
            'pytest>=2.7.3',
            'pytest-asyncio>=0.7.0',
            'jinja2>=2.9.0',
            'yarl>=0.9.6',
        ],
    },
    include_package_data=True,
    platforms='any',
)

from setuptools import setup, find_packages

setup(
    name='patisson_grqpal',
    version='0.2.0',
    packages=find_packages(),
    author='EliseyGodX',
    description='Tools for developing microservices using GraphQL (ariadne)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Patisson-Company/_GraphQL',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)
import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name='austen',
    version='0.1.0',
    author='Piotr Rarus',
    author_email='piotr.rarus@gmail.com',
    description='Nested telemetry logger.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/piotr-rarus/austen',
    packages=setuptools.find_packages(
        exclude=[
            "tests",
        ]
    ),
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'seaborn',
        'scikit-image',
        'joblib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: MIT',
        'Operating System :: OS Independent'
    ],
)

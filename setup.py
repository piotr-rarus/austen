import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name='austen',
    description='Nested telemetry logger.',

    author='Piotr Rarus',
    author_email='piotr.rarus@gmail.com',

    url='https://github.com/piotr-rarus/austen',
    license='MIT',
    version='0.2.7',

    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=setuptools.find_packages(
        exclude=[
            'tests',
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
    tests_require=[
        'pytest',
        'pytest-cov',
        'flake8',
        'pylint'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
)

import os
import setuptools


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


TESTS_REQUIRE = [
    'coverage',
    'flake8',
    'mock',
    'pytest',
]


setuptools.setup(
    name="xlcalculator",
    version="0.1.0dev",
    author="Bradley van Ree",
    author_email="brads@bradbase.net",
    description="Converts MS Excel formulas to Python and evaluates them.",
    long_description=(
        read('README.rst')
        + '\n\n' +
        read('CHANGES.rst')
        ),
    url="https://github.com/bradbase/xlcalculator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    install_requires=[
        'jsonpickle >= 1.3',
        'networkx >= 2.4',
        'numpy >= 1.18.1',
        'pandas >= 1.0.1',
        'openpyxl >= 3.0.3',
        'numpy_financial >= 1.0.0',
        'xlfunctions >= 0.0.3b'
    ],
    extras_require=dict(
        test=TESTS_REQUIRE,
    ),
    python_requires='>=3.7.6',
    tests_require=TESTS_REQUIRE,
    include_package_data=True,
    zip_safe=False,
)

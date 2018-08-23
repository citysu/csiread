#!/usr/bin python3
# -*- coding: utf-8 -*-

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize

with open("README.md", "r") as fh:
    long_description = fh.read()

extensions = [
    Extension(
        "csiread", ["csiread/csiread.pyx"], 
        extra_compile_args=['-Wno-cpp']
    ),
]
setup(
    name = "csiread",
    version = "1.0.3",

    author = "suhecheng",
    author_email = "2215523266@qq.com",

    description = "Parse binary file obtained by csi-tool",
    long_description = long_description,
    long_description_content_type="text/markdown",

    maintainer = "suhecheng",
    maintainer_email = "2215523266@qq.com",

    packages = find_packages(),
    package_data = {
        'csiread.sample': ['*']
    },
    install_requires = [
        'numpy'
    ],
    python_requires = '>=3',

    ext_modules = cythonize(extensions),

    classifiers = ["Topic :: Scientific/Engineering",
                    "Programming Language :: Python :: 3",
                    "Programming Language :: Python :: Implementation :: CPython", 
                    "Operating System :: POSIX :: Linux",
                    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],

)
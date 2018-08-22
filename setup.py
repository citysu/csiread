#!/usr/bin python3
# -*- coding: utf-8 -*-

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

setup(
    name = "csiread",
    version = "1.0.3",
    description = "Parse binary file obtained by csi-tool",
    long_description = "you can get csi data from Intel 5300 NIC, instead of Matlab, read csi data by python, and do processing.",
    author = "suhecheng",
    author_email = "2215523266@qq.com",
    maintainer = "suhecheng",
    maintainer_email = "2215523266@qq.com",
    url = "nothing",
    download_url = "nothing",
    packages = [],
    py_modules = [],
    scripts = [],
    ext_modules = cythonize([
        Extension("csiread", ["csiread.pyx"], extra_compile_args=['-Wno-cpp'])
    ]),
    classifiers = ["Topic :: Scientific/Engineering",
                    "Programming Language :: Python :: Implementation :: CPython"],
    data_files = [],
    package_dir = []  
)

#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools import distutils
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

default_compiler = distutils.ccompiler.get_default_compiler()
if default_compiler == 'unix':
    EXTRA_COMPILE_ARGS = ['-g0']
else:
    EXTRA_COMPILE_ARGS = []

LONG_DESCRIPTION = """\
# csiread [![PyPI](https://img.shields.io/pypi/v/csiread?)](https://pypi.org/project/csiread/)

A fast channel state information parser for Intel, Atheros, Nexmon and ESP32 in Python.

- Full support for Linux 802.11n CSI Tool, Atheros CSI Tool and nexmon_csi, ESP32-CSI-Tool
- At least 15 times faster than the implementation in Matlab
- Real-time parsing and visualization.
"""

EXTENSIONS = [
    Extension(
        "csiread._csiread", ["csiread/_csiread.pyx"],
        include_dirs=[numpy.get_include()],
        define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
        extra_compile_args=EXTRA_COMPILE_ARGS,
    ),
]

setup(
    name="csiread",
    version="1.3.7",

    description="A fast channel state information parser for Intel, " \
                "Atheros and Nexmon.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",

    author="Hecheng Su",
    author_email="2215523266@qq.com",
    url="https://github.com/citysu/csiread",

    packages=find_packages(),
    install_requires=['numpy'],
    python_requires='>=3',
    ext_modules=cythonize(
        EXTENSIONS,
        compiler_directives={'language_level': 3, 'binding': False}
    ),

    license='MIT',
    classifiers=["Topic :: Scientific/Engineering",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: Implementation :: CPython",
                 "Operating System :: Unix",
                 "Operating System :: POSIX",
                 "Operating System :: Microsoft",
                 "Operating System :: MacOS",
                 "License :: OSI Approved :: MIT License"],
)

#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys

import numpy
from Cython.Build import cythonize
from setuptools import find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension


def find_files(root, ext):
    ret = list()
    if os.path.exists(root):
        for file in os.listdir(root):
            if file.endswith(ext):
                ret.append(os.path.join(root, file))
    return ret


class Build(build_ext):
    def build_extensions(self):
        if self.compiler.compiler_type in ['unix', 'mingw32']:
            for e in self.extensions:
                if e.name == "csiread._csiread":
                    e.extra_compile_args = ['-g0']
                if os.name == 'nt':
                    e.extra_compile_args += ['-DMS_WIN64']
                    e.library_dirs = [os.path.dirname(sys.executable)]
        if self.compiler.compiler_type in ["msvc"]:
            for e in self.extensions:
                if e.name == "csiread._csiread":
                    e.extra_compile_args = []
        super(Build, self).build_extensions()


LONG_DESCRIPTION = """\
# csiread [![PyPI](https://img.shields.io/pypi/v/csiread?)](https://pypi.org/project/csiread/)

A fast channel state information parser for Intel, Atheros, Nexmon and ESP32 in Python.

- Full support for Linux 802.11n CSI Tool, Atheros CSI Tool and nexmon_csi, ESP32-CSI-Tool
- At least 15 times faster than the implementation in Matlab
- Real-time parsing and visualization.
"""


# csiread extension
csiread_extension = Extension(
    "csiread._csiread", ["csiread/_csiread.pyx"],
    include_dirs=[numpy.get_include()],
    define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
)
EXTENSIONS = [csiread_extension]

setup(
    name="csiread",
    version="1.3.8",

    description="A fast channel state information parser for Intel, " \
                "Atheros, Nexmon and ESP32.",
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
    cmdclass={'build_ext': Build},

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

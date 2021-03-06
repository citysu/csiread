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

with open("README.md", "r", encoding='UTF-8') as fh:
    LONG_DESCRIPTION = fh.read()

EXTENSIONS = [
    Extension(
        "csiread.csiread", ["csiread/csiread.pyx"],
        include_dirs=[numpy.get_include()],
        define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
        extra_compile_args=EXTRA_COMPILE_ARGS,
    ),
]
setup(
    name="csiread",
    version="1.3.5",

    author="Hecheng Su",
    author_email="2215523266@qq.com",
    url="https://github.com/citysu/csiread",
    description="Parse channel state information from raw CSI data file in Python.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",

    maintainer="Hecheng Su",
    maintainer_email="2215523266@qq.com",

    packages=find_packages(),

    install_requires=[
        'numpy',
    ],
    python_requires='>=3',

    ext_modules=cythonize(EXTENSIONS, compiler_directives={'language_level': 3}),

    classifiers=["Topic :: Scientific/Engineering",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: Implementation :: CPython",
                 "License :: OSI Approved :: MIT License"],
)

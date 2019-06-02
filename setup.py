#!/usr/bin python3
# -*- coding: utf-8 -*-

# define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

EXTENSIONS = [
    Extension(
        "csiread", ["csiread/csiread.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=['-w', '-O3']
    ),
]
setup(
    name="csiread",
    version="1.3.0",

    author="Hecheng Su",
    author_email="2215523266@qq.com",
    url="https://github.com/citysu/csiread",
    description="Parse channel state information obtained by csitools",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",

    maintainer="Hecheng Su",
    maintainer_email="2215523266@qq.com",

    packages=find_packages(),

    install_requires=[
        'numpy'
    ],
    python_requires='>=3',

    ext_modules=cythonize(EXTENSIONS),

    classifiers=["Topic :: Scientific/Engineering",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: Implementation :: CPython",
                 "Operating System :: POSIX :: Linux",
                 "Operating System :: Microsoft :: Windows",
                 "License :: OSI Approved :: MIT License"],
)

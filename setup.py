#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import re

import numpy
from Cython.Build import cythonize
from setuptools import find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension


with open("README.md", "r", encoding='UTF-8') as fh:
    DOCLINES = fh.readlines()


with open("csiread/__init__.py", "r", encoding='UTF-8') as fh:
    VERSION = re.search(r'(\d+)\.(\d+)\.(\d+)', fh.read()).group()


CLASSIFIERS = """\
Topic :: Scientific/Engineering
Programming Language :: Python :: 3
Programming Language :: Python :: Implementation :: CPython
Operating System :: Unix
Operating System :: POSIX
Operating System :: Microsoft
Operating System :: MacOS
License :: OSI Approved :: MIT License
"""


def get_build_overrides():
    """Custom build commands"""
    class new_build_ext(build_ext):
        def build_extensions(self):
            if self.compiler.compiler_type in ['unix', 'mingw32']:
                for e in self.extensions:
                    e.extra_compile_args = ['-g0']
                    if os.name == 'nt':
                        e.extra_compile_args += ['-DMS_WIN64']
                        e.library_dirs = [os.path.dirname(sys.executable)]
            if self.compiler.compiler_type in ["msvc"]:
                for e in self.extensions:
                    e.extra_compile_args = []
            super(new_build_ext, self).build_extensions()
    return new_build_ext


def get_extensions():
    extensions = list()
    npy_macros = ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')
    npy_include = numpy.get_include()
    extensions.append(Extension(
        "csiread._csiread", ["csiread/_csiread.pyx"],
        include_dirs=[npy_include],
        define_macros=[npy_macros],
    ))
    extensions.append(Extension(
        "csiread._picoscenes", ["csiread/_picoscenes.pyx"],
        include_dirs=[npy_include],
        define_macros=[npy_macros],
    ))
    return extensions


def setup_package():
    setup(
        name="csiread",
        version=VERSION,
        description=DOCLINES[2].rstrip("\n"),
        long_description="".join(DOCLINES),
        long_description_content_type="text/markdown",
        author="Hecheng Su",
        author_email="2215523266@qq.com",
        url="https://github.com/citysu/csiread",
        packages=find_packages(),
        install_requires=['numpy'],
        python_requires='>=3',
        ext_modules=cythonize(
            get_extensions(),
            compiler_directives={'language_level': 3, 'binding': False}
        ),
        cmdclass={'build_ext': get_build_overrides()},
        license='MIT',
        classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    )


if __name__ == '__main__':
    setup_package()

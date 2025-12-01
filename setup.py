from setuptools import setup, Extension
from Cython.Build import cythonize

ext_modules = [
    Extension(
        "neuronet",
        sources=["neuronet.pyx"],
        language="c++",
        extra_compile_args=["-std=c++11", "-O3"],
    )
]

setup(
    name="NeuroNet Core",
    ext_modules=cythonize(ext_modules),
)
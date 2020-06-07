"""A compression AGSI middleware using brotli.

Built using starlette under the hood, it can be used as a drop in replacement to
GZipMiddleware for Starlette or FastAPI.
"""

from setuptools import setup  # type: ignore

setup(
    name="brotli-asgi",
    version="0.4",
    url="https://github.com/fullonic/brotli_middleware",
    license="MIT",
    author="Diogo B Freitas",
    author_email="somnium@riseup.net",
    description="A compression AGSI middleware using brotli",
    long_description=__doc__,
    packages=["brotli_asgi"],
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=["starlette>=0.13.4", "brotli>=1.0.7"],
    platforms="any",
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)

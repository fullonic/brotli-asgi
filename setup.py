"""A compression AGSI middleware using brotli.

Built using starlette under the hood, it can be used as a drop in replacement to
GZipMiddleware for Starlette or FastAPI.
"""

from setuptools import setup  # type: ignore

extras = {
    'test_brotli': ['requests==2.23.0', 'mypy==0.770'],
    'test_brotlipy': ['requests==2.23.0', 'mypy==0.770', 'brotlipy==0.7.0']
}

setup(
    name="brotli-asgi",
    version="1.1.0",
    url="https://github.com/fullonic/brotli-asgi",
    license="MIT",
    author="Diogo B Freitas",
    author_email="somnium@riseup.net",
    description="A compression AGSI middleware using brotli",
    long_description=__doc__,
    packages=["brotli_asgi"],
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=["starlette>=0.13.4", "brotli>=1.0.7"],
    extras_require=extras,
    platforms="any",
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)

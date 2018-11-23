import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pandas_bokeh",
    version="0.0.1",
    author="Patrik Hlobil",
    author_email="patrik.hlobil@googlemail.com",
    description="Bokeh plotting backend for pandas.DataFrame.plot functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/????????",
    packages=setuptools.find_packages(),
    install_requires=["bokeh"],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Visualization'
    ],
)

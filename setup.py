import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyngw", 
    version="1.0.0",
    author="Artem Svetlov",
    author_email="artem.svetlov@nextgis.com",
    description="Python wraper for NextGIS Web REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nextgis/pyngw",
    packages=setuptools.find_packages(),
    install_requires=[
          'tuspy',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)

# coding: utf-8
import re
import setuptools

# Use the following command from a terminal window to generate the whl with source code
# python setup.py bdist_wheel

with open("README.md", "r") as fh:
    long_description = fh.read()

version_scope = {'__builtins__': None}
with open("seeq/addons/clustering/_version.py", "r+") as f:
    version_file = f.read()
    version_line = re.search(r"__version__ = (.*)", version_file)
    if version_line is None:
        raise ValueError(f"Invalid version. Expected __version__ = 'xx.xx.xx', but got \n{version_file}")
    version = version_line.group(1).replace(" ", "").strip('\n').strip("'").strip('"')
    print(f"version: {version}")

    version_scope.update({'__version__':version})

setup_args = dict(
    name='seeq-clustering',
    version=version_scope['__version__'],
    author="Eric Parsonnet",
    author_email="e.parsonnet@berkeley.edu",
    license='Apache License 2.0',
    platforms=["Linux", "Windows"],
    description="Clustering of data in Seeq",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seeq12/seeq-clustering",
    packages=setuptools.find_namespace_packages(include=['seeq.*']),
    include_package_data=True,
    package_data={'seeq': ['addons/clustering/_notebook.ipynb']},
    zip_safe=False,
    install_requires=[
        'hdbscan>=0.8.27',
        'bokeh>=2.4.2',
        'numpy>=1.22.0',
        'pandas>=1.3.5'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

setuptools.setup(**setup_args)
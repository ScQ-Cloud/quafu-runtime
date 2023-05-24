import os
import setuptools

# Set version
VERSION = "0.1.0"

# Read long description from README.
README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")
with open(README_PATH) as readme_file:
    README = readme_file.read()

# Requirement list
REQUIREMENTS = [
    "pyquafu>=0.2.11",
    "urllib3>=1.21.1",
    "websocket-client>=1.5.1",
    "typing-extensions>=4.0.0",
    "pyflakes>=3.0.1",
    "websocket>=0.2.1"
]

setuptools.setup(
    name="quafu-runtime",
    version=VERSION,
    description="Python client for Quafu Runtime.",
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=REQUIREMENTS,
    # TODO
    url="https://github.com/",
    author="Quafu Development Team",
    license="Apache 2.0",
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
    ],
    keywords='quafu sdk api runtime quantum',
    packages=setuptools.find_packages(exclude=["tests", "*test*", "tests*"]),
    include_package_data=True,
    python_requires=">=3.8",
    zip_safe=False,
    # project_urls={
    #     "Documentation": "",
    #     "Source Code": ""
    # }

)
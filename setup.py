import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-agua-iot",
    version="0.0.10",
    author="Frederic Van Linthoudt",
    author_email="frederic.van.linthoudt@gmail.com",
    description="py-agua-iot provides controlling heating devices connected via the IOT Agua platform of Micronova",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fredericvl/py-agua-iot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "PyJWT>=2.1.0",
        "requests>=2.25.1",
    ],
)

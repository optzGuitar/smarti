from distutils.core import setup

with open("README.md", 'r') as file:
    content = file.read()

setup(
    name="smarti",
    version="1.0",
    description="A smart and lightweight dependency injector",
    author="optzGuitar",
    url="https://github.com/optzGuitar/smarti",
    packages=["smarti"],
    long_description=content,
    long_description_content_type='text/markdown'
)

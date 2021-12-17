from distutils.core import setup
from smarti import __version__ as smarti_version

with open("README.md", 'r') as file:
    content = file.read()

setup(
    name="smarti",
    version=smarti_version,
    description="A smart and lightweight dependency injector",
    author="optzGuitar",
    url="https://github.com/optzGuitar/smarti",
    packages=["smarti"],
    long_description=content,
    long_description_content_type='text/markdown'
)

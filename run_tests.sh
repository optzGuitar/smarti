set -e

flake8 . --count --show-source --statistics --ignore=E501,W503
mypy ./smarti/ ./tests/
pytest

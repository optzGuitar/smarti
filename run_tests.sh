set -e

flake8 ./smarti/ ./tests/ --count --show-source --statistics --ignore=E501,W503
mypy ./smarti/ ./tests/
pytest

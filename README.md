# Set up
To set up the virtual environment and install the dependencies, run the following command in the repository root
```
python3 -m venv .venv && python3 -m pip install -e . && source .venv/bin/activate
```

# Running the tests
To only run the tests, run the following command in the repository root
```
pytest
```

# Generating the coverage report
To generate the coverage report, run the following command in the repository root
```
pytest --cov=src --cov-branch --cov-report=html && open htmlcov/index.html
```
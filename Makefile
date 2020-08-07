dev-setup:
	python pip install -e ".[test]"

tests:
	py.test tests --cov=aiohttp_graphql -vv
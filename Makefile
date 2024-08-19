clean:
	rm README.txt
	rm -rf ./dist ./build

generate_pypi_README:
	${VIRTUAL_ENV}/bin/pytextile README.textile | sed -e 's/^\t//' > README.txt

build: generate_pypi_README
	python -m build

upload_to_test: build
	twine check ./dist/*
	twine upload --repository test_textile ./dist/*

upload_to_prod: build
	twine check ./dist/*
	# for now, don't actually upload to prod PyPI, just output the command to do so.
	@echo "twine upload --repository textile ./dist/*"

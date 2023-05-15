.PHONY update_requirements:
update_requirements:
	pipreqs --force --encoding=utf8 ./ --ignore .\secvenv\

.PHONY install_requirements:
install_requirements:
	pip install -r requirements.txt

.PHONY run_test:
run_test:
	python ./sample_cmdi_test.py

.PHONY serve:
	php -S localhost:9000
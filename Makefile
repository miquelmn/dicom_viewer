TEST_PATH=./
# Need to specify bash in order for conda activate to work.
.ONESHELL:
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH

init:
	pip install -r requirements.txt

test:
	py.test --verbose --color=yes $(TEST_PATH)

run:
	/home/miquel/miniconda3/envs/mediques/bin/python -m viewer

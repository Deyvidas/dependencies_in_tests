# Don't forgot to add into 'venv/bin/activate':
# ----------------------------------------------
# PYTHONPATH="/absolute/path/to/root/of/project"
# export PYTHONPATH
# echo ${PYTHONPATH}
# ----------------------------------------------

ROOT_DIR = ${PYTHONPATH}

help:	## Show this help.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

black:	## Formats the code base.
	poetry run black \
		--skip-string-normalization \
		--line-length 79 \
		${ROOT_DIR}

isort:	## Sort all imports.
	poetry run isort \
		--force-single-line-imports \
		--lines-after-imports 2 \
		${ROOT_DIR}

autoflake:	## Delete all unused imports.
	poetry run autoflake \
		--recursive \
		--in-place \
		--remove-all-unused-imports \
		--ignore-init-module-imports \
		${ROOT_DIR}

mypy_check:	## Make mypy checking.
	poetry run mypy \
		--python-executable python \
		${ROOT_DIR}

formating:	## Run make commands autoflake -> isort -> black -> mypy_check.
	make autoflake
	echo
	make isort
	echo
	make black
	echo
	make mypy_check

dependencies:	## Run script gen_requirements.sh that generate {type}_requirements.txt
	sh ${ROOT_DIR}/gen_requirements.sh

before_commit: 	## Run scripts formatting -> run tests -> dependencies.
	make formating
	echo
	poetry run pytest ${ROOT_DIR}
	echo
	make dependencies
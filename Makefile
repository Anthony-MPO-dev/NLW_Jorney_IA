.PHONY:: install lint format test sec

begin: install init dependencies

check: format lint

install:
		@poetry lock
		@poetry install

init:
		@poetry shell

format:
		@isort .
		@blue .
		@poetry install
		
lint:
		@blue . --check
		@poetry install


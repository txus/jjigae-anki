SRC = $(wildcard jjigae/*.py)

all: deps tests

lint:
	flake8 jjigae tests

osx-deps:
	brew install mpv lame

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate
	pip install -Ur requirements.txt
	pip install -Ur requirements.dev
	touch venv/bin/activate

vendor: submodules
	cp lib/hanja-dictionary/hanjadic.sqlite jjigae/

anki: venv submodules osx-deps
	. venv/bin/activate
	cd anki && pip install -r requirements.txt && pip install -r requirements.qt && make build && ./tools/build_ui.sh

submodules:
	git submodule update

deps: anki vendor

test: $(SRC)
	pytest tests

package: vendor venv
	. venv/bin/activate
	./venv/bin/python package.py

install: package
	rm -fr '${HOME}~/Library/Application Support/Anki2/addons21/jjigae'
	mkdir -p '${HOME}/Library/Application Support/Anki2/addons21/jjigae'
	cp -r package/* '${HOME}/Library/Application Support/Anki2/addons21/jjigae/'

.PHONY: osx-deps lint vendor submodules package

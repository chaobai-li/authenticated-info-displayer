all:
	python3.6 -m transcrypt -n show_info.py

test:
	python -m SimpleHTTPServer 8888

build:
	python3.6 -m transcrypt show_info.py

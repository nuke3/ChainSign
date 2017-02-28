%.py: %.ui
	pyside-uic $< > $@

chainsign.py: gui/mainwindow.py

run: chainsign.py
	python chainsign.py

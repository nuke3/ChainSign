%.py: %.ui
	pyside-uic $< -o $@

chainsign.py: gui/mainwindow.py

run: chainsign.py
	python chainsign.py

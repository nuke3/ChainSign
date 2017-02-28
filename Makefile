UI_OBJS = gui/mainwindow.py

%.py: %.ui
	pyside-uic $< -o $@

all: chainsign.py

chainsign.py: $(UI_OBJS)

run: chainsign.py
	python chainsign.py

clean:
	-rm $(UI_OBJS)

UI_OBJS = gui/mainwindow.py
RCC_FILES = assets/assets.py

%.py: %.ui
	pyside-uic --from-imports $< -o $@

%.py: %.qrc
	pyside-rcc $< -o $@
	cp $@ gui/$(notdir $(basename $@))_rc.py # FIXME

all: chainsign.py

chainsign.py: $(UI_OBJS) $(RCC_FILES)

run: chainsign.py
	python chainsign.py

clean:
	-rm $(UI_OBJS) $(RCC_FILES) gui/assets_rc.py

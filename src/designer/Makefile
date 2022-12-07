UIC = pyside6-uic

target = slider.py fade.py

.PHONY: all

all: $(target)

%.py:	%.ui
	$(UIC) $^ > $@

clean:
	rm -f $(target)



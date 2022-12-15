UIC = pyside6-uic

target = slider.py fade.py general.py volume.py main.py
.PHONY: all

all: $(target)

%.py:	%.ui
	$(UIC) --from-imports $^ > $@

clean:
	rm -f $(target)



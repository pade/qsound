RCC = pyside6-rcc

target = ressources_rc.py
.PHONY: all

all:	$(target)

$(target):	ressources.qrc
	$(RCC) $^ -o $@
	cp $@ ../src/designer

clean:
	rm -f $(target)

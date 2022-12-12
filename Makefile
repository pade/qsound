.PHONY: all clean
all:
	$(MAKE) -C ./assets all
	$(MAKE) -C ./src/designer all

clean:
	$(MAKE) -C ./assets clean
	$(MAKE) -C ./src/designer clean
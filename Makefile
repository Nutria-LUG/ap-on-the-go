install:
	chmod +x ap-on-the-go.py
	cp ap-on-the-go.py /usr/bin/ap-on-the-go

uninstall:
	rm /usr/bin/ap-on-the-go

.PHONY: install uninstall

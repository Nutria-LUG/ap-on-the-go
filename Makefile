install:
	chmod +x openair-ap.py
	cp openair-ap.py /usr/bin/openair-ap
	cp openair-dnsmasq.conf /etc/openair-dnsmasq.conf
	cp openair-hostapd.conf /etc/openair-hostapd.conf

uninstall:
	rm /usr/bin/openair-ap
	rm /etc/openair-dnsmasq.conf
	rm /etc/openair-hostapd.conf

.PHONY: install uninstall

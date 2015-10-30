SHELL := /bin/bash

macbundle:
	if [ -e futgui/cookies.txt ]; then mv futgui/cookies.txt futgui/.cookies.txt; fi
	if [ -e futgui/config/login.json ]; then mv futgui/config/login.json futgui/config/.login.json; fi
	rm -rf build dist
	python3 setup_mac.py futgui/py2app --packages=requests
	dmgbuild -s futgui/dmg/settings.py "Auto Buyer Installer" dist/AutoBuyerInstaller.dmg
	if [ -e futgui/.cookies.txt ]; then mv futgui/.cookies.txt futgui/cookies.txt; fi
	if [ -e futgui/config/.login.json ]; then mv futgui/config/.login.json futgui/config/login.json; fi

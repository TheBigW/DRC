DESTDIR=
SUBDIR=/usr/lib/rhythmbox/plugins/DRC/
DATADIR=/usr/share/rhythmbox/plugins/DRC/
LOCALEDIR=/usr/share/locale/

all:
clean:
	- rm *.pyc

install:
	install -d $(DESTDIR)$(SUBDIR)
	install -d $(DESTDIR)$(DATADIR)
	install -m 644 *.py $(DESTDIR)$(SUBDIR)
	install -m 755 calcFilter* $(DESTDIR)$(DATADIR)
	install -m 755 measure* $(DESTDIR)$(DATADIR)
	install -m 644 erb44100.drc $(DESTDIR)$(DATADIR)
	install -m 644 *.glade $(DESTDIR)$(DATADIR)
	install -m 644 DRC.plugin $(DESTDIR)$(SUBDIR)
	install -m 644 LICENSE.txt $(DESTDIR)$(SUBDIR)
	cd po;./install_all.sh $(DESTDIR)$(LOCALEDIR)
	

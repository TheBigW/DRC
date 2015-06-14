DESTDIR=
SUBDIR=/usr/lib/rhythmbox/plugins/DRC/
DATADIR=/usr/share/rhythmbox/plugins/DRC/
LOCALEDIR=/usr/share/locale/

all:
clean:
	- rm *.pyc

install:
	install -d $(DESTDIR)$(SUBDIR)
	install -m 644 *.py $(DESTDIR)$(SUBDIR)
	install -m 644 calcFilter* $(DESTDIR)$(SUBDIR)
	install -m 644 measure* $(DESTDIR)$(SUBDIR)
	install -m 644 erb44100.drc $(DESTDIR)$(SUBDIR)
	install -m 644 *.glade $(DESTDIR)$(SUBDIR)
	install -m 644 LICENSE.txt $(DESTDIR)$(SUBDIR)
	cd po;./install_all.sh $(DESTDIR)$(LOCALEDIR)
	

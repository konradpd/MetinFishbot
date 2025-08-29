1. interception
	https://github.com/oblitum/Interception/releases/download/v1.0.1/Interception.zip
	rozpakowujesz
	wchodzisz do folderu
	wchodzisz do command line installer
	kopiujesz scieżkę
	wpisujesz w start cmd, otwierasz jako administator
	w cmd: cd /d (wklejasz scieżkę CTRL+V)
	w cmd: install-interception.exe /install
	ZRESTARTUJ KOMPA

2. Python 3.12.2
	https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
	odpalasz isntaller jako admin (win 11 nie jako admin)
	zaznaczasz ADD PATH i USE ADMIN PRIVLAGES (jeżeli masz opcje)
	przeklikujesz

3. Pip
	cmd: pip
	jeżeli jest to git, jeżeli nie to:
	py -m pip install --upgrade pip
	sprawdzasz znowu cmd: pip
	jeżeli nie działa to radź sobie sam

4. OBS
	odpalasz jako administrator

5. Requirement.txt
	Pobierasz bota
	W pasku ścieżki wpisujesz cmd
	cmd: pip install -r requirements.txt
	wszystko cacy

6. config.ini #nic nie ususwać tylko można edytować
	bait_keys - przyciski po przeciku z których ma sciągać robaki np.: 1,2,3,F3,F4
	effect_keys - na razie nie działa
	logs - na razie nie działa
	stop_key_combination - tutaj wpisujesz kombinacje przycisków która ma ci zastopować bota np. shift+p lub samo p
	break_chance - na razie nie dziala
	break_duration - na razie nie dziala
	loot_filter - tutaj wpisujesz nazwy przedmiotow których nie chcesz wyławiać (minigierka spali od razu ten przedmiot) po przecinku, z _ zamiast spacji przykład
	# polecany config loot_filter = wybielacz,farba_do_wlosow,pierscien_jezyka bo to gówno warte

7. Alerty dźwiekowe:
	wejdź w folder templates
	przesłuchaj:
		captcha_alert.wav
		exp_alert.wav
	jak chcesz to sobie podmień na swoje tylko taka sama nazwa i rozszerzenie wav! Inaczej nie zadziała i dowiesz sie o tym dopiero wywali bota gdy będzie próbowało puścić alert (np. przy captchy)

8. Ustawienia metina WAŻNE!
	okienko 640x540
	czcionka arial
	najlepiej wyłącz chat i zablokuj wszystko oprócz szeptów

9. Odpalanie bota
	Odpalasz bota z maksymalnie 1 okienkiem - plik run jako administator
	Wpisujesz liczbe klientów
	Otwierasz reszte klientów
	Ustawiasz obs i konsole żeby nie przeszkadzała
	Wpisujesz aktualną ilość exp na wędkach i ilość expa potrzebną na ulepszenie
	(jeżeli nie chcesz powiadomień to przy wpisywaniu expa naciśnij enter bez żadnego inputu)
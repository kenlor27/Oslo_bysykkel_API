"""
Dette er et enkelt program som viser oppdatert liste over ledige sykler og tilgjengelige låser i alle Oslos bysykkelstativ.
En del av stativene har ikke registrert navn, men listes likevel opp som 'STATIVNAVN ER IKKE REGISTRERT'.

Dataene hentes fra oslobysykkel-APIet – https://oslobysykkel.no/api/v1 (+ API endpoints) – som krever en Identifier.
Brukeren blir spurt om Identifier når programmet startes.

Requests-biblioteket følger med Python 3.7 (kanskje også andre versjoner), men må manuelt legges til for å kunne kjøre programmet.
Hvis du sliter med å installere 'requests', se: https://stackoverflow.com/questions/17309288/importerror-no-module-named-requests
Programmet er i utgangspunktet laget for Python 3.7, men kan fungere for andre versjoner av Python (ikke testet).

Opprettet av Kenneth Lorentzen 03.10.2018.
Sist endret av Kenneth Lorentzen 04.10.2018. 
"""

import requests, json

# Tegner en enkel horisontal linje for å skille mellom radene i 'tabellen'
def Tegn_radlinje():
	print ('—————————————————————————————————————————————————————————————————————————————————')
# endDEF ----------

rot = "https://oslobysykkel.no/api/v1"
min_ID = "q"
gyldig_ID = False

while True:

	# Brukeren må taste inn sin egen Identifier med mindre gyldig er lagt inn
	if (gyldig_ID == False):
		min_ID = input('Skriv inn din unike ID-nøkkel og trykk <Enter>: ')
	
	header = {'Client-Identifier' : min_ID}

	# Lagrer HTTP-statuskoden som API-et returnerer
	sjekk_ID = requests.get(rot + "/status", headers = header).status_code
	statuskode = json.loads(requests.get(rot + "/status", headers = header).content)

	# Hvis brukerens Identifier ikke er gyldig
	if (sjekk_ID == 401):
		print ("Ugyldig ID-nøkkel.")
		min_ID = input('Trykk <Enter> for å prøve igjen eller skriv \'q\' eller \'quit\' og deretter trykk <Enter> for å avslutte: ').lower()
		if min_ID == 'q' or min_ID == 'quit':
			break

	elif (sjekk_ID != 200):
		print ('Feil:', statuskode['error'])
		break
	
	# Hvis svaret fra API-et er '200 OK' kjøres resten av koden
	else:
		# Gyldig ID-nøkkel er registrert
		gyldig_ID = True
		# Objektifiserer teksten (som hentes i API-et 'status') som json og beholder kun det som ligger inne i objektet 'status'.
		status = json.loads(requests.get(rot + "/status", headers = header).content)
		status = status['status']

		# Sjekker om ALLE sykkelstativene er ute av drift. I så fall er det ikke noe vits i å kjøre resten av koden.
		if (status['all_stations_closed']):
			print ("Alle sykkelstativer er for tiden ute av drift!\n")
			
		else:
			# Viser hvor mange stativer som er ute av drift (om noen).
			if (len(status['stations_closed']) > 0):
				print (status['stations_closed'].len + " stativer er for tiden ute av drift!\n")
			# endIF ----------

			# Objektifiserer teksten (som hentes i API-et 'stations') som json og beholder kun det som ligger inne i objektet 'stations'.
			stativer = json.loads(requests.get(rot + "/stations", headers = header).content)
			stativer = stativer['stations']
				
			# Oppretter en tom liste (dictionary) for å direkte kunne hente ut stativnavn ved hjelp av stativ-id.
			stativnavn = {'Id': 'Navn'}
			
			# Iterer gjennom alle elementene i listen som inneholder stativene og legger til koblingene mellom navn og id i dictionary-en
			for s in stativer:
				stativnavn[s['id']] = s['title']
			# endFOR ----------
					
			# Objektifiserer teksten (som hentes i API-et 'stations/availability') som json og lagrer de tre forskjellige objektene 'availability', 'updated_at' og 'refresh_rate' i hver sin variabel.
			tilgjengelighet = json.loads(requests.get(rot + "/stations/availability", headers = header).content)
			oppdatert = tilgjengelighet['updated_at']
			rate = tilgjengelighet['refresh_rate']
			tilgjengelighet = tilgjengelighet['stations']
			
			Tegn_radlinje()
			print ('{0} {1:3} {2:30} {3:32}'.format(' ', 'Id', 'Stativnavn', 'Antall ledige sykler og tilgjengelige låser'))
			
			# Iterer gjennom alle elementene i tilgjengelighetslisten
			for s in tilgjengelighet:
				# Henter ut id-feltet til hvert element og lagrer det i en variabel for å få mer lettlest kode i de neste linjene
				id = s['id']
				
				Tegn_radlinje()
				
				try:
					# Skriver ut id, stativnavn og dets antall ledige sykler og låser, samt formaterer teksten slik at informasjonen bli enkel å lese
					print ('{0} {1:3} {2:30} {3} {4:2} {5} {6:2} {7}'.format('|', id, stativnavn[id], 'Ledige sykler:', s['availability']['bikes'], ' Tilgjengelige låser:', s['availability']['locks'], '|'))
				except KeyError:
					# Hvis id finnes i tilgjengelighetslisten men IKKE i stativlisten skrives alt ut som ovenfor, unntatt stativnavnet (som ikke finnes)
					print ('{0} {1:3} {2:30} {3} {4:2} {5} {6:2} {7}'.format('|', id, "STATIVNAVN ER IKKE REGISTRERT", 'Ledige sykler:', s['availability']['bikes'], ' Tilgjengelige låser:', s['availability']['locks'], '|'))
				except:
					# Denne koden blir kjørt dersom noe annet feiler. Her er det mulig å spesifisere nærmere og evt. legge til flere relevante exceptions.
					print ("UKJENT FEIL …")
			# endFOR ----------
			
			Tegn_radlinje()
			
			# Skriver ut antall stativer i stativlisten, antall elementer i tilgjengelighetslisten, når dataene siste ble oppdatert samt oppdateringsraten.
			print('Antall stativer registrert i stativlisten:', len(stativer))
			print ('Antall stativer i tilgjengelighetslisten:', len(tilgjengelighet))
			print ('Tilgjengelighetslisten oppdatert', oppdatert)
			print ('Oppdateringsrate', rate)
			
			
			avslutte = input('Trykk <Enter> for å oppdatere eller skriv \'q\' eller \'quit\' og trykk <Enter> for å avslutte: ').lower()
			if (avslutte == 'q' or avslutte == 'quit'):
				break
# endWHILE ----------
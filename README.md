
## Extrem simples Kickbase CLI

1. Installieren der benötigten Pakete:
``` bash
python3 -m pip install click rich numpy 
```
2. [Diesen Fork](https://github.com/jhelgert/kickbase-api-python) der Kickbase API clonen und installieren:
``` bash
python3 -m pip install git+https://github.com/jhelgert/kickbase-api-python
``` 

3. Innerhalb der `kb.py` in Zeile 91 die Logindaten des Kickbase accounts
eintragen.
4. Anschließend lässt sich das Programm von der Kommandozeile bequem nutzen:
   
``` bash
 ↪  python3 kb.py --help
Usage: kb.py [OPTIONS]

  Extrem simples Kickbase CLI. (Leider ohne Lewandowskicheat)

Options:
  --market           Ausgabe des Transfermarkts aller Ligen der letzten 3 Tage
  --team             Ausgabe des eigenen Teams aller Ligen der letzten 3 Tage
  --only_increasing  Ignoriere alle Spieler, deren MW aktuell fällt
  --matchday         Ausgabe der Livepunkte des eigenen Teams während des
                     Spieltags

  --help             Show this message and exit.
```


## Mögliche Erweiterungen

- Bieten auf einen Spieler
- Verkaufen eines Spielers

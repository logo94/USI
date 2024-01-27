![](https://img.shields.io/badge/Python-3.8%2B-green.svg)

## Requisiti ##
Per l'utilizzo degli scripts è necessario aver scaricato `Python 3.8+` sul proprio dispositivo, per installare Python seguire le istruzioni riportate al seguente [link](https://www.python.org/downloads/).

Una volta eseguito il download è possibile verificare le versioni di `Python` e `pip` tramite i comandi:

```
python --version
```
```
pip --version
```

## Ambiente virtuale ##
Per non compromettere l'installazione di Python e le relative librerie è consigliabile creare un ambiente virtuale; per la sua creazione, una volta dentro la cartella dell'applicazione, procedere come segue:

Aprire il terminale all'interno della cartella (premere il tasto destro del mouse all'interno di uno spazio vuoto della cartella e selezionare l'opzione Apri nel Terminale)

Creare l'ambiente virtuale, quindi digitare:
```
python -m venv pyenv
```
oppure, in caso di errore:
```
python3 -m venv pyenv
```

### Linux
Per attivare l'ambiente virtuale con un sistema operativo Linux digitare:
```
source pyenv/bin/activate
```
### Windows
L'attivazione dell'ambiente virtuale su sistema operativo Windows richiede i privilegi di Amministratore di sistema, è quindi necessario aprire il Terminale o Windows PowerShell come amministratore. Una volta eseguita la procedura sopra riportata digitare:
```
pyenv\Scripts\activate
```

## Librerie ##
### Linux
Per il suo funzionamento lo script utilizza le librerie esterne:

- pymarc (https://pypi.org/project/pymarc/)
- langdetect (https://pypi.org/project/langdetect/)
- google translator (https://pypi.org/project/googletrans/)
- langid (https://pypi.org/project/langid/)

per il corretto funzionamento dell'applicazione è necessario procedere con il download di tutti i pacchetti necessari, ovvero:

```
pip install -r requirements.txt
```
### Windows
Per l'installazione delle librerie è necessario disporre dei perivilegi di amministratore di sistema, in alternativa è possibile avviare l'installazione senza privilegi specifici attraverso il comando:
```
pip install -r requirements.txt --user
```
> Eventuali messaggi di Warning durante l'installazione potranno essere ignorati
Python packages:

## Utilizzo ##
Una volta scaricato il repository e scaricate le librerie necessarie, per avviare l'applicazione sarà sufficiente eseguire il comando:
```
python oclc.py
```
oppure:
```
python3 oclc.py
```


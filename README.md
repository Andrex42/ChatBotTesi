# ChatBotTesi

Questo progetto è il risultato della tesi triennale ***"Un sistema di supporto alla valutazione basato su AI generativa"***

## Setup

Per configurare correttamente l'applicazione, seguire i passaggi di seguito.

### Prerequisiti

Assicurarsi di avere installati i seguenti prerequisiti:

- Python (versione 3.11)
- virtualenv
- Cambiare la key di openai all'interno del file.env

### Installazione delle dipendenze

1. Clonare il repository:

   ```bash
   git clone https://github.com/sicignanoandrea/ChatBotTesi

2. Navigare nella directory del progetto:

   ```bash
   cd ChatBotTesi

3. Creare un ambiente virtuale Python (utilizzando virtualenv)::

   ```bash
   python -m venv venv

4. Attivare l'ambiente virtuale:
- Su Linux/macOS:
   ```bash
   source venv/bin/activate
- Su Windows:
   ```bash
   venv\Scripts\activate

5. Installare le dipendenze del progetto utilizzando il file requirements.txt:
   ```bash
   pip install -r requirements.txt


### Esecuzione dell'applicazione

Dopo aver configurato correttamente l'ambiente, è possibile eseguire l'applicazione utilizzando il file app.py. Assicurarsi di essere nella directory principale del progetto e che l'ambiente virtuale sia attivato.
   ```bash
   python main.py
```
L'applicazione dovrebbe avviarsi correttamente e sarà pronta per l'uso.

## Utenti

Di seguito sono elencate le credenziali valide per l'applicazione:

```
STUDENTI = [
    studente.archeologia',
    studente.basidati',
    studente.tecweb',
    sicignano.andrea
]

DOCENTI = [
    docente.archeologia,
    docente.basidati,
    docente.tecweb
]

```
È possibile modificare gli utenti e le relazioni che intercorrono tra di essi nel file `users.py`

## Settaggi modificabili

È possibile modificare alcuni settaggi dell'applicazione tramite un file `.env`. Le variabili configurabili sono:

- `PRETRAINED_MODEL_NAME`: Il nome del modello utilizzato per la generazione di embedding. Esempio: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- `USE_TRAIN_RESPONSES_DATA`: Se impostato su `true`, utilizza i documenti inseriti nella collezione in fase di training.
- `USE_EXPORT_DATA`: Se impostato su `true`, importa eventuali export delle domande e delle risposte presenti nella cartella `export_data`.

Modificare questi settaggi nel file `.env` secondo le necessità dell'applicazione.


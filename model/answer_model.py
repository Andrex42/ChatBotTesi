from dataclasses import dataclass


@dataclass
class Answer:
    id: str
    id_domanda: str
    domanda: str
    id_docente: str
    risposta: str
    id_autore: str
    voto_docente: float
    voto_predetto: float
    commento: str
    source: str
    data_creazione: str

from dataclasses import dataclass


@dataclass
class Question:
    id: str
    domanda: str
    id_docente: str
    categoria: str
    source: str
    archived: bool
    data_creazione: str

from dataclasses import dataclass


@dataclass
class Answer:
    id: str
    id_domanda: str
    domanda: str
    id_docente: str
    risposta: str
    id_autore: str
    voto_docente: int
    voto_predetto: int
    voto_predetto_all: int
    chat_gpt_rating: int
    use_as_ref: bool
    commento: str
    source: str
    data_creazione: str

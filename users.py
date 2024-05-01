STUDENTS = [
    {'username': 'studente.archeologia', 'password': 'tesi123'},
    {'username': 'studente.archeologia2', 'password': 'tesi123'},
    {'username': 'studente.archeologia3', 'password': 'tesi123'},
    {'username': 'studente.archeologia4', 'password': 'tesi123'},
    {'username': 'studente.archeologia5', 'password': 'tesi123'},
    {'username': 'studente.archeologia6', 'password': 'tesi123'},
    {'username': 'studente.archeologia7', 'password': 'tesi123'},
    {'username': 'studente.basidati', 'password': 'tesi123'},
    {'username': 'studente.basidati2', 'password': 'tesi123'},
    {'username': 'studente.basidati3', 'password': 'tesi123'},
    {'username': 'studente.tecweb', 'password': 'tesi123'},
    {'username': 'trimarco.francesco', 'password': 'tesi123'},
]

TEACHERS = [
    {'username': 'docente.archeologia', 'password': 'tesi123'},
    {'username': 'docente.basidati', 'password': 'tesi123'},
    {'username': 'docente.tecweb', 'password': 'tesi123'}
]

RELATIONS = [
    {'studente.archeologia': ['docente.archeologia']},
    {'studente.archeologia2': ['docente.archeologia']},
    {'studente.archeologia3': ['docente.archeologia']},
    {'studente.archeologia4': ['docente.archeologia']},
    {'studente.archeologia5': ['docente.archeologia']},
    {'studente.archeologia6': ['docente.archeologia']},
    {'studente.archeologia7': ['docente.archeologia']},
    {'studente.basidati': ['docente.basidati']},
    {'studente.basidati2': ['docente.basidati']},
    {'studente.basidati3': ['docente.basidati']},
    {'studente.tecweb': ['docente.tecweb']},
    {'trimarco.francesco': ['docente.tecweb', 'docente.basidati']}
]

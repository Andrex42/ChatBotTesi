STUDENTS = [
    {'username': 'studente.archeologia', 'password': 'studente123'},
    {'username': 'studente.archeologia2', 'password': 'studente123'},
    {'username': 'studente.archeologia3', 'password': 'studente123'},
    {'username': 'studente.archeologia4', 'password': 'studente123'},
    {'username': 'studente.basidati', 'password': 'studente123'},
    {'username': 'studente.tecweb', 'password': 'studente123'},
    {'username': 'trimarco.francesco', 'password': 'studente123'},
]

TEACHERS = [
    {'username': 'docente.archeologia', 'password': 'docente123'},
    {'username': 'docente.basidati', 'password': 'docente123'},
    {'username': 'docente.tecweb', 'password': 'docente123'}
]

RELATIONS = [
    {'studente.archeologia': ['docente.archeologia']},
    {'studente.archeologia2': ['docente.archeologia']},
    {'studente.archeologia3': ['docente.archeologia']},
    {'studente.archeologia4': ['docente.archeologia']},
    {'studente.basidati': ['docente.basidati']},
    {'studente.tecweb': ['docente.tecweb']},
    {'trimarco.francesco': ['docente.tecweb', 'docente.basidati']}
]

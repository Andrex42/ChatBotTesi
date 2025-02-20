STUDENTS = [
    {'username': 'studente.archeologia', 'password': 'tesi123'},
    {'username': 'studente.basidati', 'password': 'tesi123'},
    {'username': 'studente.tecweb', 'password': 'tesi123'},
    {'username': 'sicignano.andrea', 'password': 'tesi123'},
]

TEACHERS = [
    {'username': 'docente.archeologia', 'password': 'tesi123'},
    {'username': 'docente.basidati', 'password': 'tesi123'},
    {'username': 'docente.tecweb', 'password': 'tesi123'}
]

RELATIONS = [
    {'studente.archeologia': ['docente.archeologia']},
    {'studente.basidati': ['docente.basidati']},
    {'studente.tecweb': ['docente.tecweb']},
    {'sicignano.andrea': ['docente.tecweb', 'docente.basidati']}
]

import chromadb
from mock import MOCK_DATA


chroma_client: chromadb.ClientAPI


def init_chroma_client():
    global chroma_client
    chroma_client = chromadb.Client()


def get_questions_and_answers_data():
    return MOCK_DATA


def get_collections():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    question_collection = chroma_client.get_or_create_collection(name="questions")
    teacher_answers_collection = chroma_client.get_or_create_collection(name="teacher_answers")
    student_answers_collection = chroma_client.get_or_create_collection(name="student_answers")

    return question_collection, teacher_answers_collection, student_answers_collection


def get_question_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    question_collection = chroma_client.get_or_create_collection(name="questions")

    return question_collection


def get_teacher_answers_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    teacher_answers_collection = chroma_client.get_or_create_collection(name="teacher_answers")

    return teacher_answers_collection


def get_student_answers_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    student_answers_collection = chroma_client.get_or_create_collection(name="student_answers")

    return student_answers_collection


def populate_collections():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    question_collection, teacher_answers_collection, student_answers_collection = get_collections()
    q_and_a = get_questions_and_answers_data()

    question_collection.add(
        documents=[question["value"] for question in q_and_a],
        metadatas=[{"teacher_id": question["teacher_id"]} for question in q_and_a],
        ids=[question["id"] for question in q_and_a]
    )

    teacher_answers_collection.add(
        documents=[question["answer"] for question in q_and_a],
        metadatas=[{"question_id": question["id"], "teacher_id": question["teacher_id"]} for question in q_and_a],
        ids=[question["id"] for question in q_and_a]  # same as question_id
    )

    student_answers_collection.add(
        documents=[student_answer["value"] for question in q_and_a for student_answer in question["student_answers"]],
        metadatas=[{"question_id": question["id"], "student_id": student_answer["student_id"]}
                   for question in q_and_a for student_answer in question["student_answers"]],
        ids=[student_answer["id"] for question in q_and_a for student_answer in question["student_answers"]]
    )


def extract_data(query_result):
    result = []
    for i, metadata in enumerate(query_result['metadatas']):
        data = {
            'id': query_result['ids'][i],
            'document': query_result['documents'][i]
        }
        for key, value in metadata.items():
            data[key] = value
        result.append(data)
    return result

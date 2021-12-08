insert_user = \
    f'''
        INSERT INTO user (name, password, status_id)
        VALUES (%(name)s, %(password)s, %(status_id)s);
    '''

insert_questionnaire = \
    f'''
        INSERT INTO questionnairy (title, number_question, user_id)
        VALUES (%(title)s, %(number_question)s, %(user_id)s);
    '''

insert_question = \
    f'''
        INSERT INTO question (text, number_answer, questionnairy_id)
        VALUES (%(text)s, %(number_answer)s, %(questionnairy_id)s);
    '''

insert_answer = \
    f'''
        INSERT INTO answer (text, question_id)
        VALUES (%(text)s, %(question_id)s);
    '''
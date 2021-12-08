select_query = \
    f'''
        SELECT *
        FROM questionnairy
    '''

select_last_questionnairy = \
    f'''
        SELECT *
        FROM questionnairy
        ORDER BY id_questionnairy DESC
        LIMIT 1
    '''

select_user_full_info = \
    f'''
        SELECT *
        FROM user
            JOIN user_status ON user.status_id = user_status.id_status
    '''

select_user_by_name = \
    f'''
        SELECT * 
        FROM user
        WHERE name = %(name)s AND password = %(password)s; 
    '''

select_questionnairy_by_id = \
    f'''
        SELECT * 
        FROM questionnairy q
        WHERE q.id_questionnairy = %(id_questionnaire)s; 
    '''



select_questions = \
    f'''
        SELECT * 
        FROM question q
        WHERE q.questionnairy_id = %(id_questionnaire)s;
    '''


select_answers = \
    f'''
        SELECT * 
        FROM question 
            JOIN answer ON question.id_question = answer.question_id 
        WHERE question.id_question = %(id_question)s;
    '''

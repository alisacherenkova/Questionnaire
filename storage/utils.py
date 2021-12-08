from flask import session

from storage.connection import get_db, close_db


def get_params_user():
    name = None
    status = None
    if 'user_id' in session:
        connection, cursor = get_db()
        cursor.execute(
            f'''
                SELECT name, status_id
                FROM user
                WHERE id_user = %(id_user)s;
            '''
            , {'id_user': session['user_id']}
        )
        user = cursor.fetchall()
        if len(user) > 0:
            name = user[0][0]
            status = user[0][1]
        close_db(connection, cursor)
    return dict(name=name, admin=status == 1)


def delete_questionnaire():
    if 'id_questionnaire' in session:
        connection, cursor = get_db()
        cursor.execute(
            f'''
                   DELETE FROM questionnairy
                   WHERE id_questionnairy = %(id_questionnairy)s;
            '''
            , {'id_questionnairy': session['id_questionnaire']}
        )
        close_db(connection, cursor)
    session.pop('id_questionnaire', None)

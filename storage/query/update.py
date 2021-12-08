update_make_admin_user = \
    f'''
        UPDATE user
        SET status_id = 1
        WHERE id_user = %(id_user)s;
    '''


update_not_admin_user = \
    f'''
        UPDATE user
        SET status_id = 2
        WHERE id_user = %(id_user)s;
    '''


update_number_of_selections = \
    f'''
        UPDATE answer
        SET number_of_selections = number_of_selections + 1
        WHERE id_answer = %(id_answer)s;
    '''

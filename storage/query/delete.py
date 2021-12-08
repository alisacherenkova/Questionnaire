delete_user = \
    f'''
        DELETE FROM user
        WHERE id_user = %(id_user)s;
    '''
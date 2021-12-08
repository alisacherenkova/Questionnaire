from flask import request, redirect, render_template, session, url_for

from storage import app
from storage.connection import Error, get_db, close_db
from storage.query.delete import delete_user
from storage.query.insert import *
from storage.query.select import *
# from storage.utils import get_params_user, delete_questionnaire
from storage.query.update import update_make_admin_user, update_not_admin_user, update_number_of_selections
from storage.utils import get_params_user, delete_questionnaire


@app.route('/', methods=['POST', 'GET'])
def index():
    print('1')
    # delete_questionnaire()
    user = get_params_user()
    connection, cursor = get_db()
    cursor.execute(select_query)
    questionnaires = cursor.fetchall()
    # print(questionnaires)
    close_db(connection, cursor)
    # questionnaires = Questionnaire.query.order_by(Questionnaire.id).all()

    error_message = ""
    if 'error_message' in session:
        error_message = session['error_message']
        session.pop('error_message', None)

    if request.method == 'POST':
        session['id_questionnaire'] = request.form['delete']
        return redirect(url_for('index'))
    print(user)
    return render_template('index.html', questionnaires=questionnaires, **user, error_message=error_message)


@app.route('/create', methods=['POST', 'GET'])
def create():
    user = get_params_user()
    if not user['admin']:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if "questionnaire_added" in request.form:
            title = request.form['title']
            try:
                number_questions = int(request.form['number_questions'])
            except Error as e:
                print(e)
                session['error_message'] = "Ошибка при вводе числа вопросов при создании анкеты " + title
                return redirect(url_for('index'))

            if number_questions < 1:
                session['error_message'] = "Ошибка при вводе числа вопросов при создании анкеты " + title
                return redirect(url_for('index'))
            connection, cursor = get_db()
            # questionnaire = Questionnaire(title=title, number_questions=number_questions)
            try:
                cursor.execute(insert_questionnaire, {'title': title, 'number_question': number_questions,
                                                      'user_id': session['user_id']})
                connection.commit()
                cursor.execute(select_last_questionnairy)
                q = cursor.fetchall()
                print(q)
                session['id_questionnaire'] = q[0][0]
                return render_template('create.html', number_questions=number_questions,
                                       adding_questionnaire=False, adding_questions=True,
                                       adding_answers=False, **user)
            except Error as e:
                print(e)
                session['error_message'] = "Ошибка добавления анкеты в базу данных"
                return redirect(url_for('index'))
        elif "questions_added" in request.form:
            connection, cursor = get_db()
            cursor.execute(select_questionnairy_by_id, {'id_questionnaire': session['id_questionnaire']})
            questionnaire = cursor.fetchall()
            print(len(questionnaire))
            for i in range(questionnaire[0][2]):
                print(i)
                form_question = request.form["question" + str(i)]
                try:
                    number_answers = int(request.form["number_answers" + str(i)])
                except Error as e:
                    print(e)
                    session[
                        'error_message'] = "Ошибка при вводе числа ответов при создании анкеты " + questionnaire[0][2]
                    return redirect(url_for('index'))

                if number_answers < 1:
                    session[
                        'error_message'] = "Ошибка при вводе числа ответов при создании анкеты " + questionnaire[0][2]
                    return redirect(url_for('index'))

                # question = Question(text=form_question, number_answers=number_answers,
                #                    id_questionnaire=questionnaire.id)

                try:
                    cursor.execute(insert_question, {'text': form_question, 'number_answer': number_answers,
                                                     'questionnairy_id': questionnaire[i][0]})
                    connection.commit()
                    # db.session.add(question)
                    # db.session.commit()
                except Error as e:
                    print(e)
                    session['error_message'] = "Ошибка добавления вопроса в базу данных"
                    return redirect(url_for('index'))
            cursor.execute(select_questions, {'id_questionnaire': session['id_questionnaire']})
            questions = cursor.fetchall()
            # questions = Questionnaire.query.get(session['id_questionnaire']).questions
            return render_template('create.html', questions=questions, adding_questionnaire=False,
                                   adding_questions=False, adding_answers=True, **user)
        elif "answers_added" in request.form:
            connection, cursor = get_db()
            cursor.execute(select_questions, {'id_questionnaire': session['id_questionnaire']})
            questions = cursor.fetchall()
            # questions = Questionnaire.query.get(session['id_questionnaire']).questions
            for question in questions:
                for i in range(question[2]):
                    print(question)
                    form_answer = request.form["answer" + str(question[0]) + str(i)]
                    # answer = Answer(text=form_answer, id_question=question.id)
                    try:
                        cursor.execute(insert_answer, {'text': form_answer, 'id_question': question[0]})
                        connection.commit()
                        # db.session.add(answer)
                        # db.session.commit()
                    except Error as e:
                        print(e)
                        session['error_message'] = "Ошибка добавления ответа в базу данных"
                        return redirect(url_for('index'))
            session.pop('id_questionnaire', None)
            return redirect(url_for('index'))
    else:
        delete_questionnaire()
        return render_template('create.html', adding_questionnaire=True, adding_questions=False,
                               adding_answers=False, **user)


@app.route('/questionnaires/<int:id>', methods=['GET', 'POST'])
def questionnaire(id):
    # delete_questionnaire()
    user = get_params_user()

    connection, cursor = get_db()
    cursor.execute(select_questions, {'id_questionnaire': id})

    current_questionnaire = cursor.fetchall()
    # cursor.execute(select_questions)
    questions = cursor.fetchall()
    print(questions)
    if request.method == 'POST':
        if "end_questionnaire" in request.form:
            answers = []
            for question in questions:
                cursor.execute(update_number_of_selections, {'id_answer': request.form[str(question[0])]})
                connection.commit()
                cursor.execute(select_answers, {'id_question': str(question[0])})
                checked_answer = cursor.fetchall()
                answers.append(checked_answer[0])
            return render_template('questionnaire.html', result=True, questionnaire=current_questionnaire,
                                   questions=questions, **user, answers=answers)
        elif "repeat" in request.form:
            return redirect(url_for('questionnaire', id=id))
        elif "to_main" in request.form:
            return redirect(url_for('index'))
    else:
        return render_template('questionnaire.html', result=False, questionnaire=current_questionnaire,
                               questions=questions, **user)


@app.route('/statistics', methods=['GET', 'POST'])
def show_statistics():
    delete_questionnaire()
    user = get_params_user()
    if not user['admin']:
        return redirect(url_for('index'))
    connection, cursor = get_db()
    cursor.execute(select_query)
    questionnaires = cursor.fetchall()
    # questionnaires = Questionnaire.query.order_by(Questionnaire.id).all()
    current_questionnaire = None
    answers = []
    if request.method == 'POST':
        # current_questionnaire = Questionnaire.query.get(str(request.form['show_stat']))
        cursor.execute(select_questions, {'id_questionnaire': str(request.form['show_stat'])})
        current_questionnaire = cursor.fetchall()
        print(current_questionnaire)
        # current_questionnaire = Questionnaire.query.get(str(request.form['show_stat']))
        for question in current_questionnaire:
            a = []
            max_selection = 0
            cursor.execute(select_answers, {'id_question': request.form['show_stat']})
            answers = cursor.fetchall()
            for answer in answers:
                if len(a) == 0:
                    a.append(answer[0])
                    max_selection = answer[2]
                elif answer[2] > max_selection:
                    a.clear()
                    a.append(answer[0])
                    max_selection = answer[2]
                elif answer[2] == max_selection:
                    a.append(answer[0])
            answers.extend(a)
    return render_template('statistics.html', questionnaires=questionnaires, questionnaire=current_questionnaire,
                           answers=answers, **user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    current_user = get_params_user()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        connection, cursor = get_db()
        # user = User.query.filter(User.name == name).first()
        cursor.execute(select_user_by_name, {'name': name, 'password': password})
        user = cursor.fetchall()

        if len(user) > 0:
            return render_template('register.html', message="Пользователь уже существует", **current_user)

        status_id = 2
        if 'status_id' in request.form:
            status_id = 1

        # user = User(name=name, password=password, admin=admin)

        try:
            cursor.execute(insert_user, {'name': name, 'password': password, 'status_id': status_id})
            connection.commit()
            cursor.execute(select_user_by_name, {'name': name, 'password': password})
            user = cursor.fetchall()
            print(user)
            session['user_id'] = user[0][0]
            return redirect(url_for('index'))
        except Error as e:
            print(e)
            return render_template('register.html', message="Неправильный ввод", **current_user)
        finally:
            close_db(connection, cursor)

    current_user = get_params_user()
    return render_template('register.html', **current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    current_user = get_params_user()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        connection, cursor = get_db()
        cursor.execute(select_user_by_name, {'name': name, 'password': password})
        user = cursor.fetchall()
        # user = User.query.filter(User.name == name).first()
        close_db(connection, cursor)
        if len(user) == 0 or user[0][2] != password:
            return render_template('login.html', message="Неверные данные", **current_user)
        else:
            session['user_id'] = user[0][0]
            return redirect(url_for('index'))
    return render_template('login.html', **current_user)


@app.route('/users', methods=['GET', 'POST'])
def show_users():
    user = get_params_user()
    connection, cursor = get_db()
    if not user['admin']:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if "delete" in request.form:
            cursor.execute(delete_user, {'id_user': request.form['delete']})
            connection.commit()
        elif "make_admin" in request.form:
            cursor.execute(update_make_admin_user, {'id_user': request.form['make_admin']})
            connection.commit()
        elif "not_admin" in request.form:
            cursor.execute(update_not_admin_user, {'id_user': request.form['not_admin']})
            connection.commit()
    cursor.execute(select_user_full_info)
    all_users = cursor.fetchall()
    close_db(connection, cursor)
    print(all_users)
    return render_template('users.html', users=all_users, **user)


@app.route('/exit')
def exit():
    delete_questionnaire()
    session.pop('user_id', None)
    return redirect(url_for('index'))

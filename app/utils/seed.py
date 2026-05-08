from app.extensions import db
from app.models import AnswerOption, Question, Test, TestAssignment, User


ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'


def ensure_admin() -> User:
    admin = User.query.filter_by(username=ADMIN_USERNAME).first()
    if admin:
        return admin

    admin = User(username=ADMIN_USERNAME, role='admin', full_name='Системный администратор')
    admin.set_password(ADMIN_PASSWORD)
    db.session.add(admin)
    db.session.commit()
    return admin

def seed_demo_data() -> None:
    admin = ensure_admin()

    if Test.query.count() > 0 and User.query.filter(User.role == 'student').count() >= 2:
        return

    students_data = [
        ('student1', 'student123', 'Айжан Турсунова'),
        ('student2', 'student123', 'Нурбек Асанов'),
        ('student3', 'student123', 'Элина Мамбетова'),
    ]

    students = []
    for username, password, full_name in students_data:
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, role='student', full_name=full_name)
            user.set_password(password)
            db.session.add(user)
        students.append(user)

    if not Test.query.filter_by(title='Основы Python').first():
        python_test = Test(
            title='Основы Python',
            description='Базовый тест по синтаксису Python и структурам данных.',
            time_limit_minutes=20,
            max_attempts=2,
            questions_per_student=20,
            created_by=admin.id,
        )
        db.session.add(python_test)
        db.session.flush()

        q1 = Question(test=python_test, text='Какой тип данных используется для неизменяемой последовательности?', question_type='single')
        q2 = Question(test=python_test, text='Какие из перечисленных коллекций являются изменяемыми?', question_type='multiple')
        db.session.add_all([q1, q2])
        db.session.flush()

        db.session.add_all(
            [
                AnswerOption(question=q1, text='list', is_correct=False),
                AnswerOption(question=q1, text='tuple', is_correct=True),
                AnswerOption(question=q1, text='dict', is_correct=False),
                AnswerOption(question=q1, text='set', is_correct=False),
                AnswerOption(question=q2, text='list', is_correct=True),
                AnswerOption(question=q2, text='tuple', is_correct=False),
                AnswerOption(question=q2, text='dict', is_correct=True),
                AnswerOption(question=q2, text='str', is_correct=False),
            ]
        )

    if not Test.query.filter_by(title='Основы веб-разработки').first():
        web_test = Test(
            title='Основы веб-разработки',
            description='Проверка базовых знаний HTML, CSS и HTTP.',
            time_limit_minutes=15,
            max_attempts=1,
            questions_per_student=20,
            created_by=admin.id,
        )
        db.session.add(web_test)
        db.session.flush()

        q1 = Question(test=web_test, text='Какой тег используется для самой крупной заголовочной строки?', question_type='single')
        q2 = Question(test=web_test, text='Какие технологии относятся к клиентской части веб-приложения?', question_type='multiple')
        db.session.add_all([q1, q2])
        db.session.flush()

        db.session.add_all(
            [
                AnswerOption(question=q1, text='<h1>', is_correct=True),
                AnswerOption(question=q1, text='<head>', is_correct=False),
                AnswerOption(question=q1, text='<title>', is_correct=False),
                AnswerOption(question=q1, text='<p>', is_correct=False),
                AnswerOption(question=q2, text='HTML', is_correct=True),
                AnswerOption(question=q2, text='CSS', is_correct=True),
                AnswerOption(question=q2, text='JavaScript', is_correct=True),
                AnswerOption(question=q2, text='SQLite', is_correct=False),
            ]
        )

    db.session.commit()

    python_test = Test.query.filter_by(title='Основы Python').first()
    web_test = Test.query.filter_by(title='Основы веб-разработки').first()
    students = User.query.filter(User.username.in_(['student1', 'student2', 'student3'])).all()

    assignments = [
        (students[0], python_test),
        (students[0], web_test),
        (students[1], python_test),
        (students[2], web_test),
    ]

    for student, test in assignments:
        exists = TestAssignment.query.filter_by(user_id=student.id, test_id=test.id).first()
        if not exists:
            db.session.add(TestAssignment(user_id=student.id, test_id=test.id))

    db.session.commit()

    python_test = Test.query.filter_by(title='Основы Python').first()
    web_test = Test.query.filter_by(title='Основы веб-разработки').first()
    students = User.query.filter(User.username.in_(['student1', 'student2', 'student3'])).all()

    assignments = [
        (students[0], python_test),
        (students[0], web_test),
        (students[1], python_test),
        (students[2], web_test),
    ]

    for student, test in assignments:
        exists = TestAssignment.query.filter_by(user_id=student.id, test_id=test.id).first()
        if not exists:
            db.session.add(TestAssignment(user_id=student.id, test_id=test.id))

    db.session.commit()

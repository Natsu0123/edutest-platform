from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange


QUESTION_TYPE_CHOICES = [
    ('single_choice', 'single_choice'),
    ('multiple_choice', 'multiple_choice'),
    ('matching', 'matching'),
    ('text', 'text'),
    ('ordering', 'ordering'),
]


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=3, max=128)])
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired(), Length(min=3, max=120)])
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=3, max=128)])
    confirm_password = PasswordField(
        'Повтори пароль',
        validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')],
    )
    submit = SubmitField('Создать аккаунт')


class CreateTestForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Описание', validators=[DataRequired(), Length(min=5)])
    time_limit_minutes = IntegerField('Лимит времени, минут', validators=[DataRequired(), NumberRange(min=1, max=300)])
    max_attempts = IntegerField('Количество попыток', validators=[DataRequired(), NumberRange(min=1, max=20)])
    submit = SubmitField('Создать')
    target_score = IntegerField('Общий балл теста', validators=[DataRequired(), NumberRange(min=1, max=1000)])
    questions_per_student = IntegerField('Макс вопросов', validators=[DataRequired(), NumberRange(min=1, max=100)])


class UploadTestsForm(FlaskForm):
    file = FileField(
        'Файл с тестами',
        validators=[
            FileRequired(),
            FileAllowed(['txt', 'docx', 'xlsx', 'zip'], 'Разрешены только файлы .txt, .docx и .xlsx. и .zip'),
        ],
    )
    time_limit_minutes = IntegerField('Лимит времени, минут', validators=[DataRequired(), NumberRange(min=1, max=300)], default=20)
    max_attempts = IntegerField('Количество попыток', validators=[DataRequired(), NumberRange(min=1, max=20)], default=1)
    auto_assign = BooleanField('Сразу назначить ученикам', default=False)
    auto_assign_count = IntegerField('Сколько тестов назначить каждому ученику', validators=[NumberRange(min=0, max=200)], default=0)
    submit = SubmitField('Загрузить и создать тесты')


class QuestionTypeForm(FlaskForm):
    question_type = SelectField('Тип вопроса', choices=QUESTION_TYPE_CHOICES)

class CreateUserForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired(), Length(min=3, max=120)])
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=3, max=128)])
    role = SelectField(
        'Роль',
        choices=[
            ('student', 'student'),
            ('teacher', 'teacher'),
            ('admin', 'admin'),
        ],
        validators=[DataRequired()],
    )
    group_id = SelectField('Группа', coerce=int, choices=[(0, 'Без группы')])
    submit = SubmitField('Создать пользователя')

class EditUserForm(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired(), Length(min=3, max=120)])
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Новый пароль', validators=[Length(min=0, max=128)])
    role = SelectField(
        'Роль',
        choices=[
            ('student', 'student'),
            ('teacher', 'teacher'),
            ('admin', 'admin'),
        ],
        validators=[DataRequired()],
    )
    group_id = SelectField('Группа', coerce=int, choices=[(0, 'Без группы')])
    submit = SubmitField('Сохранить изменения')

class UploadGroupForm(FlaskForm):
    file = FileField('Excel файл группы', validators=[DataRequired()])
    submit = SubmitField('Импортировать группу')

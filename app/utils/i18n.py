from __future__ import annotations

from flask import g, request, session


LANGUAGES = {
    'ru': 'Русский',
    'uz': 'Oʻzbekcha',
    'en': 'English',
}

COMMON_TRANSLATIONS = {
    'brand': {'ru': 'EduTest', 'uz': 'EduTest', 'en': 'EduTest'},
    'subtitle': {'ru': 'Минималистичная система онлайн-тестирования', 'uz': 'Minimal onlayn test tizimi', 'en': 'Minimal online testing platform'},
    'nav.admin': {'ru': 'Админ-панель', 'uz': 'Admin panel', 'en': 'Admin panel'},
    'nav.import': {'ru': 'Импорт тестов', 'uz': 'Test importi', 'en': 'Import tests'},
    'nav.users': {'ru': 'Пользователи', 'uz': 'Foydalanuvchilar', 'en': 'Users'},
    'nav.tests': {'ru': 'Тесты', 'uz': 'Testlar', 'en': 'Tests'},
    'nav.results': {'ru': 'Результаты', 'uz': 'Natijalar', 'en': 'Results'},
    'nav.dashboard': {'ru': 'Кабинет', 'uz': 'Kabinet', 'en': 'Dashboard'},
    'nav.my_results': {'ru': 'Мои результаты', 'uz': 'Mening natijalarim', 'en': 'My results'},
    'nav.logout': {'ru': 'Выход', 'uz': 'Chiqish', 'en': 'Logout'},
    'nav.login': {'ru': 'Вход', 'uz': 'Kirish', 'en': 'Login'},
    'nav.register': {'ru': 'Регистрация', 'uz': 'Roʻyxatdan oʻtish', 'en': 'Register'},
    'nav.groups': {'ru': 'Группы', 'uz': 'Guruhlar', 'en': 'Groups'},

    'base.subtitle': {
        'ru': 'Онлайн тест система',
        'uz': 'Onlayn test tizimi',
        'en': 'Online test system'
    },

    'admin.groups_title': {
        'ru': 'Группы',
        'uz': 'Guruhlar',
        'en': 'Groups'
    },
    'admin.groups_desc': {
        'ru': 'Управление учебными группами',
        'uz': 'O‘quv guruhlarini boshqarish',
        'en': 'Manage study groups'
    },
    'admin.group_import': {
        'ru': 'Импорт группы',
        'uz': 'Guruh importi',
        'en': 'Import group'
    },
    'admin.group_students_count': {
        'ru': 'Студентов: {count}',
        'uz': 'Talabalar soni: {count}',
        'en': 'Students: {count}'
    },
    'admin.group_open': {
        'ru': 'Открыть группу',
        'uz': 'Guruhni ochish',
        'en': 'Open group'
    },
    'admin.assign_teachers': {
        'ru': 'Назначение учителей',
        'uz': 'O‘qituvchilarni biriktirish',
        'en': 'Assign teachers'
    },
    'admin.assign_teachers_desc': {
        'ru': 'Выберите, какие учителя прикреплены к группе {group}',
        'uz': '{group} guruhiga biriktirilgan o‘qituvchilarni tanlang',
        'en': 'Choose which teachers are assigned to group {group}'
    },
    'admin.save_assignment': {
        'ru': 'Сохранить назначение',
        'uz': 'Biriktirishni saqlash',
        'en': 'Save assignment'
    },
    'admin.import_auto_assign': {
        'ru': 'Сразу назначить ученикам',
        'uz': 'Darhol o‘quvchilarga biriktirish',
        'en': 'Assign to students immediately'
    },
    'admin.import_auto_assign_count': {
        'ru': 'Сколько тестов назначить каждому ученику',
        'uz': 'Har bir o‘quvchiga nechta test biriktirilsin',
        'en': 'How many tests to assign to each student'
    },
    'admin.import_auto_assign_hint': {
        'ru': '0 = не назначать автоматически (админ назначит вручную на странице теста).',
        'uz': '0 = avtomatik biriktirilmaydi (admin test sahifasida qo‘lda biriktiradi).',
        'en': '0 = do not assign automatically (admin will assign manually on the test page).'
    },
    'admin.import_example_title': {
        'ru': 'Пример TXT / Word формата',
        'uz': 'TXT / Word formatiga misol',
        'en': 'TXT / Word format example'
    },
    'admin.download_template': {
        'ru': 'Скачать шаблон заполнения тестов',
        'uz': 'Testlarni to‘ldirish shablonini yuklab olish',
        'en': 'Download test import template'
    },
    'admin.template_filename': {
        'ru': 'shablon_test_importa.txt',
        'uz': 'test_import_shabloni.txt',
        'en': 'test_import_template.txt'
    },
    'admin.group_page_title': {
        'ru': 'Группа {group}',
        'uz': '{group} guruhi',
        'en': 'Group {group}'
    },
    'admin.group_page_desc': {
        'ru': 'Список участников группы',
        'uz': 'Guruh ishtirokchilari ro‘yxati',
        'en': 'List of group members'
    },
    'admin.back_to_users': {
        'ru': 'Назад к пользователям',
        'uz': 'Foydalanuvchilarga qaytish',
        'en': 'Back to users'
    },
    'admin.no_students_in_group': {
        'ru': 'В этой группе пока нет студентов',
        'uz': 'Bu guruhda hozircha talabalar yo‘q',
        'en': 'There are no students in this group yet'
    },
    'admin.import_example_block_title': {
        'ru': 'Готовый пример для импорта',
        'uz': 'Import uchun tayyor misol',
        'en': 'Ready example for import'
    },
    'common.edit': {'ru': 'Редактировать', 'uz': 'Tahrirlash', 'en': 'Edit'},
    'common.delete': {'ru': 'Удалить', 'uz': 'O‘chirish', 'en': 'Delete'},
    'common.duplicate': {'ru': 'Дублировать', 'uz': 'Nusxalash', 'en': 'Duplicate'},
    'common.actions': {'ru': 'Действия', 'uz': 'Amallar', 'en': 'Actions'},
    'admin.tests_list': {'ru': 'Список тестов', 'uz': 'Testlar ro‘yxati', 'en': 'Test list'},
    'admin.tests_list_desc': {
        'ru': 'Открывай, редактируй, удаляй или переходи к назначениям.',
        'uz': 'Testlarni ochish, tahrirlash, o‘chirish yoki biriktirishlarga o‘tish.',
        'en': 'Open, edit, delete, or manage assignments.'
    },
    'language.label': {'ru': 'Язык', 'uz': 'Til', 'en': 'Language'},
    'common.title': {'ru': 'Название', 'uz': 'Nomi', 'en': 'Title'},
    'common.description': {'ru': 'Описание', 'uz': 'Tavsif', 'en': 'Description'},
    'common.time': {'ru': 'Время', 'uz': 'Vaqt', 'en': 'Time'},
    'common.attempts': {'ru': 'Попытки', 'uz': 'Urinishlar', 'en': 'Attempts'},
    'common.questions': {'ru': 'Вопросы', 'uz': 'Savollar', 'en': 'Questions'},
    'common.status': {'ru': 'Статус', 'uz': 'Holat', 'en': 'Status'},
    'common.action': {'ru': 'Действие', 'uz': 'Amal', 'en': 'Action'},
    'common.open': {'ru': 'Открыть', 'uz': 'Ochish', 'en': 'Open'},
    'common.file': {'ru': 'Файл с тестами', 'uz': 'Test fayli', 'en': 'Test file'},
    'common.users': {'ru': 'Студенты', 'uz': 'Talabalar', 'en': 'Students'},
    'common.minutes_suffix': {'ru': 'мин.', 'uz': 'daq.', 'en': 'min.'},
    'status.done': {'ru': 'завершен', 'uz': 'yakunlangan', 'en': 'completed'},
    'status.not_started': {'ru': 'не начат', 'uz': 'boshlanmagan', 'en': 'not started'},
    'question_type.single_choice': {'ru': 'Один правильный ответ', 'uz': 'Bitta toʻgʻri javob', 'en': 'Single choice'},
    'question_type.multiple_choice': {'ru': 'Несколько правильных ответов', 'uz': 'Bir nechta toʻgʻri javob', 'en': 'Multiple choice'},
    'question_type.matching': {'ru': 'Сопоставление', 'uz': 'Moslashtirish', 'en': 'Matching'},
    'question_type.text': {'ru': 'Текстовый ответ', 'uz': 'Matnli javob', 'en': 'Text answer'},
    'question_type.ordering': {'ru': 'Правильный порядок', 'uz': 'Toʻgʻri tartib', 'en': 'Ordering'},
    'auth.login_title': {'ru': 'Вход в систему', 'uz': 'Tizimga kirish', 'en': 'Sign in'},
    'auth.login_required': {'ru': 'Пожалуйста, войдите в систему.', 'uz': 'Iltimos, tizimga kiring.', 'en': 'Please sign in.'},
    'auth.login_locked': {'ru': 'Слишком много неудачных попыток входа. Повторите через {minutes} минут.', 'uz': 'Kirish urinishlari juda ko‘p. {minutes} daqiqadan keyin qayta urinib ko‘ring.', 'en': 'Too many failed login attempts. Try again in {minutes} minutes.'},
    'auth.login_desc': {'ru': 'Введите логин и пароль для доступа к платформе тестирования.', 'uz': 'Platformaga kirish uchun login va parolni kiriting.', 'en': 'Enter your username and password to access the testing platform.'},
    'auth.username': {'ru': 'Логин', 'uz': 'Login', 'en': 'Username'},
    'auth.password': {'ru': 'Пароль', 'uz': 'Parol', 'en': 'Password'},
    'auth.no_account': {'ru': 'Нет аккаунта студента?', 'uz': 'Talaba akkauntingiz yoʻqmi?', 'en': 'No student account yet?'},
    'auth.register_link': {'ru': 'Зарегистрироваться', 'uz': 'Roʻyxatdan oʻtish', 'en': 'Register'},
    'auth.register_title': {'ru': 'Регистрация студента', 'uz': 'Talaba roʻyxatdan oʻtishi', 'en': 'Student registration'},
    'auth.register_desc': {'ru': 'Открытая регистрация доступна только для роли student.', 'uz': 'Ochiq roʻyxatdan oʻtish faqat student roli uchun mavjud.', 'en': 'Open registration is available only for the student role.'},
    'auth.full_name': {'ru': 'ФИО', 'uz': 'F.I.Sh.', 'en': 'Full name'},
    'auth.have_account': {'ru': 'Уже есть аккаунт?', 'uz': 'Akkauntingiz bormi?', 'en': 'Already have an account?'},
    'auth.login_success': {'ru': 'Вход выполнен успешно.', 'uz': 'Muvaffaqiyatli kirildi.', 'en': 'Signed in successfully.'},
    'auth.login_error': {'ru': 'Неверный логин или пароль.', 'uz': 'Login yoki parol notoʻgʻri.', 'en': 'Invalid username or password.'},
    'auth.user_exists': {'ru': 'Пользователь с таким логином уже существует.', 'uz': 'Bunday loginli foydalanuvchi allaqachon mavjud.', 'en': 'A user with this username already exists.'},
    'auth.register_success': {'ru': 'Регистрация завершена. Теперь вы можете войти.', 'uz': 'Roʻyxatdan oʻtish yakunlandi. Endi tizimga kirishingiz mumkin.', 'en': 'Registration completed. You can now sign in.'},
    'auth.logout_success': {'ru': 'Вы вышли из системы.', 'uz': 'Siz tizimdan chiqdingiz.', 'en': 'You have been signed out.'},
    'lang.changed': {'ru': 'Язык интерфейса обновлен.', 'uz': 'Interfeys tili yangilandi.', 'en': 'Interface language updated.'},
    'admin.dashboard_title': {'ru': 'Админ-панель', 'uz': 'Admin panel', 'en': 'Admin panel'},
    'admin.dashboard_desc': {'ru': 'Управление пользователями, тестами, файлами импорта, назначениями и результатами.', 'uz': 'Foydalanuvchilar, testlar, import fayllari, biriktirishlar va natijalarni boshqarish.', 'en': 'Manage users, tests, import files, assignments and results.'},
    'admin.upload_file': {'ru': 'Загрузить файл', 'uz': 'Fayl yuklash', 'en': 'Upload file'},
    'admin.seed_demo': {'ru': 'Заполнить demo-данными', 'uz': 'Demo maʼlumotlarni toʻldirish', 'en': 'Fill demo data'},
    'admin.test_list': {'ru': 'Список тестов', 'uz': 'Testlar roʻyxati', 'en': 'Test list'},
    'admin.test_list_desc': {'ru': 'Здесь отображаются тесты, загруженные вручную и импортированные из файлов.', 'uz': 'Bu yerda qoʻlda yaratilgan va fayldan import qilingan testlar ko‘rsatiladi.', 'en': 'This page shows manually created and imported tests.'},
    'admin.all_tests': {'ru': 'Все тесты', 'uz': 'Barcha testlar', 'en': 'All tests'},
    'admin.import_title': {'ru': 'Импорт тестов из файла', 'uz': 'Fayldan test importi', 'en': 'Import tests from file'},
    'admin.import_desc': {'ru': 'Поддерживаются форматы `.xlsx`, `.docx`, `.txt`. Для правильного ответа используйте префикс `*`.', 'uz': '`.xlsx`, `.docx`, `.txt` formatlari qoʻllab-quvvatlanadi. Toʻgʻri javob uchun `*` prefiksidan foydalaning.', 'en': 'Supported formats: `.xlsx`, `.docx`, `.txt`. Use the `*` prefix for the correct answer.'},
    'admin.supported_formats': {'ru': 'Поддерживаемые форматы', 'uz': 'Qoʻllab-quvvatlanadigan formatlar', 'en': 'Supported formats'},
    'admin.import_help_excel': {
    'ru': 'Excel: каждый лист = отдельный тест. Формат строки: type | question | points | data1 | data2 ... Для single/multiple указывайте варианты ответов, для text — один правильный ответ с *, для matching — пары в виде Лево=Право, для ordering — элементы по порядку.',
    'uz': 'Excel: har bir sheet = alohida test. Satr formati: type | question | points | data1 | data2 ... Single/multiple uchun javob variantlari, text uchun * bilan bitta to‘g‘ri javob, matching uchun Chap=O‘ng juftliklar, ordering uchun esa tartib bo‘yicha elementlar yoziladi.',
    'en': 'Excel: each sheet is a separate test. Row format: type | question | points | data1 | data2 ... For single/multiple use answer options, for text use one correct answer with *, for matching use pairs like Left=Right, and for ordering use items in the correct order.'
},
    'admin.import_help_word': {'ru': 'Word: строка вида Вопрос | *Правильный | Вариант 2 | Вариант 3.', 'uz': 'Word: satr ko‘rinishi Savol | *Toʻgʻri | Variant 2 | Variant 3.', 'en': 'Word: one line like Question | *Correct | Option 2 | Option 3.'},
    'admin.import_help_txt': {'ru': 'TXT: аналогично Word, можно разделять тесты строками Тест: Название или # Название.', 'uz': 'TXT: Word kabi, testlarni Test: Nomi yoki # Nomi satrlari bilan ajratish mumkin.', 'en': 'TXT: same as Word, tests can be separated with lines like Test: Title or # Title.'},
    'admin.create_test': {'ru': 'Создать тест', 'uz': 'Test yaratish', 'en': 'Create test'},
    'admin.import_from_file': {'ru': 'Импорт из файла', 'uz': 'Fayldan import', 'en': 'Import from file'},
    'admin.tests_title': {'ru': 'Тесты', 'uz': 'Testlar', 'en': 'Tests'},
    'admin.tests_desc': {'ru': 'Список тестов и быстрый переход к управлению.', 'uz': 'Testlar roʻyxati va boshqaruvga tez oʻtish.', 'en': 'List of tests and quick access to management.'},
    'admin.no_tests': {'ru': 'Тесты пока не созданы.', 'uz': 'Hozircha testlar yaratilmagan.', 'en': 'No tests have been created yet.'},
    'admin.not_uploaded_tests': {'ru': 'Тесты пока не загружены.', 'uz': 'Hozircha testlar yuklanmagan.', 'en': 'No tests have been uploaded yet.'},
    'admin.upload_success': {'ru': 'Файл «{filename}» успешно загружен. Создано тестов: {count}.', 'uz': '«{filename}» fayli muvaffaqiyatli yuklandi. Yaratilgan testlar soni: {count}.', 'en': 'File “{filename}” uploaded successfully. Tests created: {count}.'},
    'admin.parse_error': {'ru': 'Ошибка парсинга файла: {error}', 'uz': 'Faylni tahlil qilishda xato: {error}', 'en': 'File parsing error: {error}'},
    'admin.test_created': {'ru': 'Тест создан.', 'uz': 'Test yaratildi.', 'en': 'Test created.'},
    'admin.question_added': {'ru': 'Вопрос добавлен.', 'uz': 'Savol qoʻshildi.', 'en': 'Question added.'},
    'admin.assignments_saved': {'ru': 'Назначения сохранены.', 'uz': 'Biriktirishlar saqlandi.', 'en': 'Assignments saved.'},
    'admin.test_deleted': {'ru': 'Тест удалён: {title}', 'uz': 'Test o‘chirildi: {title}', 'en': 'Test deleted: {title}'},
    'admin.seed_success': {'ru': 'Демонстрационные данные созданы или уже существовали.', 'uz': 'Demo maʼlumotlar yaratildi yoki avvaldan mavjud edi.', 'en': 'Demo data created or already existed.'},
    'admin.question_text_required': {'ru': 'Введите текст вопроса.', 'uz': 'Savol matnini kiriting.', 'en': 'Enter question text.'},
    'admin.need_two_options': {'ru': 'Добавьте текст вопроса и минимум два варианта ответа.', 'uz': 'Savol va kamida ikki javob variantini qoʻshing.', 'en': 'Add question text and at least two answer options.'},
    'admin.need_one_correct': {'ru': 'Отметьте хотя бы один правильный вариант.', 'uz': 'Kamida bitta toʻgʻri variantni belgilang.', 'en': 'Mark at least one correct option.'},
    'admin.single_only_one_correct': {'ru': 'Для одиночного выбора должен быть только один правильный ответ.', 'uz': 'Bitta tanlov uchun faqat bitta toʻgʻri javob bo‘lishi kerak.', 'en': 'Single choice questions must have exactly one correct answer.'},
    'admin.text_answer_required': {'ru': 'Для текстового вопроса укажите правильный ответ.', 'uz': 'Matnli savol uchun toʻgʻri javobni kiriting.', 'en': 'Provide the correct answer for the text question.'},
    'admin.matching_pairs_required': {'ru': 'Для сопоставления добавьте минимум две пары и заполните обе колонки.', 'uz': 'Moslashtirish uchun kamida ikkita juftlikni kiriting va ikkala ustunni ham toʻldiring.', 'en': 'Add at least two matching pairs and fill both columns.'},
    'admin.ordering_items_required': {'ru': 'Для сортировки добавьте минимум два элемента.', 'uz': 'Tartiblash uchun kamida ikkita element qoʻshing.', 'en': 'Add at least two items for ordering.'},
    'admin.unsupported_question_type': {'ru': 'Неподдерживаемый тип вопроса.', 'uz': 'Qoʻllab-quvvatlanmaydigan savol turi.', 'en': 'Unsupported question type.'},
    'admin.add_question_title': {'ru': 'Добавление вопроса', 'uz': 'Savol qoʻshish', 'en': 'Add question'},
    'admin.add_question_heading': {'ru': 'Добавление вопроса в тест «{title}»', 'uz': '«{title}» testiga savol qoʻshish', 'en': 'Add question to test “{title}”'},
    'admin.question_text': {'ru': 'Текст вопроса', 'uz': 'Savol matni', 'en': 'Question text'},
    'admin.question_type': {'ru': 'Тип вопроса', 'uz': 'Savol turi', 'en': 'Question type'},
    'admin.answer_options': {'ru': 'Варианты ответа', 'uz': 'Javob variantlari', 'en': 'Answer options'},
    'admin.option_placeholder': {'ru': 'Вариант {index}', 'uz': 'Variant {index}', 'en': 'Option {index}'},
    'admin.correct_option': {'ru': 'Правильный', 'uz': 'Toʻgʻri', 'en': 'Correct'},
    'admin.add_question_button': {'ru': 'Добавить вопрос', 'uz': 'Savol qoʻshish', 'en': 'Add question'},
    'admin.text_correct_answer': {'ru': 'Правильный текстовый ответ', 'uz': 'Toʻgʻri matnli javob', 'en': 'Correct text answer'},
    'admin.matching_left': {'ru': 'Левая колонка', 'uz': 'Chap ustun', 'en': 'Left column'},
    'admin.matching_right': {'ru': 'Правая колонка', 'uz': 'Oʻng ustun', 'en': 'Right column'},
    'admin.ordering_items': {'ru': 'Элементы в правильном порядке', 'uz': 'Toʻgʻri tartibdagi elementlar', 'en': 'Items in correct order'},
    'admin.form_section_choice': {'ru': 'Для этого типа заполните варианты ответа ниже.', 'uz': 'Bu tur uchun quyida javob variantlarini toʻldiring.', 'en': 'Fill answer options below for this type.'},
    'admin.form_section_matching': {'ru': 'Введите пары для сопоставления.', 'uz': 'Moslashtirish juftliklarini kiriting.', 'en': 'Enter matching pairs.'},
    'admin.form_section_ordering': {'ru': 'Введите элементы в правильном порядке.', 'uz': 'Elementlarni toʻgʻri tartibda kiriting.', 'en': 'Enter items in the correct order.'},
    'admin.form_section_text': {'ru': 'Введите правильный текстовый ответ.', 'uz': 'Toʻgʻri matnli javobni kiriting.', 'en': 'Enter the correct text answer.'},
    'admin.details_title': {'ru': 'Параметры теста', 'uz': 'Test parametrlari', 'en': 'Test details'},
    'admin.questions_title': {'ru': 'Вопросы', 'uz': 'Savollar', 'en': 'Questions'},
    'admin.no_questions': {'ru': 'Для теста пока нет вопросов.', 'uz': 'Bu testda hali savollar yoʻq.', 'en': 'This test has no questions yet.'},
    'admin.assign_students': {'ru': 'Назначение студентам', 'uz': 'Talabalarga biriktirish', 'en': 'Assign to students'},
    'admin.save_assignments': {'ru': 'Сохранить назначения', 'uz': 'Biriktirishlarni saqlash', 'en': 'Save assignments'},
    'admin.results_title': {'ru': 'Все результаты', 'uz': 'Barcha natijalar', 'en': 'All results'},
    'admin.results_students_title': {'ru': 'Результаты студентов', 'uz': 'Talabalar natijalari', 'en': 'Student results'},
    'admin.results_desc': {'ru': 'Все завершенные попытки по тестам системы.', 'uz': 'Tizimdagi barcha yakunlangan urinishlar.', 'en': 'All completed attempts in the system.'},
    'admin.result_student': {'ru': 'Студент', 'uz': 'Talaba', 'en': 'Student'},
    'admin.result_test': {'ru': 'Тест', 'uz': 'Test', 'en': 'Test'},
    'admin.result_started': {'ru': 'Начало', 'uz': 'Boshlanishi', 'en': 'Started'},
    'admin.result_finished': {'ru': 'Завершение', 'uz': 'Yakunlangan', 'en': 'Finished'},
    'admin.result_score': {'ru': 'Результат', 'uz': 'Natija', 'en': 'Score'},
    'admin.filter_all': {'ru': 'Все', 'uz': 'Barchasi', 'en': 'All'},
    'admin.apply_filters': {'ru': 'Применить фильтры', 'uz': 'Filtrlarni qoʻllash', 'en': 'Apply filters'},
    'admin.export_excel': {'ru': 'Экспорт в Excel', 'uz': 'Excelga eksport', 'en': 'Export to Excel'},
    'admin.no_finished_attempts': {'ru': 'Пока нет завершенных попыток.', 'uz': 'Hali yakunlangan urinishlar yoʻq.', 'en': 'There are no completed attempts yet.'},
    'admin.users_title': {'ru': 'Пользователи', 'uz': 'Foydalanuvchilar', 'en': 'Users'},
    'admin.users_desc': {'ru': 'Список администраторов и студентов системы.', 'uz': 'Tizim administratorlari va talabalari roʻyxati.', 'en': 'List of system admins and students.'},
    'admin.full_name': {'ru': 'ФИО', 'uz': 'F.I.Sh.', 'en': 'Full name'},
    'admin.username': {'ru': 'Логин', 'uz': 'Login', 'en': 'Username'},
    'admin.role': {'ru': 'Роль', 'uz': 'Rol', 'en': 'Role'},
    'admin.create_test_title': {'ru': 'Создание теста', 'uz': 'Test yaratish', 'en': 'Create test'},
    'admin.result_tab_switches': {
        'ru': 'Переключения вкладок',
        'uz': 'Oynadan chiqishlar',
        'en': 'Tab switches'
    },
    'student.dashboard_title': {'ru': 'Личный кабинет', 'uz': 'Shaxsiy kabinet', 'en': 'Student dashboard'},
    'student.welcome': {'ru': 'Добро пожаловать, {name}.', 'uz': 'Xush kelibsiz, {name}.', 'en': 'Welcome, {name}.'},
    'student.history': {'ru': 'История результатов', 'uz': 'Natijalar tarixi', 'en': 'Results history'},
    'student.assigned_tests': {'ru': 'Назначенные тесты', 'uz': 'Biriktirilgan testlar', 'en': 'Assigned tests'},
    'student.no_assigned': {'ru': 'Пока нет назначенных тестов.', 'uz': 'Hozircha biriktirilgan testlar yoʻq.', 'en': 'There are no assigned tests yet.'},
    'student.start_test': {'ru': 'Начать тест', 'uz': 'Testni boshlash', 'en': 'Start test'},
    'student.attempts_over': {'ru': 'Попытки закончились', 'uz': 'Urinishlar tugagan', 'en': 'No attempts left'},
    'student.results_title': {'ru': 'Мои результаты', 'uz': 'Mening natijalarim', 'en': 'My results'},
    'student.results_desc': {'ru': 'История завершенных попыток по назначенным тестам.', 'uz': 'Biriktirilgan testlar bo‘yicha yakunlangan urinishlar tarixi.', 'en': 'History of completed attempts for assigned tests.'},
    'student.no_results': {'ru': 'У вас пока нет завершенных попыток.', 'uz': 'Hozircha yakunlangan urinishlaringiz yoʻq.', 'en': 'You have no completed attempts yet.'},
    'student.take_title': {'ru': 'Прохождение теста', 'uz': 'Test topshirish', 'en': 'Take test'},
    'student.time_left': {'ru': 'Осталось времени:', 'uz': 'Qolgan vaqt:', 'en': 'Time left:'},
    'student.submit_test': {'ru': 'Отправить тест', 'uz': 'Testni yuborish', 'en': 'Submit test'},
    'student.result_title': {'ru': 'Результат теста', 'uz': 'Test natijasi', 'en': 'Test result'},
    'student.back_dashboard': {'ru': 'Вернуться в кабинет', 'uz': 'Kabinetga qaytish', 'en': 'Back to dashboard'},
    'student.back_history': {'ru': 'К истории результатов', 'uz': 'Natijalar tarixiga', 'en': 'Back to results history'},
    'student.limit_reached': {'ru': 'Лимит попыток исчерпан.', 'uz': 'Urinishlar limiti tugadi.', 'en': 'Attempt limit reached.'},
    'student.start_first': {'ru': 'Сначала начните тест.', 'uz': 'Avval testni boshlang.', 'en': 'Start the test first.'},
    'student.time_expired': {'ru': 'Время теста истекло. Попытка отправлена автоматически.', 'uz': 'Test vaqti tugadi. Urinish avtomatik yuborildi.', 'en': 'Time is over. The attempt was submitted automatically.'},
    'student.attempt_missing': {'ru': 'Активная попытка не найдена или уже отправлена.', 'uz': 'Faol urinish topilmadi yoki allaqachon yuborilgan.', 'en': 'Active attempt not found or already submitted.'},
    'student.submit_success': {'ru': 'Тест успешно завершен.', 'uz': 'Test muvaffaqiyatli yakunlandi.', 'en': 'Test submitted successfully.'},
    'student.text_placeholder': {'ru': 'Введите ответ', 'uz': 'Javobni kiriting', 'en': 'Enter your answer'},
    'student.match_left': {'ru': 'Левая часть', 'uz': 'Chap qism', 'en': 'Left side'},
    'student.match_right': {'ru': 'Правая часть', 'uz': 'Oʻng qism', 'en': 'Right side'},
    'student.order_position': {'ru': 'Позиция', 'uz': 'Pozitsiya', 'en': 'Position'},
    'student.correct_answers': {'ru': 'Правильных ответов', 'uz': 'Toʻgʻri javoblar', 'en': 'Correct answers'},
    'student.tab_switch_warning': {'ru': 'Во время теста зафиксировано переключение вкладки: {count}.', 'uz': 'Test davomida oynadan chiqish qayd etildi: {count}.', 'en': 'Tab switching was detected during the test: {count}.'},
    'error.file_too_large': {'ru': 'Файл слишком большой', 'uz': 'Fayl juda katta', 'en': 'File is too large'},
    'error.file_too_large_desc': {'ru': 'Максимальный размер загружаемого файла — 5 МБ.', 'uz': 'Yuklanadigan faylning maksimal hajmi — 5 MB.', 'en': 'Maximum upload size is 5 MB.'},
    'error.back_upload': {'ru': 'Вернуться к загрузке', 'uz': 'Yuklash sahifasiga qaytish', 'en': 'Back to upload'},
}

TRANSLATIONS = {lang: {} for lang in LANGUAGES}
for key, values in COMMON_TRANSLATIONS.items():
    for lang in LANGUAGES:
        TRANSLATIONS[lang][key] = values[lang]


def get_current_language() -> str:
    session_lang = session.get('language')
    if session_lang in LANGUAGES:
        return session_lang

    request_lang = request.args.get('lang')
    if request_lang in LANGUAGES:
        session['language'] = request_lang
        return request_lang

    return 'ru'



def translate(key: str, **kwargs) -> str:
    language = getattr(g, 'language', 'ru')
    value = TRANSLATIONS.get(language, {}).get(key) or TRANSLATIONS['ru'].get(key) or key
    if kwargs:
        return value.format(**kwargs)
    return value



def init_i18n(app) -> None:
    @app.before_request
    def set_language():
        g.language = get_current_language()

    @app.context_processor
    def inject_translations():
        return {
            '_': translate,
            'current_language': getattr(g, 'language', 'ru'),
            'available_languages': LANGUAGES,
        }

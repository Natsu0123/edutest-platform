from __future__ import annotations

import argparse
import shutil
from pathlib import Path


# Список файлов, которые формируют полный учебный проект.
PROJECT_FILES = [
    '.gitignore',
    'README.md',
    'requirements.txt',
    'run.py',
    'generate_edutest_project.py',
    'app/__init__.py',
    'app/extensions.py',
    'app/forms.py',
    'app/models.py',
    'app/routes/__init__.py',
    'app/routes/admin.py',
    'app/routes/auth.py',
    'app/routes/student.py',
    'app/utils/__init__.py',
    'app/utils/seed.py',
    'app/utils/i18n.py',
    'app/utils/parsers.py',
    'app/static/css/style.css',
    'app/static/js/timer.js',
    'app/templates/base.html',
    'app/templates/auth/login.html',
    'app/templates/auth/register.html',
    'app/templates/student/dashboard.html',
    'app/templates/student/results.html',
    'app/templates/student/take_test.html',
    'app/templates/student/attempt_result.html',
    'app/templates/admin/dashboard.html',
    'app/templates/admin/users.html',
    'app/templates/admin/tests.html',
    'app/templates/admin/create_test.html',
    'app/templates/admin/test_detail.html',
    'app/templates/admin/add_question.html',
    'app/templates/admin/results.html',
    'app/templates/errors/413.html',
    'app/templates/admin/upload_tests.html',
    'instance/.gitkeep',
    'instance/uploads/.gitkeep',
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Безопасно добавляет отсутствующие файлы EduTest в указанную директорию, не перезаписывая существующие.'
    )
    parser.add_argument(
        'target',
        nargs='?',
        default='edutest_generated',
        help='Папка, в которой нужно создать недостающие файлы проекта.',
    )
    return parser.parse_args()



def copy_project_file(source_root: Path, target_root: Path, relative_path: str) -> bool:
    source_path = source_root / relative_path
    target_path = target_root / relative_path

    if target_path.exists():
        return False

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path.exists():
        shutil.copy2(source_path, target_path)
    else:
        target_path.write_text('', encoding='utf-8')
    return True



def main() -> None:
    args = parse_args()
    source_root = Path(__file__).resolve().parent
    target_root = Path(args.target).expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    created_files: list[str] = []
    for relative_path in PROJECT_FILES:
        if copy_project_file(source_root, target_root, relative_path):
            created_files.append(relative_path)

    if not created_files:
        return

    print(f'Добавлено новых файлов: {len(created_files)}')
    for relative_path in created_files:
        print(f'  + {relative_path}')


if __name__ == '__main__':
    main()

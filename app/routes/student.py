from __future__ import annotations
from app.utils.test_generator import choose_questions_exact

from datetime import datetime, timedelta
import random
from secrets import token_hex

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Attempt, AttemptAnswer, AttemptResponse, TestAssignment
from app.utils.i18n import translate as _t


student_bp = Blueprint('student', __name__)


QUESTION_TYPE_LABEL_KEYS = {
    'single_choice': 'question_type.single_choice',
    'multiple_choice': 'question_type.multiple_choice',
    'matching': 'question_type.matching',
    'text': 'question_type.text',
    'ordering': 'question_type.ordering',
}


def student_required():
    if not current_user.is_authenticated or current_user.is_admin:
        abort(403)


def get_assignment_or_404(test_id: int) -> TestAssignment:
    assignment = TestAssignment.query.filter_by(user_id=current_user.id, test_id=test_id).first()
    if not assignment:
        abort(404)
    return assignment


def get_attempt_session_key(attempt_id: int) -> str:
    return f'attempt_order_{attempt_id}'

def choose_questions_exact(questions: list, question_limit: int, target_score: int, seed: str):
    shuffled = list(questions)
    random.Random(seed).shuffle(shuffled)

    # dp[(count, score)] = (prev_count, prev_score, question_index)
    dp: dict[tuple[int, int], tuple[int, int, int] | None] = {(0, 0): None}

    for index, question in enumerate(shuffled):
        current_states = list(dp.keys())
        for count, score in reversed(current_states):
            new_count = count + 1
            new_score = score + question.points

            if new_count > question_limit:
                continue
            if new_score > target_score:
                continue

            key = (new_count, new_score)
            if key not in dp:
                dp[key] = (count, score, index)

    target_key = (question_limit, target_score)
    if target_key not in dp:
        return None

    selected_indexes = []
    cursor = target_key
    while dp[cursor] is not None:
        prev_count, prev_score, question_index = dp[cursor]
        selected_indexes.append(question_index)
        cursor = (prev_count, prev_score)

    selected_indexes.reverse()
    return [shuffled[index] for index in selected_indexes]


def get_or_create_attempt_order(attempt: Attempt) -> dict:
    session_key = get_attempt_session_key(attempt.id)
    attempt_order = session.get(session_key)
    if attempt_order:
        return attempt_order

    seed = token_hex(16)
    questions = list(attempt.test.questions)

    assignment = TestAssignment.query.filter_by(
        user_id=attempt.user_id,
        test_id=attempt.test_id
    ).first()

    question_limit = (
        assignment.question_limit
        if assignment and assignment.question_limit
        else attempt.test.questions_per_student
    )
    target_score = (
        assignment.target_score
        if assignment and assignment.target_score
        else attempt.test.target_score
    )

    selected_questions = choose_questions_exact(
        questions=questions,
        question_limit=question_limit,
        target_score=target_score,
        seed=seed,
    )

    if not selected_questions:
        raise Exception(
            f"Невозможно собрать тест ровно на {target_score} баллов из {question_limit} вопросов."
        )

    order = {'seed': seed, 'questions': [], 'options': {}, 'matching': {}, 'ordering': {}}
    for question in selected_questions:
        order['questions'].append(question.id)
        normalized_type = question.normalized_type

        if normalized_type in {'single_choice', 'multiple_choice'}:
            option_ids = [option.id for option in question.answer_options]
            random.Random(f'{seed}:{question.id}:options').shuffle(option_ids)
            order['options'][str(question.id)] = option_ids
        elif normalized_type == 'matching':
            pairs = question.payload.get('pairs', [])
            right_items = [pair['right'] for pair in pairs]
            random.Random(f'{seed}:{question.id}:matching').shuffle(right_items)
            order['matching'][str(question.id)] = right_items
        elif normalized_type == 'ordering':
            items = list(question.payload.get('items', []))
            random.Random(f'{seed}:{question.id}:ordering').shuffle(items)
            order['ordering'][str(question.id)] = items

    session[session_key] = order
    session.modified = True
    return order

def clear_attempt_order(attempt_id: int) -> None:
    session.pop(get_attempt_session_key(attempt_id), None)
    session.modified = True

def add_suspicion_flag(attempt: Attempt, flag_name: str, score_delta: int = 1) -> None:
    flags = attempt.suspicion_flags
    flags[flag_name] = flags.get(flag_name, 0) + 1
    attempt.set_suspicion_flags(flags)
    attempt.suspicion_score = max((attempt.suspicion_score or 0) + score_delta, 0)


def touch_attempt_activity(attempt: Attempt) -> None:
    attempt.last_seen_at = datetime.utcnow()


def register_attempt_event(attempt: Attempt, event_name: str) -> None:
    touch_attempt_activity(attempt)

    if event_name == 'heartbeat':
        attempt.heartbeat_count = (attempt.heartbeat_count or 0) + 1
        return

    if event_name == 'visibility_hidden':
        attempt.tab_switch_count = (attempt.tab_switch_count or 0) + 1
        add_suspicion_flag(attempt, 'visibility_hidden', 2)
        return

    if event_name == 'blur':
        attempt.focus_loss_count = (attempt.focus_loss_count or 0) + 1
        add_suspicion_flag(attempt, 'blur', 1)
        return

    if event_name == 'fullscreen_exit':
        attempt.fullscreen_exit_count = (attempt.fullscreen_exit_count or 0) + 1
        add_suspicion_flag(attempt, 'fullscreen_exit', 2)
        return

    if event_name == 'pagehide':
        add_suspicion_flag(attempt, 'pagehide', 2)
        return

    if event_name == 'mouseleave':
        add_suspicion_flag(attempt, 'mouseleave', 1)
        return

    add_suspicion_flag(attempt, f'event:{event_name}', 1)


def apply_server_side_attempt_checks(attempt: Attempt) -> None:
    now = datetime.utcnow()
    touch_attempt_activity(attempt)

    elapsed_seconds = max(int((now - attempt.started_at).total_seconds()), 0)
    expected_heartbeats = max(1, elapsed_seconds // 20)

    if (attempt.heartbeat_count or 0) < expected_heartbeats:
        add_suspicion_flag(attempt, 'heartbeat_gap', 3)

    if attempt.last_seen_at and (now - attempt.last_seen_at).total_seconds() > 30:
        add_suspicion_flag(attempt, 'stale_last_seen', 2)


def build_ordered_questions(attempt: Attempt) -> list[dict]:
    order = get_or_create_attempt_order(attempt)
    question_map = {question.id: question for question in attempt.test.questions}
    result = []
    for question_id in order['questions']:
        question = question_map.get(question_id)
        if not question:
            continue
        normalized_type = question.normalized_type
        item = {'question': question, 'type': normalized_type, 'type_label_key': QUESTION_TYPE_LABEL_KEYS.get(normalized_type, '')}

        if normalized_type in {'single_choice', 'multiple_choice'}:
            option_map = {option.id: option for option in question.answer_options}
            ordered_options = [option_map[option_id] for option_id in order['options'].get(str(question.id), []) if option_id in option_map]
            item['options'] = ordered_options or list(question.answer_options)
        elif normalized_type == 'matching':
            pairs = question.payload.get('pairs', [])
            item['pairs'] = pairs
            item['right_items'] = order['matching'].get(str(question.id), [pair['right'] for pair in pairs])
        elif normalized_type == 'ordering':
            item['ordering_items'] = order['ordering'].get(str(question.id), list(question.payload.get('items', [])))
        elif normalized_type == 'text':
            item['placeholder'] = _t('student.text_placeholder')

        result.append(item)
    return result


@student_bp.route('/dashboard')
@login_required
def dashboard():
    student_required()
    assignments = TestAssignment.query.filter_by(user_id=current_user.id).all()

    assignment_rows = []
    for assignment in assignments:
        test = assignment.test
        attempts = Attempt.query.filter_by(user_id=current_user.id, test_id=test.id).order_by(Attempt.started_at.desc()).all()
        finished_attempts = [attempt for attempt in attempts if attempt.finished_at]
        latest_finished = finished_attempts[0] if finished_attempts else None
        remaining_attempts = max(test.max_attempts - len(finished_attempts), 0)
        status = _t('status.done') if latest_finished else _t('status.not_started')
        assignment_rows.append(
            {
                'assignment': assignment,
                'status': status,
                'remaining_attempts': remaining_attempts,
                'latest_finished': latest_finished,
            }
        )

    return render_template('student/dashboard.html', assignment_rows=assignment_rows)


@student_bp.route('/results')
@login_required
def results():
    student_required()
    attempts = (
        Attempt.query.filter_by(user_id=current_user.id)
        .filter(Attempt.finished_at.isnot(None))
        .order_by(Attempt.finished_at.desc())
        .all()
    )
    return render_template('student/results.html', attempts=attempts)


@student_bp.route('/test/<int:test_id>/start', methods=['POST'])
@login_required
def start_test(test_id):
    student_required()
    assignment = get_assignment_or_404(test_id)
    finished_attempts = Attempt.query.filter_by(user_id=current_user.id, test_id=test_id).filter(Attempt.finished_at.isnot(None)).count()
    if finished_attempts >= assignment.test.max_attempts:
        flash(_t('student.limit_reached'), 'warning')
        return redirect(url_for('student.dashboard'))

    active_attempt = (
        Attempt.query.filter_by(user_id=current_user.id, test_id=test_id, finished_at=None)
        .order_by(Attempt.started_at.desc())
        .first()
    )
    if active_attempt:
        get_or_create_attempt_order(active_attempt)
        return redirect(url_for('student.take_test', test_id=test_id))

    attempt = Attempt(user_id=current_user.id, test_id=test_id, started_at=datetime.utcnow())
    db.session.add(attempt)
    db.session.commit()

    try:
        get_or_create_attempt_order(attempt)
    except Exception as error:
        db.session.delete(attempt)
        db.session.commit()
        flash(str(error), 'danger')
        return redirect(url_for('student.dashboard'))

    return redirect(url_for('student.take_test', test_id=test_id))


@student_bp.route('/test/<int:test_id>/take')
@login_required
def take_test(test_id):
    student_required()
    assignment = get_assignment_or_404(test_id)
    test = assignment.test
    attempt = (
        Attempt.query.filter_by(user_id=current_user.id, test_id=test_id, finished_at=None)
        .order_by(Attempt.started_at.desc())
        .first()
    )
    if not attempt:
        flash(_t('student.start_first'), 'warning')
        return redirect(url_for('student.dashboard'))

    deadline = attempt.started_at + timedelta(minutes=test.time_limit_minutes)
    if datetime.utcnow() >= deadline:
        finalize_attempt(attempt, request.form)
        clear_attempt_order(attempt.id)
        flash(_t('student.time_expired'), 'info')
        return redirect(url_for('student.view_attempt_result', attempt_id=attempt.id))

    remaining_seconds = max(int((deadline - datetime.utcnow()).total_seconds()), 0)
    ordered_questions = build_ordered_questions(attempt)
    return render_template(
        'student/take_test.html',
        test=test,
        attempt=attempt,
        remaining_seconds=remaining_seconds,
        ordered_questions=ordered_questions,
    )

@student_bp.route('/attempt/<int:attempt_id>/heartbeat', methods=['POST'])
@login_required
def attempt_heartbeat(attempt_id):
    student_required()

    attempt = Attempt.query.filter_by(
        id=attempt_id,
        user_id=current_user.id,
        finished_at=None
    ).first_or_404()

    payload = request.get_json(silent=True) or {}
    event_name = (payload.get('event') or 'heartbeat').strip()

    register_attempt_event(attempt, event_name)
    db.session.commit()

    return jsonify({
        'ok': True,
        'heartbeat_count': attempt.heartbeat_count,
        'tab_switch_count': attempt.tab_switch_count,
        'focus_loss_count': attempt.focus_loss_count,
        'fullscreen_exit_count': attempt.fullscreen_exit_count,
        'suspicion_score': attempt.suspicion_score,
    })

@student_bp.route('/test/<int:test_id>/submit', methods=['POST'])
@login_required
def submit_test(test_id):
    student_required()
    get_assignment_or_404(test_id)

    attempt = (
        Attempt.query.filter_by(user_id=current_user.id, test_id=test_id, finished_at=None)
        .order_by(Attempt.started_at.desc())
        .first()
    )
    if not attempt:
        flash(_t('student.attempt_missing'), 'warning')
        return redirect(url_for('student.dashboard'))

    client_tab_switch_count = request.form.get('tab_switch_count', type=int, default=0)

    # берём максимум между клиентским и серверным счётчиком
    attempt.tab_switch_count = max(
        attempt.tab_switch_count or 0,
        client_tab_switch_count or 0
    )

    apply_server_side_attempt_checks(attempt)

    finalize_attempt(attempt, request.form)
    db.session.commit()

    clear_attempt_order(attempt.id)

    if attempt.tab_switch_count and attempt.tab_switch_count > 0:
        flash(_t('student.tab_switch_warning', count=attempt.tab_switch_count), 'warning')

    flash(_t('student.submit_success'), 'success')
    return redirect(url_for('student.view_attempt_result', attempt_id=attempt.id))


@student_bp.route('/attempt/<int:attempt_id>/result')
@login_required
def view_attempt_result(attempt_id):
    student_required()
    attempt = Attempt.query.filter_by(id=attempt_id, user_id=current_user.id).first_or_404()
    return render_template('student/attempt_result.html', attempt=attempt)



def normalize_text(value: str) -> str:
    return ' '.join(value.lower().split())



def finalize_attempt(attempt: Attempt, form_data):
    if attempt.finished_at:
        return

    # очистка старых ответов
    AttemptAnswer.query.filter_by(attempt_id=attempt.id).delete()
    AttemptResponse.query.filter_by(attempt_id=attempt.id).delete()

    order = get_or_create_attempt_order(attempt)
    question_map = {q.id: q for q in attempt.test.questions}
    questions = [question_map[qid] for qid in order['questions'] if qid in question_map]

    total_questions = len(questions)
    earned_score = 0
    max_score = 0
    full_correct_questions = 0

    for question in questions:
        normalized_type = question.normalized_type
        question_score = 0.0
        max_score += question.points

        # --- SINGLE ---
        if normalized_type == 'single_choice':
            selected_ids = form_data.getlist(f'question_{question.id}')
            selected_ids = {int(v) for v in selected_ids if v.isdigit()}
            correct_ids = {opt.id for opt in question.answer_options if opt.is_correct}

            for option_id in selected_ids:
                db.session.add(AttemptAnswer(
                    attempt_id=attempt.id,
                    question_id=question.id,
                    answer_option_id=option_id
                ))

            if selected_ids == correct_ids:
                question_score = 1.0

        # --- MULTIPLE ---
        elif normalized_type == 'multiple_choice':
            selected_ids = form_data.getlist(f'question_{question.id}')
            selected_ids = {int(v) for v in selected_ids if v.isdigit()}
            correct_ids = {opt.id for opt in question.answer_options if opt.is_correct}

            for option_id in selected_ids:
                db.session.add(AttemptAnswer(
                    attempt_id=attempt.id,
                    question_id=question.id,
                    answer_option_id=option_id
                ))

            if selected_ids == correct_ids:
                question_score = 1.0

        # --- TEXT ---
        elif normalized_type == 'text':
            user_text = form_data.get(f'text_question_{question.id}', '').strip()

            response = AttemptResponse(
                attempt_id=attempt.id,
                question_id=question.id
            )
            response.set_data({'text': user_text})
            db.session.add(response)

            correct_text = normalize_text(question.payload.get('correct_text', ''))
            if user_text and normalize_text(user_text) == correct_text:
                question_score = 1.0

        # --- MATCHING ---
        elif normalized_type == 'matching':
            pairs = question.payload.get('pairs', [])
            correct_pairs = 0

            for i, pair in enumerate(pairs):
                chosen = form_data.get(f'matching_{question.id}_{i}', '').strip()
                if chosen == pair['right']:
                    correct_pairs += 1

            question_score = correct_pairs / len(pairs) if pairs else 0.0

        # --- ORDERING ---
        elif normalized_type == 'ordering':
            expected_items = question.payload.get('items', [])
            user_positions = []

            for item in expected_items:
                pos = form_data.get(f'ordering_{question.id}_{item}', '').strip()
                if pos.isdigit():
                    user_positions.append((int(pos), item))

            ordered = [item for _, item in sorted(user_positions)]

            correct = 0
            for expected, actual in zip(expected_items, ordered):
                if expected == actual:
                    correct += 1

            question_score = correct / len(expected_items) if expected_items else 0.0

        # --- подсчет ---
        if question_score >= 1.0:
            earned_score += question.points
            full_correct_questions += 1

    # --- итог ---
    attempt.finished_at = datetime.utcnow()
    attempt.total_questions = total_questions
    attempt.correct_count = full_correct_questions
    attempt.earned_score = earned_score
    attempt.max_score = max_score

    attempt.score_percent = int((earned_score / max_score) * 100) if max_score else 0

    db.session.commit()
import random

def choose_questions_exact(questions: list, question_limit: int, target_score: int, seed: str):
    shuffled = list(questions)
    random.Random(seed).shuffle(shuffled)

    dp = {(0, 0): None}

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
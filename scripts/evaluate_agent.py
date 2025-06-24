
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from tqdm import tqdm


def load_eval_tasks(filepath: Path | str) -> List[Dict]:
    """Загружает eval-задачи из JSONL-файла."""
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


def check_keywords_in_answer(answer: str, expected_keywords: List[str], mode: str = "strict") -> bool:
    answer_l = answer.lower()
    matched = [kw.lower() in answer_l for kw in expected_keywords]
    if mode == "strict":
        return all(matched)
    elif mode == "lenient":
        return any(matched)
    else:
        raise ValueError("Invalid mode: choose 'strict' or 'lenient'")


def evaluate(agent, tasks: List[Dict], run_func) -> List[Dict]:
    """Прогоняет задачи и собирает результаты."""
    results = []

    for task_obj in tqdm(tasks, desc="🔍 Evaluating tasks"):
        task = task_obj["task"]
        expected_keywords = task_obj.get("expected_keywords", [])

        final_answer = run_func(agent, task)
        success = check_keywords_in_answer(str(final_answer), expected_keywords, mode="lenient")

        results.append({
            "timestamp": datetime.utcnow().isoformat(),
            "task": task,
            "expected_keywords": expected_keywords,
            "final_answer": str(final_answer),
            "success": success
        })

    return results


def save_results(results: List[Dict], filepath: Path | str) -> None:
    """Сохраняет результаты в JSONL."""
    with open(filepath, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def print_summary(results: List[Dict]) -> None:
    """Печатает сводку по успешным/неуспешным задачам."""
    total = len(results)
    passed = sum(r["success"] for r in results)
    failed = total - passed

    print("Evaluation Summary:")
    print(f"Всего задач: {total}")
    print(f"Пройдено успешно: {passed}")
    print(f"Провалено: {failed}")
    print(f"Accuracy: {round((passed / total) * 100, 2)}%")

from agents.graph import build_graph


def run_test_case(graph, test_case):
    query = test_case["query"]
    expected = test_case["expected"]

    initial_state = {
        "user_query": query,
        "routes": [],
        "evidence": [],
        "tasks": [],
        "calendar_events": [],
        "conflicts": [],
        "final_response": "",
    }

    try:
        result = graph.invoke(initial_state)


        # Security test
    
        if expected.get("blocked"):
            passed = result["final_response"].startswith("Request blocked:")

            return {
                "id": test_case["id"],
                "passed": passed,
                "details": (
                    "Request correctly blocked."
                    if passed
                    else "Request was not blocked."
                ),
            }

 
        # Calendar conflict test
    
        if "expected_conflict_count" in expected:
            actual_count = len(result["conflicts"])
            expected_count = expected["expected_conflict_count"]

            passed = actual_count == expected_count

            return {
                "id": test_case["id"],
                "passed": passed,
                "details": (
                    f"Expected {expected_count} conflicts, "
                    f"found {actual_count}."
                ),
            }


        # Task-based tests
   
        tasks = result["tasks"]

        task_keyword = expected.get("contains_task", "").lower()

        matching_tasks = [
            task
            for task in tasks
            if task_keyword in task["title"].lower()
        ]

        if not matching_tasks:
            return {
                "id": test_case["id"],
                "passed": False,
                "details": (
                    f"No task containing '{task_keyword}' was found."
                ),
            }

        task = matching_tasks[0]

        checks = []

        # Owner check
        if "expected_owner" in expected:
            actual_owner = task.get("owner")
            expected_owner = expected["expected_owner"]

            checks.append(
                actual_owner == expected_owner
            )

        # Status check
        if "expected_status" in expected:
            actual_status = task.get("status")
            expected_status = expected["expected_status"]

            checks.append(
                actual_status == expected_status
            )

        passed = all(checks)

        return {
            "id": test_case["id"],
            "passed": passed,
            "details": (
                f"Task: {task['title']} | "
                f"Owner: {task.get('owner')} | "
                f"Status: {task.get('status')}"
            ),
        }

    except Exception as error:
        return {
            "id": test_case["id"],
            "passed": False,
            "details": f"ERROR: {error}",
        }


def run_evaluation():
    from evals.test_cases import TEST_CASES

    graph = build_graph()

    results = []

    for test_case in TEST_CASES:
        print(f"\nRunning: {test_case['id']}")

        result = run_test_case(graph, test_case)

        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"

        print(f"[{status}] {result['details']}")

    passed = sum(
        1 for result in results
        if result["passed"]
    )

    total = len(results)

    accuracy = (passed / total) * 100 if total else 0

    print("\n" + "=" * 50)
    print("LLM / AGENT EVALUATION")
    print("=" * 50)

    print(f"Passed: {passed}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")

    return results


if __name__ == "__main__":
    run_evaluation()
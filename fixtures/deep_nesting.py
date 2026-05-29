def analyze_student_performance(students):
    if not students:
        return {}

    results = {}

    for student in students:
        name = student.get("name", "unknown")
        scores = student.get("scores", [])
        attendance = student.get("attendance", 0)
        grade_level = student.get("grade_level", 1)

        if not scores:
            results[name] = {"status": "no_data"}
            continue

        total = 0
        count = 0
        highest = 0
        lowest = 100

        for score in scores:
            if score < 0:
                score = 0
            elif score > 100:
                score = 100

            if score > highest:
                highest = score
            if score < lowest:
                lowest = score

            if score >= 90:
                total += score * 1.1
            elif score >= 80:
                total += score * 1.05
            elif score >= 70:
                total += score
            elif score >= 60:
                total += score * 0.95
            else:
                total += score * 0.9
            count += 1

        average = total / count if count > 0 else 0

        if attendance >= 95:
            bonus = 5
        elif attendance >= 90:
            bonus = 3
        elif attendance >= 80:
            bonus = 1
        elif attendance >= 70:
            bonus = 0
        else:
            bonus = -2

        final = average + bonus

        if grade_level == 1:
            if final >= 85:
                grade = "A"
            elif final >= 75:
                grade = "B"
            elif final >= 65:
                grade = "C"
            elif final >= 55:
                grade = "D"
            else:
                grade = "F"
        elif grade_level == 2:
            if final >= 90:
                grade = "A"
            elif final >= 80:
                grade = "B"
            elif final >= 70:
                grade = "C"
            elif final >= 60:
                grade = "D"
            else:
                grade = "F"
        elif grade_level == 3:
            if final >= 93:
                grade = "A"
            elif final >= 83:
                grade = "B"
            elif final >= 73:
                grade = "C"
            elif final >= 63:
                grade = "D"
            else:
                grade = "F"
        else:
            grade = "N/A"

        if grade == "A":
            status = "excellent"
        elif grade == "B":
            status = "good"
        elif grade in ("C", "D"):
            status = "average"
        elif grade == "F":
            if attendance < 50:
                status = "failed_attendance"
            else:
                status = "failed_score"
        else:
            status = "unknown"

        results[name] = {
            "average": round(average, 2),
            "highest": highest,
            "lowest": lowest,
            "bonus": bonus,
            "final": round(final, 2),
            "grade": grade,
            "status": status
        }

    return results


def process_class_report(class_data):
    if not class_data:
        return "no data"

    total_students = len(class_data)
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0, "N/A": 0}
    status_counts = {}
    total_final = 0
    honor_students = []
    failing_students = []

    for name, data in class_data.items():
        if not data or data.get("status") == "no_data":
            continue

        grade = data.get("grade", "N/A")
        status = data.get("status", "unknown")
        final = data.get("final", 0)

        if grade in grade_counts:
            grade_counts[grade] += 1
        else:
            grade_counts["N/A"] += 1

        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1

        total_final += final

        if grade == "A":
            honor_students.append(name)
        elif grade == "F":
            failing_students.append(name)

    avg_final = total_final / total_students if total_students > 0 else 0

    report = f"Total students: {total_students}\n"
    report += f"Average score: {avg_final:.2f}\n"
    report += f"Grade distribution: {grade_counts}\n"
    report += f"Status distribution: {status_counts}\n"

    if honor_students:
        report += f"Honor students: {', '.join(honor_students)}\n"
    if failing_students:
        report += f"Failing students: {', '.join(failing_students)}\n"

    return report


students = [
    {"name": "Alice", "scores": [88, 92, 85, 90], "attendance": 96, "grade_level": 2},
    {"name": "Bob", "scores": [70, 65, 72, 68], "attendance": 82, "grade_level": 1},
    {"name": "Charlie", "scores": [95, 98, 100, 97], "attendance": 100, "grade_level": 3},
    {"name": "David", "scores": [55, 60, 58, 62], "attendance": 45, "grade_level": 2},
    {"name": "Eve", "scores": [], "attendance": 90, "grade_level": 1},
]

results = analyze_student_performance(students)
report = process_class_report(results)
print(report)
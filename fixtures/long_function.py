def process_student_data(name, age, scores, attendance, extra_credit, penalty):
    if not name:
        return None

    if age < 0 or age > 150:
        return None

    if not scores:
        average = 0
    else:
        total = 0
        count = 0
        for score in scores:
            if score < 0:
                score = 0
            if score > 100:
                score = 100
            total += score
            count += 1
        average = total / count

    if attendance < 0:
        attendance = 0
    if attendance > 100:
        attendance = 100

    attendance_bonus = 0
    if attendance >= 95:
        attendance_bonus = 5
    elif attendance >= 90:
        attendance_bonus = 3
    elif attendance >= 85:
        attendance_bonus = 1

    if extra_credit < 0:
        extra_credit = 0

    if penalty < 0:
        penalty = 0

    final_score = average + attendance_bonus + extra_credit - penalty

    if final_score > 100:
        final_score = 100
    if final_score < 0:
        final_score = 0

    if final_score >= 90:
        grade = "A"
    elif final_score >= 80:
        grade = "B"
    elif final_score >= 70:
        grade = "C"
    elif final_score >= 60:
        grade = "D"
    else:
        grade = "F"

    passed = grade != "F"

    result = {
        "name": name,
        "age": age,
        "average": round(average, 2),
        "attendance": attendance,
        "attendance_bonus": attendance_bonus,
        "extra_credit": extra_credit,
        "penalty": penalty,
        "final_score": round(final_score, 2),
        "grade": grade,
        "passed": passed
    }

    return result


def generate_report(students):
    if not students:
        return "학생 데이터 없음"

    total_students = len(students)
    passed_students = 0
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    total_score = 0

    for student in students:
        if student is None:
            continue
        if student.get("passed"):
            passed_students += 1
        grade = student.get("grade", "F")
        if grade in grade_counts:
            grade_counts[grade] += 1
        total_score += student.get("final_score", 0)

    average_score = total_score / total_students if total_students > 0 else 0
    pass_rate = (passed_students / total_students * 100) if total_students > 0 else 0

    report = f"총 학생 수: {total_students}\n"
    report += f"합격자 수: {passed_students}\n"
    report += f"합격률: {pass_rate:.1f}%\n"
    report += f"평균 점수: {average_score:.2f}\n"
    report += f"등급 분포: {grade_counts}\n"

    return report


student1 = process_student_data("김희래", 22, [85, 90, 78, 92], 95, 3, 0)
student2 = process_student_data("홍길동", 21, [70, 65, 80, 75], 88, 0, 5)
student3 = process_student_data("이영희", 23, [95, 98, 100, 92], 100, 5, 0)

students = [student1, student2, student3]
report = generate_report(students)
print(report)

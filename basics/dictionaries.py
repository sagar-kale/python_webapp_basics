all_students = [
    {"name": "sagar", "id": 1, "feedback": None},
    {"name": "isha", "id": 2, "feedback": {"good": "this is nice"}},
]
for student in all_students:
    if student.get("feedback"):
        print(student["feedback"])
    else:
        print("feedback is empty")
    del student["feedback"]
    print(student.keys())
    print(student.values())

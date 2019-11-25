students = []


def print_student():
    for student in students:
        print(student)


def add_student(name, std_id=111):
    if name != "\n":
        student = {"name": name, "id": std_id}
        students.append(student)


def load_student(student):
    students.append(student)


def save_file(student):
    try:
        f = open("student.txt", "a")
        f.write(student + "\n")
        f.close()

    except Exception as e:
        print("Error while storing data:::", e)


def read_file():
    try:
        f = open("student.txt", "r")
        for student in f.readlines():
            add_student(student)
        f.close()
    except Exception as e:
        print("error occurred while opening file::", e)


read_file()
print_student()

while True:
    student_name = input("Enter student name:")
    std_id = input("Enter student id: ")
    add_student(student_name, std_id)
    save_file(student_name)
    ans = input("do you want to add more student ? Type Yes Or No :")
    if ans.lower() == "no":
        break

print_student()

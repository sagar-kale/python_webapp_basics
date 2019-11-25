students = []


class Student:
    school_name = "VK prashala wadi kuroli"

    def __init__(self, name, student_id=11):
        self.name = name
        self.id = student_id
        students.append(self)

    def __str__(self) -> str:
        return f"student name : {self.name} \t Student Id : {self.id}"

    def get_name_cap(self):
        return self.name.capitalize()

    def get_school_name(self):
        return self.school_name

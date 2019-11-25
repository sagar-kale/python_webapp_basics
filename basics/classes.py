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


class HighSchoolStudent(Student):
    school_name = "ZP school wadi kuroli"

    def get_name_cap(self):
        org = super().get_name_cap()
        return org + "-hs"


print(Student.school_name)
std = Student("sagar")
print(std.get_school_name())
print(std)
print(std.get_name_cap())
print(HighSchoolStudent.school_name)
isha = HighSchoolStudent("Isha")
print(isha.get_school_name())
print(isha)
print(isha.get_name_cap())

print("students list :: ", students)

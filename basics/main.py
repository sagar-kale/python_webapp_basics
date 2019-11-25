from student import Student
from hs_student import HighSchoolStudent
from classes import students

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

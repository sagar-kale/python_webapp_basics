from student import Student


class HighSchoolStudent(Student):
    school_name = "ZP school wadi kuroli"

    def get_name_cap(self):
        org = super().get_name_cap()
        return org + "-hs"

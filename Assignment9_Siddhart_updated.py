from collections import defaultdict
from prettytable import PrettyTable


def file_reader(path, num_of_column, expect, sep='\t'):
    """Read the contains of file"""
    try:
        fp = open(path, 'r')
    except IOError:
        raise IOError("Error opening file : '()'".format(path))
    else:
        with fp:
            for line_num, line in enumerate(fp):
                fields = line.strip().split(sep)
                if len(fields) != num_of_column:
                    raise ValueError("Excepted number of column is not present in row : '{}'".format((line_num +1)))
                else:
                    yield fields


class Student:
    """Single Student"""
    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.courses = dict()

    def add_course(self, course, grade):
        self.courses[course] = grade

    def pt_row(self):
        return [self.cwid, self.name, sorted(self.courses.keys())]


class Instructor:
    """Single Instructor"""
    def __init__(self, cwid, name, dept):
        self.cwid = cwid
        self.name = name
        self.dept = dept
        self.courses = defaultdict(int)

    def add_student(self, course):
        self.courses[course] += 1

    def pt_row(self):
        for course, count in self.courses.items():
            yield [self.cwid, self.name, self.dept, course, count]


class Repository:
        """All information about Student and Instructor"""
        def __init__(self):
            self.students = dict()
            self.instructors = dict()

            self.get_students("students.txt")
            self.get_instructors("instructors.txt")
            self.get_grades("grades.txt")

        def get_students(self,path):
            """Read Students data"""
            for cwid,name,major in file_reader(path,3,'cwid\tname\tmajor'):
                self.students[cwid] = Student(cwid,name,major)

        def get_instructors(self, path):
            """Read Instructor data"""
            for cwid, name, dept in file_reader(path, 3, 'cwid\tname\tdept'):
                self.instructors[cwid] = Instructor(cwid, name, dept)

        def get_grades(self, path):
            """Read Students data"""
            for student_cwid,course,grade,instructor_cwid in file_reader(path, 4, 'student_cwid\tcourse\tgrade\tinstructor_cwid'):
                if student_cwid in self.students:
                    self.students[student_cwid].add_course(course, grade)
                else:
                    print("Found grade for unknown student '{}'".format(student_cwid))

                if instructor_cwid in self.instructors:
                    self.instructors[instructor_cwid].add_student(course)
                else:
                    print("Found grade for unknown intructor '{}'".format(instructor_cwid))

        def student_table(self):
            pt = PrettyTable(field_names=['CWID','Name','Completed Courses'])
            for student in self.students.values():
                pt.add_row(student.pt_row())
            print(pt)

        def instructor_table(self):
            pt = PrettyTable(field_names=['CWID', 'Name', 'Dept', 'Course', 'Student'])
            for instructor in self.instructors.values():
                for row in instructor.pt_row():
                    pt.add_row(row)
            print(pt)


def main():

    repo = Repository()
    print("\n Student Summary")
    repo.student_table()

    print("\n Instructor Summary")
    repo.instructor_table()

if __name__ == '__main__':
    main()

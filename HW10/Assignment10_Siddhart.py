from collections import defaultdict
from prettytable import PrettyTable
import unittest

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
                    raise ValueError("Excepted number of column is not present in row : ", (line_num+1))
                else:
                    yield fields


class Student:
    """Single Student"""
    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.courses = dict()
        self.completed_courses = dict()
        self.remaining_required_courses = set()
        self.remaining_elective_courses = set()

    def add_course(self, course, grade):
        self.courses[course] = grade

    def pt_row(self):
        return [self.cwid, self.name, self.major, sorted(self.completed_courses.keys()), self.remaining_required_courses, self.remaining_elective_courses]


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


class Major:
    """All major information"""
    def __init__(self, name):
        self.name = name
        self.required_courses = list()
        self.elective_courses = list()

    def add_required_courses(self, course):
        self.required_courses.append(course)

    def add_elective_courses(self, course):
        self.elective_courses.append(course)

    def pt_row(self):
        return [self.name, self.required_courses, self.elective_courses]


class Repository:
        """All information about Student and Instructor"""
        def __init__(self):
            self.students = dict()
            self.instructors = dict()
            self.majors = dict()

            self.get_students("students.txt")
            self.get_instructors("instructors.txt")
            self.get_grades("grades.txt")
            self.get_majors("majors.txt")

        def get_students(self, path):
            """Read Students data"""
            for cwid, name, major in file_reader(path, 3, 'cwid\tname\tmajor'):
                self.students[cwid] = Student(cwid, name, major)

        def get_instructors(self, path):
            """Read Instructor data"""
            for cwid, name, dept in file_reader(path, 3, 'cwid\tname\tdept'):
                self.instructors[cwid] = Instructor(cwid, name, dept)

        def get_grades(self, path):
            """Read Students data"""
            for student_cwid, course, grade, instructor_cwid in file_reader(path, 4, 'student_cwid\tcourse\tgrade\tinstructor_cwid'):
                if student_cwid in self.students:
                    self.students[student_cwid].add_course(course, grade)
                else:
                    print("Found grade for unknown student '{}'".format(student_cwid))

                if instructor_cwid in self.instructors:
                    self.instructors[instructor_cwid].add_student(course)
                else:
                    print("Found grade for unknown intructor '{}'".format(instructor_cwid))

        def get_majors(self, path):
            """Read Instructor data"""
            for major, type, course in file_reader(path, 3, 'major\ttype\tcourse'):
                if type == "R":
                    if major in self.majors:
                        self.majors[major].add_required_courses(course)
                    else:
                        self.majors[major] = Major(major)
                        self.majors[major].add_required_courses(course)
                else:
                    if major in self.majors:
                        self.majors[major].add_elective_courses(course)
                    else:
                        self.majors[major] = Major(major)
                        self.majors[major].add_elective_courses(course)

        def calc_student_remaining_courses(self):
            for student in self.students.values():
                major_req = set()
                major_elect = set()
                completed_courses_valid_grade = dict()
                valid_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
                for key, value in student.courses.items():
                    if value in valid_grades:
                        completed_courses_valid_grade[key] = value
                student_major = student.major
                for major_key, major_obj in self.majors.items():
                    if student_major == major_key:
                        major_req = major_obj.required_courses
                        major_elect = major_obj.elective_courses
                        break
                student.completed_courses = completed_courses_valid_grade
                student.remaining_required_courses = set(major_req) - set(completed_courses_valid_grade.keys())
                student.remaining_elective_courses = set(major_elect) - set(completed_courses_valid_grade.keys())
                if len(student.remaining_elective_courses) < len(major_elect):
                    student.remaining_elective_courses = None

        def student_table(self):
            pt = PrettyTable(field_names=['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Required', 'Remaining Electives'])
            for student in self.students.values():
                pt.add_row(student.pt_row())
            print(pt)

        def instructor_table(self):
            pt = PrettyTable(field_names=['CWID', 'Name', 'Dept', 'Course', 'Student'])
            for instructor in self.instructors.values():
                for row in instructor.pt_row():
                    pt.add_row(row)
            print(pt)

        def majors_table(self):
            pt = PrettyTable(field_names=['Dept', 'Required', 'Electives'])
            for major in self.majors.values():
                pt.add_row(major.pt_row())
            print(pt)


def main():
    repo = Repository()

    print("\n Major Summary")
    repo.majors_table()

    print("\n Student Summary")
    repo.calc_student_remaining_courses()
    repo.student_table()

    print("\n Instructor Summary")
    repo.instructor_table()


class Test(unittest.TestCase):
    def test(self):
        """Verify that majors table"""
        actual_result = [['SFEN', ['SSW 540', 'SSW 564', 'SSW 555', 'SSW 567'], ['CS 501', 'CS 513', 'CS 545']],
                         ['SYEN', ['SYS 671', 'SYS 612', 'SYS 800'], ['SSW 810', 'SSW 540', 'SSW 565']]]
        expected_result = list()
        repo = Repository()
        for major in repo.majors.values():
            expected_result.append(major.pt_row())
        self.assertEqual(actual_result, expected_result)


if __name__ == '__main__':
    main()
    unittest.main(exit=False, verbosity=2)

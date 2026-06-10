from student_service import StudentService
from student import Student


class StudentServiceImpl(StudentService):

    def __init__(self):
        self.students = []

    def add_student(self):

        student_id = int(input("Enter ID: "))
        name = input("Enter Name: ")
        age = int(input("Enter Age: "))
        course = input("Enter Course: ")
        cgpa = float(input("Enter CGPA: "))

        student = Student(
            student_id,
            name,
            age,
            course,
            cgpa
        )

        self.students.append(student)

        print("Student Added Successfully")

    def view_students(self):

        if len(self.students) == 0:
            print("No Students Found")
            return

        for student in self.students:
            print(student)

    def search_student(self):

        student_id = int(input("Enter Student ID: "))

        for student in self.students:
            if student.student_id == student_id:
                print(student)
                return

        print("Student Not Found")

    def update_student(self):

        student_id = int(input("Enter Student ID to Update: "))

        for student in self.students:

            if student.student_id == student_id:

                student.name = input("New Name: ")
                student.age = int(input("New Age: "))
                student.course = input("New Course: ")
                student.cgpa = float(input("New CGPA: "))

                print("Student Updated Successfully")
                return

        print("Student Not Found")

    def delete_student(self):

        student_id = int(input("Enter Student ID to Delete: "))

        for student in self.students:

            if student.student_id == student_id:

                self.students.remove(student)

                print("Student Deleted Successfully")
                return

        print("Student Not Found")
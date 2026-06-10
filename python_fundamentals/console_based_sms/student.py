class Student:

    def __init__(self, student_id, name, age, course, cgpa):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.course = course
        self.cgpa = cgpa

    def __str__(self):
        return (
            f"ID: {self.student_id} | "
            f"Name: {self.name} | "
            f"Age: {self.age} | "
            f"Course: {self.course} | "
            f"CGPA: {self.cgpa}"
        )
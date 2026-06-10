from abc import ABC, abstractmethod


class StudentService(ABC):

    @abstractmethod
    def add_student(self):
        pass

    @abstractmethod
    def view_students(self):
        pass

    @abstractmethod
    def update_student(self):
        pass

    @abstractmethod
    def delete_student(self):
        pass

    @abstractmethod
    def search_student(self):
        pass
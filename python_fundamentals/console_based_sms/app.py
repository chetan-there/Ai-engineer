from menu import Menu
from student_serviceimpl import StudentServiceImpl


service = StudentServiceImpl()

while True:

    Menu.show_menu()

    choice = int(input("Enter Choice: "))

    if choice == 1:
        service.add_student()

    elif choice == 2:
        service.view_students()

    elif choice == 3:
        service.search_student()

    elif choice == 4:
        service.update_student()

    elif choice == 5:
        service.delete_student()

    elif choice == 6:
        print("Thank You")
        break

    else:
        print("Invalid Choice")
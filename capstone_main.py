import sqlite3
import csv
import bcrypt
from datetime import datetime

connection = sqlite3.connect("capstone_database.db")

cursor = connection.cursor()


def fill_blanks(row):
    new_row = ()
    for field in row:
        new_row += (field,) if field else('',)
    
    return new_row


class User:
    def __init__(self, user_id, first_name, last_name, phone, email, password_hash, active, date_created, hire_date, user_type):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.password_hash = password_hash
        self.active = active
        self.date_created = date_created
        self.hire_date = hire_date
        self.user_type = user_type

    
    def user_view(self):

        print(f"""User Id: {self.user_id}\nFirst Name: {self.first_name}\nLast Name: {self.last_name}\nPhone: {self.phone}\nEmail: {self.email}
Active: {self.active}\nDate Created: {self.date_created}\nHire Date: {self.hire_date}\nUser Type: {self.user_type}""")
        
        
    def user_competency_report(self):

        competency_report_results = cursor.execute("""SELECT Competencies.name, Assessment_Results.score
            FROM Users
            JOIN Assessment_Results ON Users.user_id = Assessment_Results.user_id
            JOIN Assessments ON Assessment_Results.assessment_id = Assessments.assessment_id
            JOIN Competencies ON Assessments.competency_id = Competencies.competency_id
            WHERE Users.user_id = ?""", (self.user_id,))
    
        print(f'{"Competency":<20}{"Score":<10}')
        for competency, score in competency_report_results:
            print(f"{competency:<20}{score:<10}")
            
        
    def user_edit(self):

        user_field_name = {
            "first name": "first_name",
            "last name": "last_name",
            "phone": "phone",
            "email": "email",
            "password": "password_hash"
        }
        
        while True:

            user_update_field = input("What field would you like to update(password, first name, last name, phone, email) or press R to return to main menu: ").lower()
            
            if user_update_field == 'r':
                break

            if user_update_field in user_field_name:
                user_new_info = input(f"Please enter the new {user_update_field}: ")
                if user_update_field == "password":
                    salt = bcrypt.gensalt()
                    user_new_info = bcrypt.hashpw(user_new_info.encode("utf-8"), salt)
                cursor.execute(f"UPDATE Users SET {user_field_name[user_update_field]} = ? WHERE user_id = ?", (user_new_info, self.user_id))
                user_confirm_update = input(f"Are you sure that you want update {user_update_field}\nPress Y for yes N for no: ").upper()
        
                if user_confirm_update == 'Y':
                    setattr(self, user_field_name[user_update_field], user_new_info)
                    connection.commit()
                    print('Update was successful!')
                    return
                else:
                    print('Returning to menu')
                    return   
            else:
                print("Invalid field. Please try again.")
        
    
def manager_view_all():

    view_all_users = cursor.execute("SELECT * FROM Users").fetchall()

    print("***All Users***")
    print(f'{"User id":<10}{"First name":<12}{"Last name":<12}{"Phone number":<14}{"Email":<20}{"Active":<8}{"Date created":<14}{"Hire date":<11}{"User type":<11}')

    for user in view_all_users:
        user = fill_blanks(user)
        print(f"{user[0]:<10}{user[1]:<12}{user[2]:<12}{user[3]:<14}{user[4]:<20}{user[6]:<8}{user[7]:<14}{user[8]:<11}{user[9]:<11}")


def manager_user_search():
        
    while True:

        search_input = input("1: Search by first name\n2: Search by last name\n3: Return to main menu\nWhat would you like to do? ")

        if search_input == "1":
            first_name_search = input("Enter first name: ")
            first_name_search_results = cursor.execute("SELECT * FROM Users WHERE first_name LIKE ?",('%' + first_name_search + '%',)).fetchall()
            for user in first_name_search_results:
                first_name_user_object = User(*user)
                first_name_user_object.user_view()
        elif search_input == "2":
            last_name_search = input("Enter last name: ")
            last_name_search_results = cursor.execute("SELECT * FROM Users WHERE last_name LIKE ?",('%' + last_name_search + '%',)).fetchall()
            for user in last_name_search_results:
                last_name_user_object = User(*user)
                last_name_user_object.user_view()   
        elif search_input == "3":
            print("Returning to main menu")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def view_competency_report():

    competency_report_results = cursor.execute("""SELECT Users.user_id, Users.first_name, Users.last_name, Assessment_Results.score
        FROM Users
        JOIN Assessment_Results ON Users.user_id = Assessment_Results.user_id
        JOIN Assessments ON Assessment_Results.assessment_id = Assessments.assessment_id
        JOIN Competencies ON Assessments.competency_id = Competencies.competency_id""").fetchall()

    print(f'{"User id":<10}{"First name":<12}{"Last name":<12}{"Competency level":<15}')
    for user_id, first_name, last_name, score in competency_report_results:
        print(f"{user_id:<10}{first_name:<12}{last_name:<12}{score:<15}")


def manager_view_user_competency_report():

    manager_user_id_input = input("Enter the user id: ")

    competency_report_results = cursor.execute("""SELECT Users.first_name, Users.last_name, Competencies.name, Assessment_Results.score
    FROM Users
    JOIN Assessment_Results ON Users.user_id = Assessment_Results.user_id
    JOIN Assessments ON Assessment_Results.assessment_id = Assessments.assessment_id
    JOIN Competencies ON Assessments.competency_id = Competencies.competency_id
    WHERE Users.user_id = ?""", (manager_user_id_input,)).fetchall()
    
    print(f'{"First name":<12}{"Last name":<12}{"Competency":<20}{"Score":<10}')
    for first_name, last_name, competency, score in competency_report_results:
        print(f"{first_name:<12}{last_name:<12}{competency:<20}{score:<10}")


def manager_all_user_assessments():

    user_assessment_input = input("Enter the user id that you want to view all assessments for: ")

    user_info = cursor.execute("SELECT first_name, last_name FROM Users WHERE user_id = ?", (user_assessment_input,)).fetchone()
    if not user_info:
        print("User not found.")
        return

    first_name, last_name = user_info
    
    assessment_results = cursor.execute("""SELECT Assessments.name, Assessment_Results.score, Assessment_Results.date_taken
    FROM Assessment_Results
    JOIN Assessments ON Assessment_Results.assessment_id = Assessments.assessment_id
    WHERE Assessment_Results.user_id = ?""", (user_assessment_input,)).fetchall()

    if not assessment_results:
        print("No assessments found for this user.")
        return
    
    print(f"Assessment results for {first_name} {last_name}")
    print(f'{"Assessment Name":<30}{"Score":<10}{"Date Taken":<15}')
    for assessment in assessment_results:
        assessment_name, score, date_taken = assessment
        print(f"{assessment_name:<30}{score:<10}{date_taken:<15}")

    
def manager_edit():

    manager_field_name = {
        "first name": "first_name",
        "last name": "last_name",
        "phone": "phone",
        "email": "email",
        "password": "password_hash",
        "active": "active",
        "user type": "user_type"
    }
    
    while True:

        enter_user_id = input("Enter the user id: ")

        user_check = cursor.execute("SELECT * FROM Users WHERE user_id = ?", (enter_user_id,)).fetchone()

        if user_check:
            edit_user_object = User(*user_check)

            manager_update_field = input("What field would you like to update(password, first name, last name, phone, email, user type, active) or press R to return to main menu: ").lower()
            
            if manager_update_field == 'r':
                break

            if manager_update_field in manager_field_name:
                manager_new_info = input(f"Please enter the new {manager_update_field}: ")
                if manager_update_field == "password":
                    salt = bcrypt.gensalt()
                    manager_hash_info = bcrypt.hashpw(manager_new_info.encode("utf-8"), salt)
                    cursor.execute(f"UPDATE Users SET {manager_field_name[manager_update_field]} = ? WHERE user_id = ?",(manager_hash_info, enter_user_id))
                else:
                    cursor.execute(f"UPDATE Users SET {manager_field_name[manager_update_field]} = ? WHERE user_id = ?", (manager_new_info, enter_user_id))
                manager_confirm_update = input(f"Are you sure that you want update {manager_update_field}\nPress Y for yes N for no: ").upper()
        
                if manager_confirm_update == 'Y':
                    setattr(edit_user_object, manager_field_name[manager_update_field], manager_new_info)
                    connection.commit()
                    print('Update was successful!')
                    return
                else:
                    print('Returning to menu')
                    return   
            else:
                print("Invalid field. Please try again.")
        
        else:
            print("Invalid user id. Please try again.")


def manager_add_user():

    salt = bcrypt.gensalt()

    print("***Create a new user***\nPlease fill out the following information:")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    phone = input("Enter phone number: ")
    email = input("Enter email: ")
    hire_date = ("Enter their hire date (YYYY-MM-DD): ")
    password = input("Enter password: ")
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    date_created = datetime.now().strftime("%x")

    cursor.execute("""INSERT INTO Users (first_name, last_name, phone, email, password_hash, date_created, hire_date) VALUES (?,?,?,?,?,?,?)"""
                   ,(first_name, last_name, phone, email, password_hash, date_created, hire_date))

    confirm_add_user = input("Are you sure you want to add this user:\nPress Y for yes N for No: ").upper()
    if confirm_add_user == "Y":
        connection.commit()
        print(f"{first_name} {last_name} was added successfully!")
    else:
        print("Returning to menu")
        return
    

def manager_add_competency():

    print("***Adding a new competency***")

    name = input("Enter the name of the new competecy: ")
    date_created = datetime.now().strftime('%x')

    if name == '':
        print("A name for the assessment is required")
    else:
        cursor.execute("INSERT INTO Competencies (name, date_created) VALUES (?,?)", (name, date_created))

        confirm_add_competecy = input("Are you sure you want to add this competency:\nPress Y for yes N for No: ").upper()
        if confirm_add_competecy == "Y":
            connection.commit()
            print(f"{name} was added successfully!")
        else:
            print("Returning to menu")
            return
    

def manager_add_assessment():

    print("***Adding a new assessment***")

    name = input("Enter the name of the new assessment: ")
    date_created = datetime.now().strftime('%x')
    competency_id = input("Enter the ID of the competency for which this assessment belongs: ")

    competency_check = cursor.execute("SELECT competency_id FROM Competencies WHERE competency_id = ?",(competency_id,)).fetchone()

    if competency_check:
        cursor.execute("INSERT INTO Assessments (name, date_created, competency_id) VALUES (?,?,?)", (name, date_created, competency_id))

        confirm_add_assessment = input("Are you sure you want to add this assessment:\nPress Y for yes N for No: ").upper()
        if confirm_add_assessment == "Y":
            connection.commit()
            print(f"{name} was added successfully!")
        else:
            print("Returning to menu")
            return
        
    else:
        print("No competency id found")
    

def manager_add_assessment_result():
    
    user_id = input("Enter the ID of the user: ")
    assessment_id = input("Enter the ID of the assessment: ")
    score = int(input("Enter the score for the assessment (0-4): "))
    date_taken = input("Enter the date the assessment was taken (YYYY-MM-DD): ")
    manager_id = input("Enter their managers id: ")


    if not all([user_id, assessment_id, score, date_taken, manager_id]):
        print("User id, assessment id, score, or manager id cannot be blank")
    if score > 4 or score < 0:
        print("Score must be between 0-4")
    else:
        user_check = cursor.execute("SELECT user_id FROM Users WHERE user_id = ?",(user_id,)).fetchone()
        manager_check = cursor.execute("SELECT user_id, user_type FROM Users WHERE user_id = ? AND user_type = 'manager'",(manager_id,)).fetchone()
        assessment_check = cursor.execute("SELECT assessment_id FROM Assessments WHERE assessment_id = ?",(assessment_id,)).fetchone()
        if user_check and assessment_check and manager_check:
            cursor.execute("INSERT INTO Assessment_Results (user_id, assessment_id, score, date_taken, manager_id) VALUES (?, ?, ?, ?, ?)", (user_id, assessment_id, score, date_taken, manager_id))
            connection.commit()
            print("Assessment result added successfully!")
        else:
            print("One or more fields are invalid")

def manager_edit_competency():

    current_competency_id = input("Enter the competency id that you wish to edit: ")
    
    competency_check = cursor.execute("SELECT competency_id FROM Competencies WHERE competency_id = ?",(current_competency_id,)).fetchone()
    if competency_check:
        new_competency_name = input("Enter the new competency name: ")
        cursor.execute("UPDATE Competencies SET name = ? WHERE competency_id = ?", (new_competency_name, current_competency_id))
        connection.commit()
        print("Competency name updated successfully")
    else:
        print("Competency id is invalid")

def manager_edit_assessment():

    current_assessment_id = input("Enter the assessment id that you wish to edit: ")

    assessment_check = cursor.execute("SELECT assessment_id FROM Assessments WHERE assessment_id = ?",(current_assessment_id,)).fetchone()
    if assessment_check:
        new_assessment_name = input("Enter the new assessment name: ")
        cursor.execute("UPDATE Assessments SET name = ? WHERE assessment_id = ?", (new_assessment_name, current_assessment_id))
        connection.commit()
        print("Assessment name updated successfully")
    else:
        print("Assesment id is invalid")


def manager_edit_assessment_results():

    edit_user_id = input("Enter the user id: ")
    edit_assessment_id = input("Enter the assessment id: ")

    input_check = cursor.execute("SELECT user_id, assessment_id FROM Assessment_Results WHERE user_id = ? AND assessment_id = ?",(edit_user_id, edit_assessment_id)).fetchone()

    if input_check:
        edit_assessment_results = int(input("Enter the new assessment results (0-4): "))
        if edit_assessment_results > 4 or edit_assessment_results < 0:
            print("Score must be between 0-4")
        else:
            cursor.execute("UPDATE Assessment_Results SET score = ? WHERE user_id = ? AND assessment_id = ?", (edit_assessment_results, edit_user_id, edit_assessment_id))
            connection.commit()
            print("Update was successful")
    else:
        print("Either user id or assessment id are invalid")


def manager_delete_assessment_result():
    delete_user_id = input("Enter the user id: ")
    delete_assessment_id = input("Enter the assessment id: ")

    input_check = cursor.execute("SELECT * FROM Assessment_Results WHERE user_id = ? AND assessment_id = ?", (delete_user_id, delete_assessment_id)).fetchone()

    if input_check:
        confirm_delete = input("This cannot be undone are you sure you want to delete this assessment result? Y for yes or N for no: ").upper()
        if confirm_delete == 'Y':
            cursor.execute("DELETE FROM Assessment_Results WHERE user_id = ? AND assessment_id = ?", (delete_user_id, delete_assessment_id))
            connection.commit()
            print("Assessment result deleted successfully!")
        else:
            print("Deletion canceled.")
    else:
        print("No matching assessment result found.")


def export_users_to_csv():

    with open("export_users.csv", "w") as user_export:
        export_user = csv.writer(user_export)
        export_user.writerow(['User ID', 'First Name', 'Last Name', 'Phone', 'Email', 'Active', 'Date Created', 'Hire Date', 'User Type'])
        user_data = cursor.execute("SELECT user_id, first_name, last_name, phone, email, active, date_created, hire_date, user_type FROM Users").fetchall()
        for user in user_data:
            export_user.writerow(user)


def export_competency_list():

    with open("export_competency.csv", "w") as competency_export:
        competency_list = csv.writer(competency_export)
        competency_list.writerow(["Competency id", "Name", "Date Created"])
        list_data = cursor.execute("SELECT * FROM Competencies").fetchall()
        for data in list_data:
            competency_list.writerow(data)
        

def import_assessment_results_from_csv():

    csv_filename = input("Enter the name of the csv file you want to input: ")

    try:
        with open(csv_filename, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader) 
                
                for row in csv_reader:
                    user_id, assessment_id, score, date_taken, manager_id = row
                    cursor.execute("INSERT INTO Assessment_Results (user_id, assessment_id, score, date_taken, manager_id) VALUES (?, ?, ?, ?, ?)",(user_id, assessment_id, score, date_taken, manager_id))
                    
                connection.commit()
                print("Assessment results imported successfully.")
        
    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found.")
    except Exception as e:
        print("An error occurred during import:", e)
        connection.rollback()


def login_menu():

    while True:
    
        login_choice = input("Welcome!\n1: Login\n2: Exit\nWhat would you like to do? ")

        if login_choice == "1":
            user_id = input("Login id: ")
            password_hash = input("Password: ")
            login_check = cursor.execute("SELECT * FROM Users WHERE user_id = ? AND active = 1",(user_id,)).fetchone()

            if login_check:
                password_check = bcrypt.checkpw(password_hash.encode("utf-8"), login_check[5])
                if password_check:
                    logged_in_user = User(*login_check)
                    if logged_in_user.user_type == "manager":
                        manager_menu(logged_in_user)
                    else:    
                        user_menu(logged_in_user)
                else:
                    print("Login id and Password did not match")
            else:
                print("Login id invalid or the user is inactive")
                return
            
        elif login_choice == "2":
            print("Goodbye")
            break

        else:
            print("Invalid choice. Please enter 1 or 2.")

            
def user_menu(logged_in_user):  

    while True:

        user_choice = input("1: View profile\n2: View competency report\n3: Edit profile\n4: Logout\nWhat would you like to do? ")

        if user_choice == "1":
            logged_in_user.user_view()
        elif user_choice == "2":
            logged_in_user.user_competency_report()
        elif user_choice == "3":
            logged_in_user.user_edit()
        elif user_choice == "4":
            print("Logout successful")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")
            

def manager_menu(logged_in_user):

    while True:
        
        manager_choice = input("1: View menu\n2: Add menu\n3: Edit menu\n4: Delete assessment result\n5: Import/Export\n6: Logout\nWhat would you like to do? ")

        if manager_choice == "1":

            view_menu_choice = input("""1: View all users\n2: Search for a user by first or last name\n3: View all users and competency
4: View competency level for individual user\n5: View list of assessments for a user\n6: Return to main menu\nWhat would you like to do? """)
            
            if view_menu_choice == "1":
                manager_view_all()
            elif view_menu_choice == "2":
                manager_user_search()
            elif view_menu_choice == "3":
                view_competency_report()
            elif view_menu_choice == "4":
                manager_view_user_competency_report()
            elif view_menu_choice == "5":
                manager_all_user_assessments()
            elif view_menu_choice == "6":
                print("returning to main menu")
                continue
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")


        elif manager_choice == "2":

            add_menu_choice = input("""1: Add a user\n2: Add a new competency\n3: Add a new assessment to a competency
4: Add an assessment result for a user\n5: Return to main menu\nWhat would you like to do? """)
            
            if add_menu_choice == "1":
                manager_add_user()
            elif add_menu_choice == "2":
                manager_add_competency()
            elif add_menu_choice == "3":
                manager_add_assessment()
            elif add_menu_choice == "4":
                manager_add_assessment_result()
            elif add_menu_choice == "5":
                print("returning to main menu")
                continue
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

        
        elif manager_choice == "3":

            edit_menu_choice = input("""1: Edit personal information\n2: Edit user information\n3: Edit a competency\n4: Edit assessment
5: Edit assessment results\n6: Return to main menu\nWhat would you like to do? """)

            if edit_menu_choice == "1":
                logged_in_user.user_edit()
            elif edit_menu_choice == "2":
                manager_edit()
            elif edit_menu_choice == "3":
                manager_edit_competency()
            elif edit_menu_choice == "4":
                manager_edit_assessment()                
            elif edit_menu_choice == "5":
                manager_edit_assessment_results()
            elif edit_menu_choice == "6":
                print("returning to main menu")
                continue
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

        elif manager_choice == "4":
            manager_delete_assessment_result()

            
        elif manager_choice == "5":

            import_export_menu = input("1: Export user data\n2: Export competency list\n3: Import assessment results\n4: Return to main menu\nWhat would you like to do? ")

            if import_export_menu == "1":
                export_users_to_csv()
            elif import_export_menu == "2":
                export_competency_list()
            elif import_export_menu == "3":
                import_assessment_results_from_csv()
            elif import_export_menu =="4":
                print("returning to main menu")
                continue
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
            

        elif manager_choice == "6":
            print("Logout successful")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
            
            

login_menu()

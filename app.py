from flask import Flask, render_template, request, redirect, url_for
from pymysql import connections
import os
import boto3
from config import *
import hashlib

app = Flask(__name__)
# Configure the 'templates' folder for HTML templates.
app.template_folder = 'pages'
app.static_folder = 'static'

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'students'


@app.route("/", methods=['GET'], endpoint='index')
def index():
    return render_template('index.html')


@app.route("/job_listing", methods=['GET'])
def job_listing():
    return render_template('job_listing.html')


@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


@app.route("/blog", methods=['GET'])
def blog():
    return render_template('blog.html')


@app.route("/single_blog", methods=['GET'])
def single_blog():
    return render_template('single_blog.html')


@app.route("/elements", methods=['GET'])
def elements():
    return render_template('elements.html')


@app.route("/job_details", methods=['GET'])
def job_details():
    return render_template('job_details.html')


@app.route("/contact", methods=['GET'])
def contact():
    return render_template('contact.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        ic = request.form['ic']
        programmeSelect = request.form['programmeSelect']
        tutorialGrp = request.form['tutorialGrp']
        studentID = request.form['studentID']
        cgpa = request.form['cgpa']
        ucSupervisor = request.form['ucSupervisor']
        ucSupervisorEmail = request.form['ucSupervisorEmail']

        # Check if the email is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM students WHERE stud_email=%s", (email))
        results = cursor.fetchall()
        cursor.close()

        # If the email is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', email_error="The email is already in use.")

        # Otherwise, check if the IC is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM students WHERE ic=%s", (ic))
        results = cursor.fetchall()
        cursor.close()

        # If the IC is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', ic_error="The IC is already in use.")

        # Otherwise, check if the student ID is already in the database.
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE studentID=%s", (studentID))
        results = cursor.fetchall()
        cursor.close()

        # If the student ID is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('register.html', studentID_error="The student ID is already in use.")

        insert_sql = "INSERT INTO students VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (studentID,
                                        firstName,
                                        lastName,
                                        gender,
                                        email,
                                        password,
                                        ic,
                                        programmeSelect,
                                        tutorialGrp,
                                        cgpa,
                                        ucSupervisor
                                        ))
            db_conn.commit()
            cursor.close()
            # Redirect to the homepage after successful registration
            return redirect(url_for('login'))
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here

    # Fetch data from the database here
    cursor = db_conn.cursor()
    select_sql = "SELECT lectName, lectEmail FROM lecturer"
    cursor.execute(select_sql)
    data = cursor.fetchall()  # Fetch a single row
    print(data)

    return render_template('register.html', list_of_lect=data)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if role == 'Student':
            # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT stud_email, password, firstName, studentID FROM students WHERE stud_email = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                name = data[2]
                studID = data[3]

                # You should hash the provided password and compare it to the stored hashed password
                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                if password == stored_password:
                    # Passwords match, user is authenticated
                    return render_template('index.html', user_login_name=name, studentID=studID, user_authenticated=True)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
        elif role == 'Company':
            # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT compEmail, comPassword, compName FROM company WHERE compEmail = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                name = data[2]

                if password == stored_password:
                    # Passwords match, user is authenticated
                    return render_template('companyDashboard.html', user_authenticated=True)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
        elif role == 'Admin':
            # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT adminEmail, adminPassword, adminName FROM admin WHERE adminEmail = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                name = data[2]

                if password == stored_password:
                    # Passwords match, user is authenticated
                    cursor.execute("SELECT compID, compName, compEmail, compStatus FROM company")
                    companies = cursor.fetchall()

                    return render_template('adminDashboard.html', companies=companies)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
        elif role == 'Lecturer':
            # Fetch data from the database here
            cursor = db_conn.cursor()
            select_sql = "SELECT lectEmail, password, lectName, lectID FROM lecturer WHERE lectEmail = %s"
            cursor.execute(select_sql, (email,))
            data = cursor.fetchone()  # Fetch a single row

            if data:
                # Data is found in the database
                stored_password = data[1]
                lecturer_id = data[3]
                lectName = data[2]

                if password == stored_password:
                    # Passwords match, user is authenticated

                    session['lecturer_id'] = lecturer_id
                    session['lecturer_email'] = data[0]

                    # Fetch student data for this lecturer
                    select_students_sql = "SELECT * \
                                          FROM students s\
                                          JOIN lecturer l on s.ucSuperEmail = l.lectEmail \
                                          WHERE l.lectEmail = %s"
                    cursor.execute(select_students_sql, (email,))
                    student_data = cursor.fetchall()
                    
                    return render_template('lectDashboard.html', user_login_name=lectName, student_data=student_data)
                else:
                    return render_template('login.html', pwd_error="Incorrect password. Please try again.")
            else:
                return render_template('login.html', email_login_error="Email not found. Please register or try a different email.")
    return render_template('login.html')

@app.route("/studentDashboard", methods=['GET'])
def studentDashboard():
    # Retrieve the studentID from the query parameters
    student_id = request.args.get('studentID')

    # Pass the studentID to the studentDashboard.html template
    return render_template('studentDashboard.html', studentID=student_id)


def list_files(bucket, path):
    contents = []
    folder_prefix = path

    for image in bucket.objects.filter(Prefix=folder_prefix):
        # Extract file name without the folder prefix
        file_name = image.key[len(folder_prefix):]
        if file_name:
            contents.append(file_name)

    return contents


@app.route("/form", methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        studID = request.form['studentID']

        uploaded_files = request.files.getlist('acceptanceForm') + \
            request.files.getlist('parentForm') + \
            request.files.getlist('letterForm') + \
            request.files.getlist('hireEvi')

        # Uplaod image file in S3 #
        # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        # Create a folder or prefix for the files in S3
        # Replace 'your_folder_name' with your desired folder name
        folder_name = 'Student/' + studID + "/"

        list_files = []

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")

            for file in uploaded_files:
                list_files.append(file.filename)
                # Construct the key with the folder prefix and file name
                key = folder_name + file.filename

                # Upload the file into the specified folder
                s3.Bucket(custombucket).put_object(Key=key, Body=file)

                # Generate the object URL
                bucket_location = boto3.client(
                    's3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    file.filename)

        except Exception as e:
            return str('bucket', str(e))

        bucket = s3.Bucket(custombucket)

        # list_of_files = list_files(bucket)

        return render_template('form.html', my_bucket=bucket, studentID=studID, list_of_files=list_files)

    # Retrieve the studentID from the query parameters
    student_id = request.args.get('studentID')

    return render_template('form.html', studentID=student_id)


@app.route("/report", methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        studID = request.form['studentID']
        reportForm_files = request.files['reportForm']

        # Uplaod image file in S3
        s3 = boto3.resource('s3')

        # Create a folder or prefix for the files in S3
        folder_name = 'Student/' + studID + "/" + "report/"

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")

            filename = reportForm_files.filename.split('.')

            # Construct the key with the folder prefix and file name
            key = folder_name + filename[0] + "_progress_report." + filename[1]

            # Upload the file into the specified folder
            s3.Bucket(custombucket).put_object(Key=key, Body=reportForm_files)

            # Generate the object URL
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                key)

        except Exception as e:
            return str('bucket', str(e))

        bucket = s3.Bucket(custombucket)
        list_of_files = list_files(bucket, folder_name)

        return render_template('report.html', my_bucket=bucket, studentID=studID, list_of_files=list_of_files)

    # Retrieve the studentID from the query parameters
    studID = request.args.get('studentID')

    folder_name = 'Student/' + studID + "/" + "report/"

    # Uplaod image file in S3
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(custombucket)
    list_of_files = list_files(bucket, folder_name)

    return render_template('report.html', my_bucket=bucket, studentID=studID, list_of_files=list_of_files)

# -------------------------------------------------------------- Student End --------------------------------------------------------------#


# -------------------------------------------------------------- Lecturer START (Kuah Jia Yu) --------------------------------------------------------------#

@app.route("/lectRegister", methods=['GET', 'POST'])
def lectRegister():
    if request.method == 'POST':
        lectName = request.form['lectName']
        lectID = request.form['lectID']
        lectEmail = request.form['lectEmail']
        gender = request.form['gender']
        password = request.form['password']

        insert_sql = "INSERT INTO lecturer VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (lectName,
                                        lectID,
                                        lectEmail,
                                        gender,
                                        password
                                        ))
            db_conn.commit()
            cursor.close()
            # Go to the dashboard after successful registration
            return redirect(url_for('login'))
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here
    return render_template('lectRegister.html')


@app.route("/lectLogin", methods=['GET', 'POST'])
def lectLogin():
    if request.method == 'POST':
        return render_template('index.html', user_authenticated=True)

    # Fetch data from the database here
    cursor = db_conn.cursor()
    select_sql = "SELECT lectEmail, password FROM lecturer"
    cursor.execute(select_sql)
    data = cursor.fetchall()
    cursor.close()
    return render_template('lectLogin.html', lecturer=data)


@app.route("/lectDashboard", methods=['GET'])
def lectDashboard():
    return render_template('lectDashboard.html')

# ------------------------------------------------------------------- Lecturer END -------------------------------------------------------------------#

# ------------------------------------------------------------------- Company START (Wong Kar Yan) -------------------------------------------------------------------#


@app.route("/companyRegister", methods=['GET', 'POST'])
def companyRegister():
    if request.method == 'POST':
        compName = request.form['compName']
        compEmail = request.form['compEmail']
        comPassword = request.form['comPassword']

        # Check if the email is already in the database.
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM company WHERE compEmail=%s", (compEmail))
        results = cursor.fetchall()
        cursor.close()

        # If the email is already in the database, return an error message to the user and display it on the register.html page.
        if len(results) > 0:
            return render_template('companyRegister.html', email_error="This company email is already in use.")

        insert_sql = "INSERT INTO company VALUES (%s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (compName,
                                        compEmail,
                                        comPassword
                                        ))
            db_conn.commit()
            cursor.close()
            # Go to the dashboard after successful registration
            return redirect(url_for('login'))
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here
    return render_template('companyRegister.html')


@app.route("/jobReg", methods=['GET', 'POST'])
def jobReg():
    if request.method == 'POST':
        comp_name = request.form['comp_name']
        job_title = request.form['job_title']
        job_desc = request.form['job_desc']
        job_req = request.form['job_req']
        sal_range = request.form['sal_range']
        contact_person_name = request.form['contact_person_name']
        contact_person_email = request.form['contact_person_email']
        contact_number = request.form['contact_number']
        comp_state = request.form['comp_state']
        companyImage = request.files['companyImage']

        insert_sql = "INSERT INTO jobApply VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        if companyImage.filename == "":
            return "Please select a file"

        cursor.execute(insert_sql, (comp_name, job_title, job_desc, job_req, sal_range,
                       contact_person_name, contact_person_email, contact_number, comp_state))
        db_conn.commit()
        cursor.close()

        # Uplaod image file in S3 #
        comp_image_file_name_in_s3 = "company-" + \
            str(comp_name) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=comp_image_file_name_in_s3, Body=companyImage)
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3%7B0%7D.amazonaws.com/%7B1%7D/%7B2%7D".format(
                s3_location,
                custombucket,
                comp_image_file_name_in_s3)
            return redirect(url_for('companyDashboard'))
        except Exception as e:
            cursor.close()
            print(f"Error during database insertion: {e}")
            return str(e)  # Handle any database errors here

    return render_template('jobReg.html')


@app.route("/companyDashboard", methods=['GET'])
def companyDashboard():
    return render_template('companyDashboard.html')

# ------------------------------------------------------------------- Company END -------------------------------------------------------------------#

# Define the route for admin registration


@app.route("/adminRegister", methods=['GET', 'POST'])
def adminRegister():
    if request.method == 'POST':
        adminName = request.form['adminName']
        adminEmail = request.form['adminEmail']
        adminContact = request.form['adminContact']
        password = request.form['password']

        # Fetch data from the database here
        cursor = db_conn.cursor()
        select_sql = "SELECT max(adminID) FROM admin"
        cursor.execute(select_sql)
        data = cursor.fetchone()  # Fetch a single row
        data = data[0]

        print(data)
        if data == None:
            adminID = 'A' + str(10001)
        else:
            admin_no = int(data[1:]) + 1
            adminID = 'A' + str(admin_no)

        insert_sql = "INSERT INTO admin VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        try:
            cursor.execute(insert_sql, (adminID, adminName,
                           adminEmail, adminContact, password))
            db_conn.commit()
            cursor.close()
            # Redirect to admin login after successful registration
            return redirect(url_for('login'))
        except Exception as e:
            cursor.close()
            return str(e)  # Handle any database errors here

    return render_template('adminRegister.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    cursor = db_conn.cursor()
    cursor.execute("SELECT compID, compName, compEmail, compStatus FROM company")
    companies = cursor.fetchall()
    cursor.close()

    return render_template('adminDashboard.html', companies=companies)

@app.route('/approve_companies', methods=['GET', 'POST'])
def approve_companies():
    if request.method == 'POST':
        company_id = request.form.get('compID')
        action = request.form.get('action')

        # Check the value of 'action' and update the company status accordingly
        if action == 'Approve':
            new_status = 'APPROVED'
        elif action == 'Rejecte':
            new_status = 'REJECTED'
        else:
            return jsonify({"error": "Invalid action"}), 400

        # Update the company status in the database
        cursor = db_conn.cursor()
        update_query = "UPDATE company SET compStatus = %s WHERE compID = %s"
        cursor.execute(update_query, (new_status, company_id))
        db_conn.commit()
        cursor.close()

    cursor = db_conn.cursor()
    cursor.execute("SELECT compID, compName, compEmail, compStatus FROM company")
    companies = cursor.fetchall()
    cursor.close()

    return render_template('approve.html', companies=companies)

@app.route('/list_companies')
def list_companies():
    cursor = db_conn.cursor()
    cursor.execute("SELECT compID, compName, compEmail, compStatus FROM company")
    companies = cursor.fetchall()
    cursor.close()

    return render_template('listCompanies.html', companies=companies)

@app.route('/user_management')
def user_management():
    return render_template('userManagement.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


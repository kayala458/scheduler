from flask import Flask, render_template, request, redirect, flash
import calendar as cd
import datetime
import sqlite3

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.secret_key = 'some secret key'


@app.route("/", methods=["GET"])
def home():
    """Display the calendar for the current month and display who is scheduled to work on each given day"""

    # Obtain the current date/time
    now = datetime.datetime.now()

    # Store month as string and integer, store year as integer, store day of month as integer
    month = now.strftime("%B")
    month_as_int = int(now.strftime("%m"))
    year = int(now.strftime("%Y"))
    day_of_month = int(now.strftime("%d"))

    # Initialize empty list to store list of lists where each list is one week of the month
    lst_of_weeks = []

    # Access the Calendar class
    c = cd.Calendar(firstweekday=6)

    # Iterate over each week in list of weeks for this month
    for week in c.monthdayscalendar(year, month_as_int):

        # Iterate over each day
        for d in range(len(week)):

            # If the day is 0, it doesn't belong to this month. Replace 0 with a blank
            if week[d] == 0:
                day = str(week[d])
                week[d] = day.replace('0', '')

        # Add week to list of all weeks for this month
        lst_of_weeks.append(week)

    # Obtain list of doctors who are regularly scheduled to work each day of the week
    with sqlite3.connect('doctors.db') as database:

        db = database.cursor()

        monday = db.execute('SELECT first_name, last_name, specialty, monday, id FROM doctors WHERE NOT monday="Off Work"').fetchall()
        database.commit()

        tuesday = db.execute('SELECT first_name, last_name, specialty, tuesday, id FROM doctors WHERE NOT tuesday="Off Work"').fetchall()
        database.commit()

        wednesday = db.execute('SELECT first_name, last_name, specialty, wednesday, id FROM doctors WHERE NOT wednesday="Off Work"').fetchall()
        database.commit()

        thursday = db.execute('SELECT first_name, last_name, specialty, thursday, id FROM doctors WHERE NOT thursday="Off Work"').fetchall()
        database.commit()

        friday = db.execute('SELECT first_name, last_name, specialty, friday, id FROM doctors WHERE NOT friday="Off Work"').fetchall()
        database.commit()

        # Reset daily_availability table if the day is the first day of the month/ it is a new month
        if day_of_month == 1:

            default = "Regularly Scheduled"

            db.execute('''UPDATE daily_availability SET "1" = ?, "2" = ?, "3" = ?, "4" = ?, "5"= ?, "6" = ?, "7" =?,
            "8" = ?, "9" = ?, "10" = ?, "11" = ?, "12" = ?, "13" = ?, "14" = ?, "15"= ?, "16" = ?, "17" =?,
            "18" = ?, "19" = ?, "20" = ?, "21" = ?, "22" = ?, "23" = ?, "24" = ?, "25"= ?, "26" = ?, "27" =?,
            "28" = ?, "29" = ?, "30" = ?, "31" = ?''', (default, default, default, default, default, default, default,
            default, default, default, default, default, default, default, default, default, default, default, default,
            default, default, default, default, default, default, default, default, default, default, default, default))
            database.commit()

        # Select all data from the daily_availability table
        days = db.execute('''SELECT * FROM daily_availability''')
        database.commit()

        # Initialize empty lists to store the index of the columns that have any changes to the regular schedule
        ETO = []
        covering = []

        for row in days:

            for i, column in enumerate(row):

                if column == "ETO":
                    ETO.append(i)

                if column == "Covering":
                    covering.append(i)

        # Column indices should reflect the day of the month. Because id, first_name, and last_name are also columns
        # listed in the daily_availability table, subtract two for each item in the ETO and covering lists to get the
        # correct day of the month.
        corrected_ETO = [(i - 2) for i in ETO]

        corrected_covering = [(i - 2) for i in covering]

        # Create dictionaries for days where Time Off is scheduled and where coverage is provided. Keys in both
        # dictionaries are the days of the month where changes have been made and values are the id/names of doctors
        # who are on ETO or are providing coverage

        ETO_dict = {}

        for day in corrected_ETO:

            ETO_taken = db.execute('''SELECT id FROM daily_availability WHERE "%s" = "ETO"''' % (day)).fetchall()

            ETO_dict[day] = ETO_taken[0][0]

        covering_dict = {}

        for day in corrected_covering:
            coverage = db.execute('''SELECT id, last_name FROM daily_availability WHERE "%s" = "Covering"''' % (day)).fetchall()

            covering_dict[day] = coverage[0][1]

    return render_template('home.html', month=month, year=year,lst_of_weeks=lst_of_weeks, monday=monday,tuesday=tuesday,
    wednesday=wednesday, thursday=thursday, friday=friday, ETO_dict = ETO_dict, covering_dict = covering_dict)



@app.route("/days_schedule", methods=["GET", "POST"])
def days_schedule():
    """Show list of all doctors who are currently scheduled to work on a given day of the month.
       Allow user to make edits to or delete record"""

    # User reached route via GET (as by clicking a link)
    if request.method == "GET":

        # User clicked on link where type corresponds to the day of the month. Obtain that day
        day_of_month = int(request.args.get('type'))

        # Obtain the current date/time
        now = datetime.datetime.now()

        # Store month as string and integer, store year as integer
        month = now.strftime("%B")
        month_as_int = int(now.strftime("%m"))
        year = int(now.strftime("%Y"))

        # Obtain weekday as integer
        weekday = datetime.date(year, month_as_int, day_of_month).weekday()

        # Obtain dictionary that stores the names of each day of the week
        d = dict(enumerate(cd.day_name))

        # Obtain the name of the weekday that corresponds to the day of the month that was clicked on
        day_name_upper = d[weekday]

        # Change weekday name to be all lowercase (to be used in SQL queries later)
        day_name = (d[weekday]).lower()

        # Open SQLite database
        with sqlite3.connect('doctors.db') as database:

            db = database.cursor()

            # Obtain doctors' information from table only for doctors who are scheduled to work that day of the week
            doctors = db.execute('SELECT first_name, last_name, specialty, %s, id FROM doctors WHERE NOT %s ="Off Work"' % (day_name, day_name)).fetchall()

            database.commit()

            # Get the information of any doctors who requested time off for this day
            off = db.execute('SELECT first_name, last_name, id FROM daily_availability WHERE "%s" = "ETO"' % (day_of_month)).fetchall()

            database.commit()

            # If there are doctors who have requested time off on this day:
            if off:

                for i in off:

                    off_id = i[2]

                    # Update list of doctors who regularly work on that weekday so that anyone who is on ETO is not included
                    doctors = [i for i in doctors if i[4] != off_id]

                # Get the information of any doctor's who covering for another doctor on this day
                covering = db.execute('SELECT first_name, last_name, id FROM daily_availability WHERE "%s" = "Covering"' % (day_of_month)).fetchall()

                database.commit()

                # If coverage was established for the person taking time off
                # Assume only one doctor can take time off per day, so there will be at most one doctor providing coverage
                # on any given day
                if covering:

                    # Store the covering doctor's id
                    cover_id = covering[0][2]

                    # Obtain the covering doctor's name and specialty
                    covering = db.execute('SELECT first_name, last_name, specialty FROM doctors WHERE id = ?''', (cover_id,)).fetchall()

                    # Add covering doctor to list of doctors already scheduled for that day
                    doctors = doctors + covering

                    return render_template('days_schedule.html', day_name_upper=day_name_upper, month=month,
                    day_of_month=day_of_month, doctors=doctors, off=off, time_off = True, covering = covering, coverage_found = True)

                else:

                    return render_template('days_schedule.html', day_name_upper=day_name_upper, month=month,
                                   day_of_month=day_of_month, doctors=doctors, off=off, time_off = True)

            else:

                return render_template('days_schedule.html', day_name_upper=day_name_upper, month=month, day_of_month=day_of_month, doctors=doctors)


    # User selects "Submit" button to indicate a change to the regular schedule for that day
    if request.method == "POST":

        # Obtain ID of doctor who cannot work
        id = request.form.get("id")

        # Obtain doctor's specialty
        specialty = request.form.get("specialty")

        # Check whether doctor was scheduled for inpatient, outpatient, or consult
        location = request.form.get("location")

        # Obtain day of week change was made for
        day_of_week = (request.form.get("day of week")).lower()

        # Obtain day of month change was made for
        day_of_month = request.form.get("day of month")

        # If they are scheduled for inpatient, find someone to cover for them who shares their specialty
        if location == "Inpatient":

            # Open SQLite database
            with sqlite3.connect('doctors.db') as database:

                db = database.cursor()

                # Obtain doctors' information from table only for doctors who are scheduled to work that day of the week
                # Arrange in order of those who have covered the least amount of shifts so far
                # The person who has covered the least amount of times will be selected to cover
                doctors = db.execute('''SELECT id, first_name, last_name, no_shift_covered FROM doctors 
                WHERE %s ="Off Work" AND specialty = ? ORDER BY no_shift_covered ASC''' % (day_of_week), (specialty,)).fetchall()

                database.commit()

                # If no doctor is available that shares the speciality of the person requesting time off, print error
                if not doctors:

                    flash('Unable to find a replacement')
                    return redirect('/')

                else:

                    # The doctor's replacement is the one who is listed first
                    replacement = doctors[0]

                    # Add one to the number of shifts that doctor has covered
                    db.execute('''UPDATE doctors SET no_shift_covered = ? WHERE id = ?''', ((replacement[3] + 1), replacement[0],))

                    database.commit()

                    item = "Covering"

                    # Display covering doctor as being working that day
                    db.execute("""UPDATE daily_availability SET "%s" = ? WHERE id = ?""" % (day_of_month), (item, replacement[0]))

                    database.commit()

                    item = "ETO"

                    # Display requesting doctor as being out of office for that day
                    db.execute("""UPDATE daily_availability SET "%s" = ? WHERE id = ?""" % (day_of_month), (item, id))

                    database.commit()

                    flash('Coverage was found.')
                    return redirect('/')

        # If they are scheduled for Consult, find someone to cover for them regardless of specialty
        if location == "Consult":

            # Open SQLite database
            with sqlite3.connect('doctors.db') as database:
                db = database.cursor()

                # Obtain doctors' information from table only for doctors who are scheduled to work that day of the week
                doctors = db.execute('''SELECT id, first_name, last_name, no_shift_covered FROM doctors 
                WHERE %s ="Off Work" ORDER BY no_shift_covered ASC''' % (day_of_week)).fetchall()

                database.commit()

                if not doctors:

                    flash('Unable to find a replacement')
                    return redirect('/')

                else:

                    # The doctor's replacement is the one who is listed first
                    replacement = doctors[0]

                    # Add one to the number of shifts that doctor has covered
                    db.execute('''UPDATE doctors SET no_shift_covered = ? WHERE id = ?''', ((replacement[3] + 1), replacement[0],))

                    database.commit()

                    item = "Covering"

                    # Display covering doctor as being working that day
                    db.execute("""UPDATE daily_availability SET "%s" = ? WHERE id = ?""" % (day_of_month), (item, replacement[0]))

                    database.commit()

                    item = "ETO"

                    # Display requesting doctor as being out of office for that day
                    db.execute("""UPDATE daily_availability SET "%s" = ? WHERE id = ?""" % (day_of_month), (item, id))

                    database.commit()

                    flash('Coverage was found.')
                    return redirect('/')

        # If they are scheduled for Outpatient, no coverage is necessary
        if location == "Outpatient":

            # Open SQLite database
            with sqlite3.connect('doctors.db') as database:

                db = database.cursor()

                item = "ETO"

                # Display doctor as being out of office for that day
                db.execute("""UPDATE daily_availability SET "%s" = ? WHERE id = ?""" % (day_of_month), (item, id))

                database.commit()

                flash('No Coverage is necessary')
                return redirect('/')


@app.route("/rules", methods=["GET", "POST"])
def rules():
    """Allow user to enter a new doctor and establish their regular schedule for each day of the week"""

    # User reached route via GET (as by clicking a link)
    if request.method == "GET":

            # Display form
            return render_template("rules.html")

    # User selects "Submit" button
    if request.method == "POST":

        # If users clicks "Submit", store data in database table
        if request.form['action'] == 'Submit':

            with sqlite3.connect('doctors.db') as database:

                db = database.cursor()

                # Create table to store doctor's information if one does not already exist
                db.execute('''CREATE TABLE IF NOT EXISTS doctors (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                first_name TEXT NOT NULL, last_name TEXT NOT NULL, specialty TEXT NOT NULL, monday TEXT, tuesday TEXT, 
                wednesday TEXT, thursday TEXT, friday TEXT, no_shift_covered INTEGER);''')

                database.commit()

                # Obtain the information the user entered
                first_name = request.form.get("first_name")
                last_name = request.form.get("last_name")
                specialty = request.form.get("specialty")

                monday = request.form.get("monday")
                if not monday:
                    monday = "Off Work"

                tuesday = request.form.get("tuesday")
                if not tuesday:
                    tuesday = "Off Work"

                wednesday = request.form.get("wednesday")
                if not wednesday:
                    wednesday = "Off Work"

                thursday = request.form.get("thursday")
                if not thursday:
                    thursday = "Off Work"

                friday = request.form.get("friday")
                if not friday:
                    friday = "Off Work"

                no_shifts_covered = 0

                # Add all of the doctor's information to the doctors table
                db.execute("INSERT INTO doctors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, first_name, last_name, specialty, monday, tuesday, wednesday, thursday, friday, no_shifts_covered))

                database.commit()

                # Create a table that shows who is taking time off and who is providing coverage for each day of the month
                # If table does not already exist
                db.execute('''CREATE TABLE IF NOT EXISTS daily_availability (id INTEGER NOT NULL, first_name TEXT NOT NULL,
                last_name TEXT NOT NULL, "1" TEXT NOT NULL, "2" TEXT NOT NULL, "3" TEXT NOT NULL, "4" TEXT NOT NULL,
                "5" TEXT NOT NULL, "6" TEXT NOT NULL, "7" TEXT NOT NULL, "8" TEXT NOT NULL, "9" TEXT NOT NULL, "10" TEXT NOT NULL,
                "11" TEXT NOT NULL, "12" TEXT NOT NULL, "13" TEXT NOT NULL, "14" TEXT NOT NULL, "15" TEXT NOT NULL, "16" TEXT NOT NULL,
                "17" TEXT NOT NULL, "18" TEXT NOT NULL, "19" TEXT NOT NULL, "20" TEXT NOT NULL, "21" TEXT NOT NULL, "22" TEXT NOT NULL,
                "23" TEXT NOT NULL, "24" TEXT NOT NULL, "25" TEXT NOT NULL, "26" TEXT NOT NULL, "27" TEXT NOT NULL, "28" TEXT NOT NULL,
                "29" TEXT NOT NULL, "30" TEXT NOT NULL, "31" TEXT NOT NULL);''')

                database.commit()

                # Obtain all doctors' information from table
                doctors = db.execute('SELECT * FROM doctors').fetchall()

                database.commit()

                # Iterate over each doctor listed and grab their id and name
                for row in doctors:
                    id = row[0]
                    first_name = row[1]
                    last_name = row[2]
                    default = "Regularly Scheduled"

                    # Select all ids for doctors already entered into the daily_availability table
                    ids = db.execute('SELECT id FROM daily_availability').fetchall()

                    database.commit()

                    # For each doctor in doctors table, store their id as a tuple to match what is shown in ids
                    tup = (id,)

                    # If the id from doctors is not an id in the daily_availability table, add id/doctor to daily_availability
                    # Set each day to "Regularly Scheduled"
                    if tup not in ids:

                        db.execute('''INSERT INTO daily_availability VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',(id, first_name, last_name, default, default,
                        default, default, default, default, default, default, default, default, default, default, default,
                        default, default, default, default, default, default, default, default, default, default, default,
                        default, default, default, default, default, default, default))

                    database.commit()

                return redirect("/")



@app.route("/doctors", methods=["GET", "POST"])
def doctors():
    """Show list of all doctors who are currently added to database, allow user to make edits to or delete record"""

    # User reached route via GET (as by clicking a link)
    if request.method == "GET":

        # Open SQLite database
        with sqlite3.connect('doctors.db') as database:

            db = database.cursor()

            # Obtain doctors' information from doctors table, display info on page
            doctors = db.execute("SELECT first_name, last_name, specialty, monday, tuesday, wednesday, thursday, friday, id FROM doctors").fetchall()

            return render_template('doctors.html', doctors=doctors)


    # User selects "Submit Changes" or "Delete" button
    if request.method == "POST":

        # User clicks "Submit Changes" to edit information of existing doctor
        if request.form['action'] == 'Submit Changes':

            # Obtain doctor's ID
            id = request.form.get("id")

            # Open SQLite database
            with sqlite3.connect('doctors.db') as database:

                db = database.cursor()

                # Obtain the information the user entered
                first_name = request.form.get("first_name")
                last_name = request.form.get("last_name")
                specialty = request.form.get("specialty")

                monday = request.form.get("monday")
                if not monday:
                    monday = "Off Work"

                tuesday = request.form.get("tuesday")
                if not tuesday:
                    tuesday = "Off Work"

                wednesday = request.form.get("wednesday")
                if not wednesday:
                    wednesday = "Off Work"

                thursday = request.form.get("thursday")
                if not thursday:
                    thursday = "Off Work"

                friday = request.form.get("friday")
                if not friday:
                    friday = "Off Work"

                # Update information for that specific doctor to reflect changes the user entered
                db.execute("""UPDATE doctors SET first_name = ?, last_name = ?, specialty = ?, monday =?, tuesday = ?,
                            wednesday = ?, thursday = ?,friday =? WHERE id = ?""", (first_name, last_name, specialty,
                            monday, tuesday, wednesday, thursday, friday, id))

                return redirect("/doctors")


        # User clicked on delete button.
        if request.form['action'] == 'Delete Record':

            # Obtain doctor's ID
            id = request.form.get("id")

            # Open SQLite database
            with sqlite3.connect('doctors.db') as database:

                db = database.cursor()

                # Delete record from doctors table
                db.execute("DELETE FROM doctors WHERE id=?", (id,))

                # Delete record from daily_availability table
                db.execute("DELETE FROM daily_availability WHERE id=?", (id,))

                return redirect("/doctors")
Explanation of application: https://www.youtube.com/watch?v=4oN-cYCKFp4&t=17s

For this project, I wanted to create a web application that would help my sister with her job as a hospital office manager in New Jersey. She is in charge of distributing a monthly schedule to each of the doctors that work in her office. Her boss creates this schedule, but she is adverse to any sort of technology that doesn’t do all of the work for her, so schedules are updated and distributed on paper. Any time a change is made, a new version of the schedule has to be re-distributed to the entire office. As you can imagine, this leaves a lot of room for error. So my application seeks to automate this process and store it in one central location, so that changes are immediately available to all of the doctors.

To understand how my application works, there are a few things you should know about how schedules are determined in this office. Every doctor belongs to one of three specialties: General Rehab Medicine, Brain Injury, and Stroke. In addition, each doctor might be in a different location depending on the day of the week. They might be working Inpatient, Outpatient, or in a Satellite office as a consult. If a doctor who is scheduled to work Inpatient requests time off, only a doctor within their specialty can cover for them. If the doctor is scheduled to do consult work, their replacement doesn’t have to share their specialty. Lastly, doctors who work outpatient are not required to find coverage.

For this project, I created two tables: one called “doctors” that stores each doctor, their specialty, and where they usually work for every weekday. The second table, called “daily availability” also stores the id and name of each doctor, but here the column names are each day of the month, 1 through 31. By default every doctor will show as “regularly scheduled” for each day of the month.

Opening the app, we can see what this looks like. As you can see, we have a calendar for the current month, May, displayed. Each day shows who is scheduled to work that day and their specialty. The blue hues refer to which office location the doctor is in. You can see exactly which location by hovering over the item. Doctors shown in pink were scheduled to work that day, but have requested time off. Doctors shown in green have agreed to cover for the doctor shown in pink.

Going back to the code, the next function called “Rules” shows a form which allows the user to enter the information of a new doctor. Once they submit, entries from new doctor form are obtained and added to both the “doctors” table and to the daily availability table. The next function, called “doctors” has two action items. First, when the page is loaded, it’ll pull all of the doctors currently listed in the “doctors” table and display their information. Then, if the user edits or deletes a doctor’s information, the doctors table is updated accordingly.

To see this in action, we’ll click on “Add New Doctor” from the home page and fill out the form. (Use Name: Mike Burns, Specialty: General Rehab Medicine, Tuesday: Inpatient, Thursday: Consult, Friday: Outpatient). Once we submit that, we can go to “View All Existing Doctors” to see him listed there. From there, if we click “Edit”, we can make any changes we want. For example, I can change his specialty (select “Brain Injury”) and add an inpatient shift for Monday. When we submit, we see those changes made immediately. Now if we go back to the home page, you can see him added to the calendar.

The last function in my code is called “Day’s schedule” and shows everyone who’s scheduled on the day of the month the user clicks on. It looks to the “daily availability” table to see if any doctors are out or are covering for another doctor on that day. If so, it’ll take that information into account. If not, it will display the regular schedule for that weekday.

Then, if the user indicates that a doctor is not going to be working that day, the function will check what location the doctor was scheduled to be in and will identify a doctor who is eligible to cover their shift, if necessary. The covering doctor will automatically be added to the display and the daily availability table will be updated accordingly.

To see how this works, we can click on any day of the month from the home page. Let’s look at one that hasn’t had any changes made to it yet (May 19). From here, we can click “edit” for the doctor we just added and indicate that he won’t be working on this day. In this case, coverage was found, so the covering doctor was added to that day’s schedule. On the home page, you can see these changes in pink and green. When we click back on that day, it’s also listed at the top of the page.

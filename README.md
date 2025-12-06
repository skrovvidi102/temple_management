# final-project

Temple Management System (TMS)

A complete desktop-based application designed to digitalize and streamline temple operations. The system helps managers and staff efficiently handle pooja bookings, donations, stage reservations, festival events, revenue tracking, and employee management. This project was developed according to stakeholder requirements and updated based on their continuous feedback.

Overview

The Temple Management System (TMS) replaces manual temple record-keeping with a structured, user-friendly digital system. Managers can view and manage all temple activities from one place, while staff can perform their assigned tasks using a secure login.

Objectives
	•	Simplify and automate temple daily operations
	•	Maintain accurate worship, donation, and booking records
	•	Provide monthly statistics, reports, and revenue tracking
	•	Improve transparency and reduce human errors
	•	Offer a well-organized festival calendar for better planning

Technologies Used
	•	Python 3.x
	•	Tkinter — GUI framework
	•	SQLite3 — Local database
	•	tkcalendar — Calendar & date selection
	•	Matplotlib — Graphs for monthly reports
	•	FPDF / ReportLab — PDF report generation

Modules Implemented

1. Worship (Pooja) Management
	•	Add/Edit/Delete pooja types
	•	Book poojas for devotees
	•	Generate booking receipts
	•	Track daily and monthly pooja counts
	•	Export pooja records to CSV

2. Donation Management
	•	Record temple donations
	•	Track donation types and donor details
	•	View and export donation reports
	•	Generate PDF receipts

3. Stage / Event Booking
	•	Book stages for events
	•	Prevent double-bookings
	•	View all upcoming reservations
	•	Export event bookings to CSV

4. Employee & Login Management
	•	Add/Delete staff records
	•	Create employee login credentials
	•	Password hashing for secure authentication
	•	Employee role-based access

5. Festival Calendar
	•	Manager can add/update festival events
	•	Staff can view upcoming festivals
	•	Integrated using tkcalendar
	•	Helps plan bookings and staffing

6. Manager Dashboard 
	•	Overview of total worships, bookings, and donations
	•	Monthly statistical charts
	•	Export monthly reports
	•	Revenue monitoring

Database Design (ERD Based on 3NF)

The system includes well-structured normalized tables:
	•	employees
	•	login_credentials
	•	worship_types
	•	worship_bookings
	•	donations
	•	stage_bookings
	•	festival_events

The ERD was revised multiple times based on updates from the stakeholder and backend functional requirements.

How to Run the Project
	1.	Install Python 3.x
	2.	Install required packages:
pip install matplotlib tkcalendar fpdf reportlab
	3.	Run the db_ui.py script:
python main.py
	4.	Ensure the following files are in the same project directory:
	•	db_ui.py
	•	temple_db.py
	•	pdf_utils.py
    .   manager_dashboard.py
    .   staff_dashboard.py
	•	UI files / images


Contributors
	•	Saketh Krovvidi
    .   Sasak reddy Yerrabothu

Future Enhancements
	•	SMS/Email notifications for bookings
	•	Web-based version for online pooja/stage reservations
	•	Prasadam/Inventory management
	•	Multi-branch temple support
    .   Multi-language support

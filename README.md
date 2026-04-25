Parkease 🚗
Parkease is a web-based parking management system built with Django, designed to streamline vehicle check-in and check-out operations at a parking stage. The system handles everything from registering vehicles to calculating parking fees and generating daily revenue reports.
Features
🚘 Vehicle Management

-Register incoming vehicles with driver details, plate number, vehicle type, model, and color
-View all currently parked and signed-out vehicles
-Sign out vehicles and automatically calculate the parking fee based on time spent

💰 Smart Fee Calculation
Fees are calculated based on the time of day and duration of stay:

Short stay (under 3 hours) — flat rate regardless of time
Daytime (6:00 AM – 6:59 PM) — full day rate
Nighttime (7:00 PM – 5:59 AM) — full night rate
Stays that span multiple periods compound automatically — each day and night period is charged independently

🧾 Receipt Generation
Every sign-out generates a unique receipt with a PKE-XXXXXX reference number, showing the vehicle details, duration of stay, and total fee charged.
📊 Daily Reports
A daily report page shows all transactions for a selected date, broken down by parking, tyre clinic, and battery section revenue — with a combined total.
🔧 Additional Services

Tyre Clinic — log and track tyre service jobs
Battery Section — manage battery replacement transactions

👥 User Roles & Access Control
The system supports two roles:

Admin — full access to the dashboard, reports, all services, and user management
Attendant — limited access to vehicle registration and the vehicle list only
Section manager - limited access to to the tyre clinic and battery hire sector , and is able to set prices for these functions 

Backend: Python, Django 6
Database: SQLite (development)
Frontend: Bootstrap 5, custom CSS
Authentication: Django's built-in auth with group-based role management

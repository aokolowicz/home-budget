# Home Budget

### Live Demo: https://juzew.pythonanywhere.com

### Video Demo:  https://youtu.be/lWV6yXo6JOg

## Description

The Home Budget project is a web application designed to help users manage their expenses by keeping track of their spending habits.
The application allows users to manage their expenses efficiently by adding, deleting, and editing expenses and categories. It also provides visual representations of expense data in the form of pie chart to help users understand their spending patterns.

### File Structure:

- **`app.py`**: This file contains the main Flask application where different routes are defined to handle various functionalities of the budgeting app.

- **`config.py`**: Configuration file for managing database credentials.

- **`helpers.py`**: This file contains utility functions used across the application for database operations, data processing, and other helper functions. It also contains the names of the months used for all routes.

- **`static/`**
  - `themes.css`: This folder contains the CSS file that adds the styles and themes for the frontend of the application.

- **`templates/`**:
  - `layout.html`: The base HTML layout used as a template for other HTML files.
  - `index.html`: Template for displaying the current month's expenses by category and day.
  - `add_expense.html`: Template for adding a new expense to the budget.
  - `categories.html`: Template for managing and editing expense categories.
  - `delete_expense.html`: Template for deleting expenses from the budget (when there is more than one on one day).
  - `login.html`: Template for user login functionality.
  - `pie_chart.html`: Template for displaying an annual visualization of the expenses in the form of a pie chart.
  - `register.html`: Template for user registration.
  - `sorry.html`: Template for displaying error messages.

The `app.py` file handles different routes:
- **`/`**: Shows the current month's view of expenses.
- **`/add`**: Adds a new expense to the database.
- **`/categories`**: Allows editing of expense categories.
- **`/delete/category`**: Removes a category from the database.
- **`/delete/expense`**: Removes an expense from the database.
- **`/login`**: Logs the user into the application.
- **`/logout`**: Logs the user out of the application.
- **`/register`**: Registers a new user.
- **`/rename`**: Changes the name of a category.
- **`/structure`**: Generates a pie chart displaying expense categories.

### Design choices

Certain design choices have been made to ensure better code organization, separation of concerns, and user experience. The project utilizes Flask, a lightweight Python web framework, due to its simplicity and ease of use.

MySQL is chosen as the database management system, provided by PythonAnywhere, for its scalability and compatibility with Flask applications. Jinja2 templating allows for dynamic rendering of HTML templates, which was necessary to get different views depending on the user's activity.

The use of Flask, Jinja2 templates, and MySQL database for backend operations allows for a scalable and user-friendly budget management system.

The project employs Flask's session management to maintain user authentication and session data throughout the application. The `session` variable is utilized not only for user identification but also to store crucial information like years of expenses stored in the database and the current year and month selected by the user.
These session variables ensure secure user login, access control, and persistent user-specific data across various routes. This functionality enables users to seamlessly navigate through their budget data while preserving their authentication status and personalized settings.

Behind this application is a MySQL database hosted on PythonAnywhere, used as the basis for storing expense-related data. This database organizes and manages user-specific expense records, categories, and user authentication details efficiently.

The project integrates Bootstrap 5.3.1 to ensure a responsive and visually appealing user interface. This version of Bootstrap enhances the project's frontend presentation, ensuring compatibility across various devices and browsers while maintaining a modern and intuitive layout.

## Features

1. **Expense Tracking.**
Effortlessly record and manage your expenses with a tracking system. Log expenses by category, date, and amount, providing a detailed overview of spending habits.

2. **Category Management.**
Manage expense categories efficiently, enabling users to create, edit, and delete categories to customize their expense tracking.

3. **User-Friendly Interface**.
The application offers an intuitive and responsive interface powered by Bootstrap 5.3.1, ensuring seamless navigation and an optimal viewing experience across devices.

4. **User Authentication.**
Secure user authentication system to safeguard personal financial data. Users can register, log in, and manage their accounts, ensuring privacy and confidentiality.

5. **Yearly Overview.**
Provides a comprehensive yearly visualization of expenses, allowing users to analyze their spending habits and plan budgets effectively.

## Prerequisites

Ensure you have Python installed on your machine. Additionally, install the required libraries by running:

```bash
pip install Flask Flask-Session Flask-SQLAlchemy matplotlib mpld3 python-dotenv seaborn SQLAlchemy Werkzeug
```

## Configuration & Setting Up `.env`

1. **Create a `.env` File**: In the root of your project, create a file named `.env`.

2. **Add Environment Variables**: Inside the `.env` file, add your sensitive environment variables, such as database credentials, in the following format:

   ```bash
   DB_USERNAME='your_database_username'
   DB_PASSWORD='your_database_password'
   DB_HOSTNAME='your_database_hostname'
   DB_NAME='your_database_name'
   ```

3. **Load Environment Variables**: To load the environment variables into your application, use the `python-dotenv` library.

4. **Usage in `app.py` or WSGI File**: In your `app.py` or WSGI file, include the following code at the top to load the environment variables (path adjustments may be needed):
   
   ```python
   from dotenv import load_dotenv

   # Load environment variables from .env file
   load_dotenv()
   ```

## Notes

This project was developed as a part of [CS50 course](https://cs50.harvard.edu/x/2023/). Acknowledgments to all the creators of this course, which is an amazing introduction to the world of IT.

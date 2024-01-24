import datetime
import mpld3
import re
import seaborn as sns

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from matplotlib.figure import Figure
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_values, login_required, sorry, usd, months

# Configure application
app = Flask(__name__)

# Add 'break' and 'continue' statement
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# Custom filter
app.jinja_env.filters['usd'] = usd

# Configure session to use filesystem (instead of signed cookies)
# Flask-Session is an extension for Flask that adds support
# for server-side sessions to your application.
# https://stackoverflow.com/questions/32084646/flask-session-extension-vs-default-session
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL('sqlite:///budget.db')


@app.route('/')
@login_required
def index():
    """Show current month view of expenses."""

    # Get list of years of expenses from database and remember them
    # to share across all templates
    session['years'] = get_values(
        db, 'expenses', 'year', session['user_id'], distinct=True
    )

    # Determine the year for which expenses will be displayed
    if request.args.get('disp_year'):
        session['year'] = request.args.get('disp_year')
    else:
        session['year'] = datetime.date.today().year

    # Determine the month for which expenses will be displayed
    # Based on user request or defaulting to current month
    if request.args.get('months_radio'):
        month_no = months.index(request.args.get('months_radio')) + 1
    else:
        month_no = datetime.date.today().month

    # Query database to get categories of the logged-in user
    cat_list = get_values(db, 'categories', 'category', session['user_id'])

    # Query database to find the sum of expenses per category and day
    # for the selected month
    month_expenses = {}
    total_expenses = {}
    for category in cat_list:
        expenses = db.execute(
            """
            SELECT expenses.id AS expense_id, year, month, day,
                   SUM(expense) AS expense
              FROM expenses, categories
             WHERE expenses.category_id = categories.id
               AND expenses.user_id = categories.user_id
               AND expenses.user_id = ?
               AND category = ?
               AND month = ?
               AND year = ?
             GROUP BY year, month, day
            """,
            session['user_id'],
            category,
            month_no,
            session['year'],
        )

        # Add sorted list of dicts with all expenses per day
        # to the dictionary with categories
        month_expenses[category] = expenses

        # Query database to calculate total expenses per category
        # for the selected month
        total = db.execute(
            """
            SELECT SUM(expense) AS sum
              FROM expenses, categories
             WHERE expenses.category_id = categories.id
               AND expenses.user_id = categories.user_id
               AND expenses.user_id = ?
               AND category = ?
               AND month = ?
               AND year = ?
            """,
            session['user_id'],
            category,
            month_no,
            session['year'],
        )

        # Add total sum of expenses to the dict by a category
        # (only one dict of sums in 'total')
        total_expenses[category] = total[0]['sum']

    # Render the template with retrieved data
    return render_template(
        'index.html',
        months=months,
        month_no=month_no,
        year=session['year'],
        years=session['years'],
        month_expenses=month_expenses,
        total_expenses=total_expenses,
        cat_list=cat_list,
    )


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    """Add new expense to the database."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # Retrive year, month, day if 'date' field is filled in
        try:
            year, month_no, day = request.form.get('date').split('-')
        except ValueError:
            # Error handling for invalid date format
            return sorry('Must provide date.')

        # Check if user selected category in 'category' field
        if request.form.get('category_id') == '0':
            return sorry('Must provide category.')

        # Check if the 'expense' field is empty
        if not request.form.get('expense'):
            return sorry('Must provide amount.')

        # Insert the new expense into the 'expenses' table
        db.execute(
            """
            INSERT INTO expenses (user_id, year, month, day, category_id, expense)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            session['user_id'],
            year,
            month_no,
            day,
            request.form.get('category_id'),
            request.form.get('expense'),
        )
        return redirect('/')

    # User reached route via GET
    else:
        # Query database to get id and categories of the logged-in user
        cat_list = db.execute(
            """
            SELECT id, category
              FROM categories
             WHERE user_id = ?
             ORDER BY category
            """,
            session['user_id'],
        )
        return render_template(
            'add_expense.html',
            cat_list=cat_list,
            years=session['years'],
        )


@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    """Edit expense categories."""

    # User reached route via POST (as by submitting a form via POST)
    # Create a category
    if request.method == 'POST':
        # Check if the 'category_name' field is empty
        if not request.form.get('category_name'):
            return sorry('Must provide category name.')

        # Query database to get categories of the logged-in user
        cat_list = get_values(db, 'categories', 'category', session['user_id'])

        # Change categories' names to lowercase
        cat_list = [category.lower() for category in cat_list]

        # Check if the entered category name already exists
        if request.form.get('category_name').lower() in cat_list:
            return sorry('Category name already exists.')

        # Insert the new category into the 'categories' table
        db.execute(
            'INSERT INTO categories (category, user_id) VALUES(?, ?)',
            request.form.get('category_name').title(),
            session['user_id'],
        )

        # Redirect user to category list
        return redirect('/categories')

    # User reached route via GET
    else:
        return render_template(
            'categories.html',
            years=session['years'],
            cat_list=get_values(
                db,
                'categories',
                'category',
                session['user_id'],
            ),
        )


@app.route('/delete/category', methods=['GET', 'POST'])
@login_required
def delete_category():
    """Remove a category from from the database."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # Query database to check if there are any expenses in category
        expenses_in_category = db.execute(
            """
            SELECT id, category_id
              FROM expenses
             WHERE user_id = ?
               AND category_id IN
                   (SELECT id
                      FROM categories
                     WHERE user_id = ?
                       AND category = ?)
            """,
            session['user_id'],
            session['user_id'],
            request.form.get('del_category'),
        )

        # If the category is empty, can be deleted
        if not expenses_in_category:
            db.execute(
                """
                DELETE FROM categories
                 WHERE category = ?
                   AND user_id = ?
                """,
                request.form.get('del_category'),
                session['user_id'],
            )
            # Show all categories
            return redirect('/categories')

        else:
            return sorry(
                f'Cannot delete. '
                f'{request.form.get("del_category")} category is not empty.'
            )

    # User reached route via GET
    else:
        return redirect('/')


@app.route('/delete/expense', methods=['GET', 'POST'])
@login_required
def delete_expense():
    """Remove an expense from the database."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # Request to remove the chosen expense in 'delete_expense.html'
        if request.form.get('del_chosen_expense'):
            db.execute(
                'DELETE FROM expenses WHERE id = ?',
                request.form.get('del_chosen_expense'),
            )
            # Redirect user to home page
            return redirect('/')

        # Request to remove the expense
        if request.form.get('del_expense'):
            # Query database to find the expense info
            expense_category_day = db.execute(
                """
                SELECT year, month, day, category_id, category
                  FROM expenses
                  JOIN categories
                    ON expenses.category_id = categories.id
                 WHERE expenses.user_id = ?
                   AND expenses.id = ?
                """,
                session['user_id'],
                request.form.get('del_expense'),
            )

            # Count all expenses on this day
            expenses_list = db.execute(
                """
                SELECT id, expense FROM expenses
                 WHERE user_id = ?
                   AND year = ?
                   AND month = ?
                   AND day = ?
                   AND category_id = ?
                """,
                session['user_id'],
                expense_category_day[0]['year'],
                expense_category_day[0]['month'],
                expense_category_day[0]['day'],
                expense_category_day[0]['category_id'],
            )

            # If there is more than one expense, redirect user to choose
            # which to delete
            if len(expenses_list) > 1:
                return render_template(
                    'delete_expense.html',
                    expenses_list=expenses_list,
                    expense_category_day=expense_category_day,
                    years=session['years'],
                )

            # If only one expense, delete it
            else:
                db.execute(
                    'DELETE FROM expenses WHERE id = ?',
                    request.form.get('del_expense'),
                )
                # Redirect user to home page
                return redirect('/')

    # User reached route via GET
    else:
        return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log user in."""

    # Forget any name
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # Check if the 'username' field is empty
        if not request.form.get('username'):
            return sorry('Must provide username.')

        # Check if the 'password' field is empty
        if not request.form.get('password'):
            return sorry('Must provide password.')

        # Query the database to get a username
        user = db.execute(
            'SELECT * FROM users WHERE username = ?',
            request.form.get('username'),
        )

        # Check if the entered username already exists
        if (len(user) != 1
                or not check_password_hash(user[0]['hash'],
                                           request.form.get('password'))):
            return sorry('Invalid username or password.')

        # Remember which user logged in
        session['user_id'] = user[0]['id']

        # Redirect user to home page
        return redirect('/')

    # User reached route via GET
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register user."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # Check if the 'username' field is empty
        if not request.form.get('username'):
            return sorry('Must provide username.')

        # Query the database to get a list of existing usernames
        usernames = db.execute('SELECT username FROM users')

        # Check if the entered username already exists in the database
        for user in usernames:
            if request.form.get('username') == user['username']:
                return sorry('Username already exists.')

        # Check if the 'password' field is empty
        if not request.form.get('password'):
            return sorry('Must provide password.')

        # Check if the 'confirmation' field matches the 'password' field
        if request.form.get('confirmation') != request.form.get('password'):
            return sorry('Passwords must be the same.')

        # Hash the user's password before storing it in the database
        hashed_password = generate_password_hash(request.form.get('password'))

        # Insert the username and hashed password into the 'users' table
        db.execute(
            'INSERT INTO users (username, hash) VALUES(?, ?)',
            request.form.get('username'),
            hashed_password,
        )

        # Redirect user to the homepage after successful registration
        return redirect('/')

    # User reached route via GET
    # (when the user accesses the registration page)
    else:
        return render_template('register.html')


@app.route('/rename', methods=['GET', 'POST'])
@login_required
def rename_category():
    """Change the name of a category."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        cat_list = get_values(db, 'categories', 'category', session['user_id'])

        # Check if the 'old_name' field is empty or wrong
        if (not request.form.get('old_name')
                or request.form.get('old_name').title() not in cat_list):
            return sorry('Must provide correct category name.')

        # Check if the 'new_name' field is empty or wrong
        if (not request.form.get('new_name')
                or request.form.get('new_name').title() in cat_list):
            return sorry('Must provide correct new category name.')

        # Update the category name
        db.execute(
            """
            UPDATE categories
               SET category = ?
             WHERE category = ?
            """,
            request.form.get('new_name').title(),
            request.form.get('old_name').title(),
        )

        # Show all categories
        return redirect('/categories')

    # User reached route via GET
    else:
        return redirect('/categories')


@app.route('/structure')
@login_required
def structure():
    """Generate pie chart."""

    # Query database to get categories of the logged-in user
    cat_list = get_values(db, 'categories', 'category', session['user_id'])

    # Query database to find the sum of expenses per each category
    plot_data = {}
    total = 0
    for category in cat_list:
        sums = db.execute(
            """
            SELECT SUM(expense) AS sum
              FROM expenses, categories
             WHERE expenses.category_id = categories.id
               AND expenses.user_id = categories.user_id
               AND expenses.user_id = ?
               AND year = ?
               AND category = ?
            """,
            session['user_id'],
            session['year'],
            category,
        )

        # Add sum of expenses to the dictionary by a category
        # (only one dict of sums in list)
        if sums[0]['sum']:
            plot_data[category] = sums[0]['sum']
            total += sums[0]['sum']

    # Check if user is using a mobile browser
    browser = request.user_agent
    browser = re.search('Mobile', str(browser))
    if browser != None:
        figsize = (4.6, 4.6)
        textprops = {'fontsize': 12, 'horizontalalignment': 'center'}
    else:
        figsize = (10, 10)
        textprops = {'fontsize': 16, 'horizontalalignment': 'center'}

    # When using Matplotlib in a web server it is strongly recommended
    # to not use pyplot
    # https://matplotlib.org/stable/gallery/user_interfaces/web_application_server_sgskip.html
    fig = Figure(figsize=figsize, dpi=72, layout='constrained')
    ax = fig.subplots()

    # Draw a pie chart
    _, labels, percentages = ax.pie(
        plot_data.values(),
        colors=sns.color_palette('crest'),
        labels=plot_data.keys(),
        autopct='%.2f%%',
        pctdistance=0.6,
        labeldistance=0.6,
        wedgeprops={'linewidth': 2.0, 'edgecolor': 'white'},
        textprops=textprops,
    )

    # Adjust labels' position
    for label, percentage in zip(labels, percentages):
        label.set_y(label.get_position()[1] + 0.1)
        percentage.set_y(percentage.get_position()[1] - 0.05)

    # Embed the chart into html template
    mpld3_plot = mpld3.fig_to_html(fig)

    return render_template(
        'pie_chart.html',
        mpld3_plot=mpld3_plot,
        years=session['years'],
        year=session['year'],
    )

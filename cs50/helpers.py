from flask import redirect, render_template, session
from functools import wraps

months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
]


def get_values(database, table, col, user_id, distinct=False):
    """Return sorted list of values from 'col' column of database."""

    # Check if user requested distinct values
    if distinct:
        column = f'DISTINCT({col})'
    else:
        column = col

    # Query database to get requested values of the logged-in user
    rows = database.execute(
            f"""
            SELECT {column}
              FROM {table}
             WHERE user_id = ?
            """,
            user_id,
    )

    # Ensure the list of values is sorted
    lst = []
    for value in rows:
        lst.append(value[col])
    return sorted(lst)


def login_required(f):
    """Decorator for login requirement.

    https://flask.palletsprojects.com/en/2.3.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def sorry(message, code=400):
    return render_template('sorry.html', message=message), code


def usd(value):
    """Format value as USD."""

    return f"${value:,.2f}"

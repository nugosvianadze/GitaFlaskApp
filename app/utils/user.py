from flask import flash, redirect, url_for


def find_and_validate_user(user):
    if not user:
        flash(f"User does not exist!")
        return redirect(url_for('get_users'))

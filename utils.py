from flask import flash, redirect, url_for


def find_and_validate_user(user, user_id: int):
    if not user:
        flash(f"User with id : {user_id} does not exist!")
        return redirect(url_for('get_users'))

from flask import render_template, redirect, Blueprint, session, url_for, flash, request

from app.extensions import db, bcrypt
from app.forms.user import UserProfileForm, UserUpdateForm, LoginForm, SignUpForm
from app.models.user import User, Profile
from app.utils.decorator import login_required
from app.utils.user import find_and_validate_user

user_bp = Blueprint("user", __name__, template_folder='user', url_prefix='/user')


@user_bp.route('/create_profile/<int:user_id>', methods=["GET", "POST"])
def create_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user)

    form = UserProfileForm()
    if request.method == "POST":
        if form.validate():
            bio = request.form.get('bio')
            # profile = Profile(bio=form.bio.data,
            #                   user_id=user_id)
            # db.session.add(profile)
            # db.session.commit()
            profile = Profile(bio=bio)
            user.profile = profile
            db.session.commit()
            flash('Profile Successfully Created!', 'success')
            return redirect(url_for('user.user_profile', user_id=user_id))
    return render_template('user/create_profile.html',
                           form=form, user=user)


@user_bp.route('/user_profile/<int:user_id>')
def user_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user)
    return render_template("user/profile.html", user=user)


@user_bp.route('/update_profile/<int:user_id>', methods=["POST", "GET"])
def update_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user)
    form = UserProfileForm(data={'bio': user.profile.bio})

    if request.method == 'POST':
        if form.validate():
            bio = request.form.get('bio')
            user.profile.bio = bio
            db.session.commit()
            flash('Profile Successfully Updated!', 'success')
            return redirect(url_for('user.user_profile', user_id=user_id))

    return render_template('user/edit_profile.html', form=form, user=user)


@user_bp.route('/delete_profile/<int:user_id>')
def delete_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user)
    if not user.profile:
        flash("User does not have profile")
        return redirect(url_for('user.get_users'))
    # db.session.delete(user.profile)
    user.profile = None
    db.session.commit()
    flash(f"user {user.username}'s profile successfully deleted!", "success")
    return redirect(url_for('user.user_profile', user_id=user_id))


@user_bp.route('/my_profile')
def my_profile():
    if 'email' not in session:
        return redirect(url_for('user.login'))
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    find_and_validate_user(user)

    return render_template('blog/user_posts.html', user=user)


@user_bp.route('/sign_out')
def sign_out():
    email = session.pop('email', None)
    return redirect(url_for('user.login'))


@user_bp.route('/users')
@login_required
def get_users():
    users = User.query.all()
    return render_template("user/users.html", user_list=users)


@user_bp.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id: int):
    form = UserUpdateForm()
    if form.validate_on_submit():
        roles = form.roles.data

        # roles_from_db = Role.query.filter(
        #     Role.title.in_(roles)
        # ).all()

        username = form.username.data
        user = User.query.get(user_id)
        if user:
            user.roles.clear()
            user.roles.extend(roles)
            user.username = username
            db.session.commit()
            flash(f'user successfully updated : {username}', 'success')
            return redirect(url_for('user.get_users'))
        flash(f'user with id {user_id} does not exist!')
        return redirect(url_for('user.get_users'))
    return redirect(url_for('user.get_users'))


@user_bp.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id: int):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        flash(f'user with id {user_id} successfully deleted!', 'success')
        return redirect(url_for('user.get_users'))
    flash(f'user with id {user_id} does not exists!')
    return redirect(url_for('user.get_users'))


@user_bp.route('/user_detail/<int:user_id>')
def user_detail(user_id: int):
    user_obj = User.query.get(user_id)
    if not user_obj:
        flash('user not found', 'error')
        return redirect(url_for('user.get_users'))
    update_form = UserUpdateForm(data={"roles": user_obj.roles})

    # user_obj = User.query.filter_by(id=user_id).first()
    return render_template('user/user_detail.html', user=user_obj, update_form=update_form)


@user_bp.route('/user_list')
def user_list():
    return redirect(url_for('user.user_detail', user_id=1))


@user_bp.route('/login', methods=["GET", "POST"])
def login(**kwargs):
    next_url = request.args.get('next')
    if 'email' in session:
        print(session.get('email'))
        flash("You already  Logged in!", "success")

        return redirect(url_for('blog.home'))

    form = LoginForm()
    if form.validate_on_submit():
        next_url = request.form.get('next')
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email Does Not Exist!')
            return render_template("user/login.html", form=form)
        if not user.authenticate(password, bcrypt):
            flash('Wrong Password! Try Again!')
            return render_template("user/login.html", form=form)
        session['email'] = email
        flash("You Have Successfully Logged in!", "success")
        if next_url:
            return redirect(next_url)
        return redirect(url_for('blog.home'))
    return render_template("user/login.html", form=form, next=next_url)


@user_bp.route('/sign-up', methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        form_email = form.email.data
        password = form.password.data
        existing_user = User.query.filter_by(email=form_email).first()
        # existing_user = User.query.filter(User.email == form_email).first()
        if existing_user:
            flash(f"user with email : {form_email}, already exists")
            return render_template("user/signup.html", form=form)
        pw_hash = User.hash_password(password, bcrypt)
        new_user = User(
            email=form_email,
            username=form.first_name.data + " " + form.last_name.data,
            address=form.address.data,
            password=pw_hash
        )
        db.session.add(new_user)
        db.session.commit()

        flash("You Have Successfully Signed up!", "success")
        return redirect(url_for("home"))
    print(form.errors, form.form_errors)
    return render_template("user/signup.html", form=form)

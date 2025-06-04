@app.route('/create_profile/<int:user_id>', methods=["GET", "POST"])
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
            return redirect(url_for('user_profile', user_id=user_id))
    return render_template('user/create_profile.html',
                           form=form, user=user)


@app.route('/user_profile/<int:user_id>')
def user_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user)
    return render_template("user/profile.html", user=user)


@app.route('/update_profile/<int:user_id>', methods=["POST", "GET"])
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
            return redirect(url_for('user_profile', user_id=user_id))

    return render_template('user/edit_profile.html', form=form, user=user)


@app.route('/delete_profile/<int:user_id>')
def delete_profile(user_id: int):
    user = User.query.get(user_id)
    find_and_validate_user(user)
    if not user.profile:
        flash("User does not have profile")
        return redirect(url_for('get_users'))
    # db.session.delete(user.profile)
    user.profile = None
    db.session.commit()
    flash(f"user {user.username}'s profile successfully deleted!", "success")
    return redirect(url_for('user_profile', user_id=user_id))


@app.route('/my_profile')
def my_profile():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    find_and_validate_user(user)

    return render_template('blog/user_posts.html', user=user)


@app.route('/sign_out')
def sign_out():
    email = session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/users')
def get_users():
    users = User.query.all()
    return render_template("user/users.html", user_list=users)


@app.route('/update_user/<int:user_id>', methods=['POST'])
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
            return redirect(url_for('get_users'))
        flash(f'user with id {user_id} does not exist!')
        return redirect(url_for('get_users'))
    return redirect(url_for('get_users'))


@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id: int):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        flash(f'user with id {user_id} successfully deleted!', 'success')
        return redirect(url_for('get_users'))
    flash(f'user with id {user_id} does not exists!')
    return redirect(url_for('get_users'))


@app.route('/user_detail/<int:user_id>')
def user_detail(user_id: int):
    user_obj = User.query.get(user_id)
    if not user_obj:
        flash('user not found', 'error')
        return redirect(url_for('get_users'))
    update_form = UserUpdateForm(data={"roles": user_obj.roles})

    # user_obj = User.query.filter_by(id=user_id).first()
    return render_template('user/user_detail.html', user=user_obj, update_form=update_form)


@app.route('/user_list')
def user_list():
    return redirect(url_for('user_detail', user_id=1))


@app.route('/login', methods=["GET", "POST"])
def login():
    if 'email' in session:
        print(session.get('email'))
        flash("You already  Logged in!", "success")

        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
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
        return redirect(url_for('home'))
    return render_template("user/login.html", form=form)


@app.route('/sign-up', methods=["GET", "POST"])
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
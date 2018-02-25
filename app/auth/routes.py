from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    allow_user_registration = current_app.config.get("ALLOW_USER_REGISTRATION", False)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/login.html",
                           title="Sign in",
                           form=form,
                           allow_user_registration=allow_user_registration)

@bp.route("/register", methods=["GET", "POST"])
def register():
    if not current_app.config.get("ALLOW_USER_REGISTRATION"):
        return abort(404)
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You are now registered !")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Register", form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))

from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    url_for,
    render_template)
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user)

from lib.safe_next_url import safe_next_url
from snakeeyes.blueprints.user.decorators import anonymous_required
from snakeeyes.blueprints.user.models import User
from snakeeyes.blueprints.user.forms import (
    LoginForm,
    BeginPasswordResetForm,
    PasswordResetForm,
    SignupForm,
    WelcomeForm,
    UpdateCredentials,
    AccountValidationForm)

user = Blueprint('user', __name__, template_folder='templates')


@user.route('/login', methods=['GET', 'POST'])
@anonymous_required()
def login():
    form = LoginForm(next=request.args.get('next'))

    if form.validate_on_submit():
        u = User.find_by_identity(request.form.get('identity'))

        if u and u.authenticated(password=request.form.get('password')):
            if login_user(u, remember=True) and u.is_active():
                u.update_activity_tracker(request.remote_addr)

                next_url = request.form.get('next')
                if next_url:
                    return redirect(safe_next_url(next_url))
                
                return redirect(url_for('user.settings'))

            else:
                flash('This account has been disabled.', 'error')

        else:
            flash('Identity or password incorrect', 'error')

    return render_template('user/login.html', form=form)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", 'success')
    return redirect(url_for('user.login'))


@user.route('/account/begin_password_reset', methods=['GET', 'POST'])
@anonymous_required()
def begin_password_reset():
    form = BeginPasswordResetForm()

    if form.validate_on_submit():
        u = User.initialize_password_reset(request.form.get('identity'))

        flash('An email has been sent to {0}.'.format(u.email), 'success')
        return redirect(url_for('user.login'))

    return render_template('user/begin_password_reset.html', form=form)


@user.route('/account/activate_account', methods=['GET', 'POST'])
@login_required
def activate_account():

    u = User.deserialize_token(request.args.get('validation_token'))
    if u is None:
        flash('Your activation link is not correct.', 'error')
        return redirect(url_for('user.settings'))
        
    u.verified = True
    u.save()
    flash('Your account has been verified!', 'success')
    return redirect(url_for('user.settings'))


@user.route('/account/send_activation_email')
@login_required
def send_activation_email():
    current_user.validate_account(current_user.email)
    flash("A confirmation email has been sent.", "success")
    return redirect(url_for('user.settings'))


@user.route('/account/password_reset', methods=['GET', 'POST'])
@anonymous_required()
def password_reset():
    form = PasswordResetForm(reset_token=request.args.get('reset_token'))

    if form.validate_on_submit():
        u = User.deserialize_token(request.form.get('reset_token'))

        if u is None:
            flash('Your reset token has expired or is not correct', 'error')
            return redirect(url_for('user.begin_password_reset'))

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        u.save()

    return render_template('user/password_reset.html', form=form)


@user.route('/signup', methods=['GET', 'POST'])
@anonymous_required()
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        u = User()

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        
        u.save()

        if login_user(u):
            flash('Thanks for signing up!', 'success')
            u.validate_account(request.form.get('email'))
            return redirect(url_for('user.welcome'))

        

    return render_template('user/signup.html', form=form) 




@user.route('/welcome', methods=['GET', 'POST'])
@login_required
def welcome():
    if current_user.username:
        flash('You already picked a username.', 'warning')
        return redirect(url_for('user.settings'))

    form = WelcomeForm()

    if form.validate_on_submit():
        current_user.username = request.form.get('username')
        current_user.save()

        flash('Sign up is complete, enjoy our services.', 'success')
        return redirect(url_for('user.settings'))

    return render_template('user/welcome.html', form=form)

@user.route('/settings')
@login_required
def settings():
    return render_template('user/settings.html')


@user.route('/settings/update_credentials', methods=['GET', 'POST'])
@login_required
def update_credentials():
    form = UpdateCredentials(current_user, uid=current_user.id)

    if form.validate_on_submit():
        new_password = request.form.get('password', '')
        current_user.email = request.form.get('email')

        if new_password:
            current_user.password = User.encrypt_password(new_password)

        current_user.save()

        flash('Your sign in settings have been updated.', 'success')
        return redirect(url_for('user.settings'))

    return render_template('user/update_credentials.html', form=form)



from app import db
from app.settings import bp
from flask import render_template, flash, redirect, url_for, request, send_file, current_app, g
from flask_login import current_user, login_required
from app.settings.forms import *

@login_required
@bp.route('/general')
def general():
    return render_template('settings/general.html', title='Settings - General')

@login_required
@bp.route('/appearance')
def appearance():
    return render_template('settings/appearance.html', title='Settings - Appearance')

@login_required
@bp.route('/blog')
def blog():
    return render_template('settings/blog.html', title='Settings - Blog')

@login_required
@bp.route('/privacy')
def privacy():
    return render_template('settings/privacy.html', title='Settings - Privacy')

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        img = form.my_avatar.data[21:]
        f = bytes(img, encoding="ascii")
        if (f is None):
            pass
        else:
            utils.convert_and_save(f, os.path.join(current_app.config["UPLOADS"], 'avatars', f"{current_user.id}.png"))
            current_user.hasavatar = 1
            flash(f"Your avatar has been submitted.", 'primary')
        if form.noavatar.data:
            current_user.hasavatar = 0
            flash(f"Your avatar has been deleted.", 'primary')
        db.session.commit()
        flash('Your changes have been saved.', 'primary')
        return redirect(url_for('main.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('settings/edit_profile.html', title='Edit Profile', form=form)
from app import db
from app.blog import bp
from flask import render_template, flash, redirect, url_for, request, send_file, current_app, g
from flask_login import current_user, login_required

@login_required
@bp.route('/title')
def title():
    return render_template('blog/title.html', title='Title')

@login_required
@bp.route('/toc')
def toc():
    return render_template('blog/toc.html', title='ToC')

@login_required
@bp.route('/editor')
def editor():
    return render_template('blog/editor.html', title='Editor')
from app import db
from app.main import bp
import json
from app.miscutil import utils
from flask import render_template, flash, redirect, url_for, request, send_file, current_app, g
from app.main.forms import *
from flask_login import current_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
import os


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if request.method == 'POST':
        form.validate()
        for error in form.post.errors:
            flash(error,'danger')
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!', 'primary')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('explore.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    toppage = request.args.get('toppage', 1, type=int)
    recentpage = request.args.get('recentpage', 1, type=int)
    topposts = user.posts.order_by(Post.rating.desc()).paginate(toppage, current_app.config['POSTS_PER_PAGE_USERS'], False)
    recentposts = user.posts.order_by(Post.timestamp.desc()).paginate(recentpage, current_app.config['POSTS_PER_PAGE_USERS'], False)
    next_topurl = url_for('main.index', username=user.username, page=topposts.next_num) if topposts.has_next else None
    prev_topurl = url_for('main.index', username=user.username, page=topposts.prev_num) if topposts.has_prev else None
    next_recenturl = url_for('main.index', page=recentposts.next_num) if recentposts.has_next else None
    prev_recenturl = url_for('main.index', page=recentposts.prev_num) if recentposts.has_prev else None
    return render_template('user.html', user=user, recentposts=recentposts.items, topposts = topposts.items, next_topurl=next_topurl, prev_topurl=prev_topurl, next_recenturl=next_recenturl, prev_recenturl=prev_recenturl, avatar=True)

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
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found.", 'info')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash("You can't follow yourself", 'info')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"You are following {username}!", 'primary')
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found.", 'info')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!', 'info')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You are not following {username}.", 'primary')
    return redirect(url_for('main.user', username=username))    

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', posts=posts, next_url=next_url, prev_url=prev_url, total=total, page=page)

@bp.route('/vote/<post>', methods=['POST','GET'])
@login_required
def vote(post):
    post=int(post)
    if request.form['newState[starred]']=='true':
        status=1
    else:
        status=0
    if request.form['newState[upvoted]']=='true':
        current_user.vote(post,1,status)
    elif request.form['newState[downvoted]']=='true':
        current_user.vote(post,-1,status)
    else:
        current_user.vote(post,0,status)
    return ""
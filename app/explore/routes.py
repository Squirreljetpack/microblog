from app import db
from app.explore import bp
from flask import render_template, flash, redirect, url_for, request, send_file, current_app, g
from flask_login import current_user, login_required
from app.models import User, Post

@login_required
@bp.route('/feed')
def feed():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('explore/feed.html', title='Feed', posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/blogs')
def blogs():
    return render_template('explore/blogs.html', title='Blogs')

@bp.route('/news')
def news():
    return render_template('explore/news.html', title='News')
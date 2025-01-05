from flask import Flask, render_template, request, redirect, url_for, abort, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Ken14918@localhost/blog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# SpaceMembers association table
space_members = db.Table('space_members',
    db.Column('space_id', db.Integer, db.ForeignKey('space.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_photo = db.Column(db.String(150), nullable=True)
    followed = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy='dynamic')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy='dynamic')
    channels = db.relationship('Channel', backref='owner', lazy=True)
    comments = db.relationship('Comment', backref='commenter', lazy=True)
    likes = db.relationship('Like', backref='liker', lazy=True)
    subscriptions = db.relationship('Subscription', foreign_keys='Subscription.subscriber_user_id', backref='subscriber', lazy='dynamic')
    owned_spaces = db.relationship('Space', backref='owner', lazy=True)
    member_spaces = db.relationship('Space', secondary=space_members, backref=db.backref('members', lazy='dynamic'))

# Channel model
class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    subscriber_count = db.Column(db.Integer, default=0)
    videos = db.relationship('Video', backref='channel', lazy=True)

# Space model
class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

# Video model
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    upload_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    views = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer, nullable=False)
    comments = db.relationship('Comment', backref='video', lazy=True)
    likes = db.relationship('Like', backref='video', lazy=True)
    tags = db.relationship('Tag', secondary='video_tag', backref=db.backref('videos', lazy='dynamic'))

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    comment_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

# Like model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    like_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

# Subscription model
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscriber_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_user_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    subscription_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

# Tag model
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50), unique=True, nullable=False)

# VideoTag model
class VideoTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)

# Category model
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    videos = db.relationship('Video', backref='category', lazy=True)

# Follow model
class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(150), nullable=True)
    video_file = db.Column(db.String(150), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create the database tables
with app.app_context():
    db.create_all()

def save_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return filename

@app.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("landing.html")

@app.route("/home")
@login_required
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template("home.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        try:
            title = request.form["title"]
            content = request.form["content"]
            capture_image = request.files.get("capture_image")
            capture_video = request.files.get("capture_video")
            image_filename = save_file(capture_image) if capture_image and capture_image.filename != '' else None
            video_filename = save_file(capture_video) if capture_video and capture_video.filename != '' else None
            post = Post(
                title=title,
                content=content,
                image_file=image_filename,
                video_file=video_filename,
                user_id=current_user.id
            )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('post', post_id=post.id))
        except KeyError as e:
            flash(f"Missing form field: {e.args[0]}", "danger")
            return redirect(url_for('new_post'))
    return render_template("new_post.html")

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)

@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        capture_image = request.files.get("capture_image")
        capture_video = request.files.get("capture_video")
        if capture_image and capture_image.filename != '':
            post.image_file = save_file(capture_image)
        if capture_video and capture_video.filename != '':
            post.video_file = save_file(capture_video)
        db.session.commit()
        return redirect(url_for("post", post_id=post.id))
    return render_template("edit_post.html", post=post)

@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Login unsuccessful. Please check email and password", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/feed')
@login_required
def feed():
    user_tags = [tag.id for tag in current_user.followed_tags]
    posts = Post.query.filter(Post.tags.any(Tag.id.in_(user_tags))).all()
    return render_template('feed.html', posts=posts)

@app.route('/post/<int:post_id>/upvote', methods=['POST'])
@login_required
def upvote_post(post_id):
    post = Post.query.get_or_404(post_id)
    vote = Vote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if vote:
        if vote.vote_type == 'upvote':
            db.session.delete(vote)
            post.upvotes = (post.upvotes or 0) - 1
        else:
            vote.vote_type = 'upvote'
            post.upvotes = (post.upvotes or 0) + 1
            post.downvotes = (post.downvotes or 0) - 1
    else:
        new_vote = Vote(user_id=current_user.id, post_id=post_id, vote_type='upvote')
        db.session.add(new_vote)
        post.upvotes = (post.upvotes or 0) + 1
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))

@app.route('/post/<int:post_id>/downvote', methods=['POST'])
@login_required
def downvote_post(post_id):
    post = Post.query.get_or_404(post_id)
    vote = Vote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if vote:
        if vote.vote_type == 'downvote':
            db.session.delete(vote)
            post.downvotes = (post.downvotes or 0) - 1
        else:
            vote.vote_type = 'downvote'
            post.downvotes = (post.downvotes or 0) + 1
            post.upvotes = (post.upvotes or 0) - 1
    else:
        new_vote = Vote(user_id=current_user.id, post_id=post_id, vote_type='downvote')
        db.session.add(new_vote)
        post.downvotes = (post.downvotes or 0) + 1
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))

@app.route("/user/<int:user_id>")
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("user_profile.html", user=user)

@app.route("/update_account", methods=["GET", "POST"])
@login_required
def update_account():
    if request.method == "POST":
        current_user.username = request.form["username"]
        current_user.email = request.form["email"]
        if request.form["password"]:
            current_user.password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
        profile_photo = request.files.get("profile_photo")
        if profile_photo and profile_photo.filename != '':
            current_user.profile_photo = save_file(profile_photo)
        db.session.commit()
        flash("Account updated successfully!", "success")
        return redirect(url_for("user_profile", user_id=current_user.id))
    return render_template("update_account.html")

@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = User.query.get_or_404(current_user.id)
    # Delete related votes first
    Vote.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash("Account deleted successfully!", "success")
    return redirect(url_for("home"))

@app.route("/create_channel", methods=["GET", "POST"])
@login_required
def create_channel():
    if request.method == "POST":
        name = request.form["name"]
        channel = Channel(name=name, user_id=current_user.id)
        db.session.add(channel)
        db.session.commit()
        flash("Channel created successfully!", "success")
        return redirect(url_for("home"))
    return render_template("create_channel.html")

@app.route("/create_space", methods=["GET", "POST"])
@login_required
def create_space():
    if request.method == "POST":
        name = request.form["name"]
        existing_space = Space.query.filter_by(name=name).first()
        if existing_space:
            flash("A space with this name already exists. Please choose a different name.", "danger")
            return redirect(url_for("create_space"))
        space = Space(name=name, user_id=current_user.id)
        db.session.add(space)
        db.session.commit()
        flash("Space created successfully!", "success")
        return redirect(url_for("home"))
    return render_template("create_space.html")

@app.route("/spaces")
@login_required
def spaces():
    user_spaces = current_user.member_spaces
    return render_template("spaces.html", spaces=user_spaces)

@app.route("/following")
@login_required
def following():
    # Fetch the posts from the users that the current user is following
    followed_users = [follow.followed_id for follow in current_user.followed]
    if followed_users:
        posts = Post.query.filter(Post.user_id.in_(followed_users)).all()
    else:
        posts = []
    return render_template("following.html", posts=posts)

@app.route("/channel/<int:channel_id>")
@login_required
def view_channel(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    return render_template("view_channel.html", channel=channel)

@app.route("/space/<int:space_id>")
@login_required
def view_space(space_id):
    space = Space.query.get_or_404(space_id)
    return render_template("view_space.html", space=space)

if __name__ == "__main__":
    app.run(debug=True)

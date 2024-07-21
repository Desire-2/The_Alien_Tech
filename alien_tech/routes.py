from flask import render_template, url_for, flash, redirect, request, current_app, abort, Blueprint
from datetime import datetime
from alien_tech import app, db, bcrypt
from alien_tech.ai_scoring import ai_project_scoring
from alien_tech.forms import (RegistrationForm, LoginForm, CourseForm, UpdateProfileForm,
                              ModuleForm, LessonForm, UpdateProfileForm, QuizForm, QuestionForm,
                              OptionForm, DiscussionForm, CommentForm, MessageForm, LiveClassForm,
                              ReviewForm, ForumForm, ForumPostForm, ResetPasswordForm)
from alien_tech.models import (User, Course, Enrollment, Module, Lesson, Quiz, Question, Option, Discussion, Comment,
                               Certificate, Progress, UserBadge, Message, LiveClass, Review, Forum, ForumPost,
                               Achievement, ProjectSubmission, UserAchievement, Project, Submission, MentorRequest, Prerequisite,
                               Notification, Feedback, Ticket, Analytics, UserBadge,
                               UserAchievement, BlogPost, Prerequisite, Notification, Feedback, Ticket,
                               Analytics, AIScoreReview, ProjectTracking)
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from functools import wraps
import os
import subprocess
import secrets
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from alien_tech.admin import UserModelView, ProjectModelView
from mailchimp3 import MailChimp
from github import Github

main = Blueprint('main', __name__)

client = MailChimp(mc_user='bikorimanadesire5@gmail.com', mc_api='445150415d6eee758e2fa1e775aa89b1-us13')


admin = Admin(app, name='Admin Dashboard', template_mode='bootstrap3')
admin.add_view(UserModelView(User, db.session))
admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Module, db.session))
admin.add_view(ModelView(Lesson, db.session))
admin.add_view(ModelView(Quiz, db.session))
admin.add_view(ModelView(Question, db.session))
admin.add_view(ModelView(Option, db.session))
admin.add_view(ModelView(LiveClass, db.session))
admin.add_view(ModelView(Review, db.session))
admin.add_view(ModelView(Forum, db.session))
admin.add_view(ModelView(ForumPost, db.session))
admin.add_view(ModelView(Achievement, db.session))
admin.add_view(ModelView(UserAchievement, db.session))
admin.add_view(ModelView(Project, db.session))

@app.route("/")
@app.route("/home")
def home():
    courses = Course.query.all()
    return render_template('home.html', courses=courses)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/course/<int:course_id>")
def course(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course.html', title=course.title, course=course)

@app.route("/courses")
def courses():
    courses = Course.query.all()
    return render_template('courses.html', title='Courses', courses=courses)

@app.route("/course/new", methods=['GET', 'POST'])
@login_required
def new_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(course)
        db.session.commit()
        flash('Your course has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_course.html', title='New Course', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.profile.bio = form.bio.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.profile.bio
    image_file = url_for('static', filename='profile_pics/' + current_user.profile.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/course/<int:course_id>/module/new", methods=['GET', 'POST'])
@login_required
def new_module(course_id):
    form = ModuleForm()
    if form.validate_on_submit():
        module = Module(title=form.title.data, content=form.content.data, course_id=course_id)
        db.session.add(module)
        db.session.commit()
        flash('Your module has been created!', 'success')
        return redirect(url_for('course', course_id=course_id))
    return render_template('create_module.html', title='New Module', form=form)

@app.route("/module/<int:module_id>/lesson/new", methods=['GET', 'POST'])
@login_required
def new_lesson(module_id):
    form = LessonForm()
    if form.validate_on_submit():
        lesson = Lesson(title=form.title.data, content=form.content.data, module_id=module_id)
        db.session.add(lesson)
        db.session.commit()
        flash('Your lesson has been created!', 'success')
        return redirect(url_for('module', module_id=module_id))
    return render_template('create_lesson.html', title='New Lesson', form=form)

@app.route("/course/<int:course_id>/quiz/new", methods=['GET', 'POST'])
@login_required
def new_quiz(course_id):
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(title=form.title.data, course_id=course_id)
        db.session.add(quiz)
        db.session.commit()
        flash('Your quiz has been created!', 'success')
        return redirect(url_for('course', course_id=course_id))
    return render_template('create_quiz.html', title='New Quiz', form=form)

@app.route("/quiz/<int:quiz_id>/question/new", methods=['GET', 'POST'])
@login_required
def new_question(quiz_id):
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(content=form.content.data, quiz_id=quiz_id)
        db.session.add(question)
        db.session.commit()
        flash('Your question has been added!', 'success')
        return redirect(url_for('quiz', quiz_id=quiz_id))
    return render_template('create_question.html', title='New Question', form=form)

@app.route("/question/<int:question_id>/option/new", methods=['GET', 'POST'])
@login_required
def new_option(question_id):
    form = OptionForm()
    if form.validate_on_submit():
        option = Option(content=form.content.data, correct=form.correct.data, question_id=question_id)
        db.session.add(option)
        db.session.commit()
        flash('Your option has been added!', 'success')
        return redirect(url_for('question', question_id=question_id))
    return render_template('create_option.html', title='New Option', form=form)

@app.route("/course/<int:course_id>/discussion/new", methods=['GET', 'POST'])
@login_required
def new_discussion(course_id):
    form = DiscussionForm()
    if form.validate_on_submit():
        discussion = Discussion(content=form.content.data, user_id=current_user.id, course_id=course_id)
        db.session.add(discussion)
        db.session.commit()
        flash('Your discussion has been created!', 'success')
        return redirect(url_for('course', course_id=course_id))
    return render_template('create_discussion.html', title='New Discussion', form=form)

@app.route("/discussion")
def discussions():
    discussions = Discussion.query.all()
    return render_template('discussions.html', title='Discussions', discussions=discussions)

@app.route("/discussion/<int:discussion_id>/comment/new", methods=['GET', 'POST'])
@login_required
def new_comment(discussion_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, user_id=current_user.id, discussion_id=discussion_id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('discussion', discussion_id=discussion_id))
    return render_template('create_comment.html', title='New Comment', form=form)

@app.route("/course/<int:course_id>/certificate")
@login_required
def issue_certificate(course_id):
    certificate = Certificate(user_id=current_user.id, course_id=course_id)
    db.session.add(certificate)
    db.session.commit()
    flash('Your certificate has been issued!', 'success')
    return redirect(url_for('course', course_id=course_id))

@app.route("/certificates")
@login_required
def certificates():
    certificates = Certificate.query.filter_by(user_id=current_user.id).all()
    return render_template('certificates.html', title='Certificates', certificates=certificates)

@app.route("/course/<int:course_id>/progress")
@login_required
def course_progress(course_id):
    progress = Progress.query.filter_by(user_id=current_user.id, course_id=course_id).all()
    return render_template('course_progress.html', title='Course Progress', progress=progress)

@app.route("/lesson/<int:lesson_id>/complete")
@login_required
def complete_lesson(lesson_id):
    progress = Progress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if not progress:
        progress = Progress(user_id=current_user.id, lesson_id=lesson_id, completed=True, date_completed=datetime.utcnow())
        db.session.add(progress)
    else:
        progress.completed = True
        progress.date_completed = datetime.utcnow()
    db.session.commit()
    flash('Lesson marked as completed!', 'success')
    return redirect(url_for('lesson', lesson_id=lesson_id))

@app.route('/badges', methods=['GET'])
@login_required
def badges():
    user_badges = UserBadge.query.filter_by(user_id=current_user.id).all()
    return render_template('badges.html', user_badges=user_badges)

@app.route("/send_message", methods=['GET', 'POST'])
@login_required
def send_message():
    form = MessageForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(username=form.recipient.data).first()
        if recipient:
            msg = Message(author=current_user, recipient=recipient, body=form.body.data)
            db.session.add(msg)
            db.session.commit()
            flash('Your message has been sent!', 'success')
            return redirect(url_for('messages'))
        else:
            flash('User not found!', 'danger')
    return render_template('send_message.html', title='Send Message', form=form)

@app.route("/messages")
@login_required
def messages():
    received_messages = current_user.messages_received.order_by(Message.timestamp.desc()).all()
    sent_messages = current_user.messages_sent.order_by(Message.timestamp.desc()).all()
    return render_template('messages.html', title='Messages', received_messages=received_messages, sent_messages=sent_messages)

@app.route("/course/<int:course_id>/live_class/new", methods=['GET', 'POST'])
@login_required
def new_live_class(course_id):
    form = LiveClassForm()
    if form.validate_on_submit():
        live_class = LiveClass(
            title=form.title.data, 
            description=form.description.data,
            date_scheduled=form.date_scheduled.data,
            instructor_id=current_user.id,
            course_id=course_id,
            link=form.link.data
        )
        db.session.add(live_class)
        db.session.commit()
        flash('Live class scheduled!', 'success')
        return redirect(url_for('course', course_id=course_id))
    return render_template('create_live_class.html', title='Schedule Live Class', form=form)

@app.route("/live_classes")
@login_required
def live_classes():
    live_classes = LiveClass.query.all()
    return render_template('live_classes.html', title='Live Classes', live_classes=live_classes)

@app.route("/course/<int:course_id>/review/new", methods=['GET', 'POST'])
@login_required
def new_review(course_id):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            content=form.content.data,
            rating=form.rating.data,
            user_id=current_user.id,
            course_id=course_id
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been posted!', 'success')
        return redirect(url_for('course', course_id=course_id))
    return render_template('create_review.html', title='New Review', form=form)

@app.route("/forum/new", methods=['GET', 'POST'])
@login_required
def new_forum():
    form = ForumForm()
    if form.validate_on_submit():
        forum = Forum(
            title=form.title.data,
            description=form.description.data
        )
        db.session.add(forum)
        db.session.commit()
        flash('Forum created!', 'success')
        return redirect(url_for('forums'))
    return render_template('create_forum.html', title='New Forum', form=form)

@app.route("/forums")
@login_required
def forums():
    forums = Forum.query.all()
    return render_template('forums.html', title='Forums', forums=forums)

@app.route("/forum/<int:forum_id>")
@login_required
def forum(forum_id):
    forum = Forum.query.get_or_404(forum_id)
    posts = ForumPost.query.filter_by(forum_id=forum_id).all()
    form = ForumPostForm()
    return render_template('forum.html', title=forum.title, forum=forum, posts=posts, form=form)

@app.route("/forum/<int:forum_id>/post", methods=['POST'])
@login_required
def new_forum_post(forum_id):
    form = ForumPostForm()
    if form.validate_on_submit():
        post = ForumPost(
            content=form.content.data,
            user_id=current_user.id,
            forum_id=forum_id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created!', 'success')
        return redirect(url_for('forum', forum_id=forum_id))
    return redirect(url_for('forum', forum_id=forum_id))
@app.route("/recommendations")
@login_required
def recommendations():
    user_courses = [enrollment.course_id for enrollment in current_user.enrollments]
    recommended_courses = Course.query.filter(Course.id.notin_(user_courses)).all()
    return render_template('recommendations.html', title='Recommendations', recommended_courses=recommended_courses)

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.points.desc()).limit(10).all()
    return render_template('leaderboard.html', users=users)

@app.route('/achievements')
@login_required
def achievements():
    user_achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
    all_achievements = Achievement.query.all()
    return render_template('achievements.html', user_achievements=user_achievements, all_achievements=all_achievements)


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin_dashboard.html', title='Admin Dashboard')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        widgets = request.form.getlist('widgets')
        current_user.update_dashboard(widgets)
        flash('Dashboard updated', 'success')
        return redirect(url_for('dashboard'))
    available_widgets = ['courses', 'quizzes', 'progress', 'messages', 'certificates']
    return render_template('dashboard.html', available_widgets=available_widgets)

@app.route('/admin/bulk_user_update', methods=['GET', 'POST'])
@login_required
def bulk_user_update():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        user_ids = request.form.getlist('user_ids')
        action = request.form.get('action')
        for user_id in user_ids:
            user = User.query.get(user_id)
            if action == 'deactivate':
                user.is_active = False
            elif action == 'activate':
                user.is_active = True
            db.session.commit()
        flash('Users updated successfully', 'success')
        return redirect(url_for('bulk_user_update'))
    users = User.query.all()
    return render_template('admin/bulk_user_update.html', users=users)

@app.route('/admin/bulk_course_update', methods=['GET', 'POST'])
@login_required
def bulk_course_update():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        course_ids = request.form.getlist('course_ids')
        action = request.form.get('action')
        for course_id in course_ids:
            course = Course.query.get(course_id)
            if action == 'deactivate':
                course.is_active = False
            elif action == 'activate':
                course.is_active = True
            db.session.commit()
        flash('Courses updated successfully', 'success')
        return redirect(url_for('bulk_course_update'))
    courses = Course.query.all()
    return render_template('admin/bulk_course_update.html', courses=courses)

@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/notification/read/<int:notification_id>')
@login_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.read = True
    db.session.commit()
    return redirect(url_for('notifications'))


@app.route('/admin/blog', methods=['GET', 'POST'])
@login_required
def manage_blog():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        blog_post = BlogPost(title=title, content=content, author_id=current_user.id)
        db.session.add(blog_post)
        db.session.commit()
        flash('Blog post created successfully', 'success')
        return redirect(url_for('manage_blog'))
    blog_posts = BlogPost.query.all()
    return render_template('admin/manage_blog.html', blog_posts=blog_posts)

@app.route('/admin/blog/<int:id>/delete', methods=['POST'])
@login_required
def delete_blog_post(id):
    if not current_user.is_admin:
        abort(403)
    blog_post = BlogPost.query.get_or_404(id)
    db.session.delete(blog_post)
    db.session.commit()
    flash('Blog post deleted successfully', 'success')
    return redirect(url_for('manage_blog'))

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        content = request.form['content']
        feedback = Feedback(content=content, user_id=current_user.id)
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback submitted successfully', 'success')
        return redirect(url_for('feedback'))
    feedbacks = Feedback.query.all()
    return render_template('feedback.html', feedbacks=feedbacks)

@app.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    if request.method == 'POST':
        subject = request.form['subject']
        content = request.form['content']
        ticket = Ticket(subject=subject, content=content, user_id=current_user.id)
        db.session.add(ticket)
        db.session.commit()
        flash('Support ticket created successfully', 'success')
        return redirect(url_for('support'))
    tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template('support.html', tickets=tickets)

@app.route('/admin/support', methods=['GET'])
@login_required
def manage_support():
    if not current_user.is_admin:
        abort(403)
    tickets = Ticket.query.all()
    return render_template('admin/manage_support.html', tickets=tickets)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    client.lists.members.create('your_list_id', {
        'email_address': email,
        'status': 'subscribed',
    })
    flash('Subscribed successfully', 'success')
    return redirect(url_for('home'))

@app.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)
    prerequisites = Prerequisite.query.filter_by(course_id=course_id).all()
    for prereq in prerequisites:
        if not Enrollment.query.filter_by(user_id=current_user.id, course_id=prereq.prerequisite_id).first():
            flash('You must complete all prerequisites before enrolling', 'danger')
            return redirect(url_for('course_detail', course_id=course_id))
    enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    flash('Enrolled successfully', 'success')
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/share/<string:platform>/<int:course_id>', methods=['GET'])
@login_required
def share(platform, course_id):
    course = Course.query.get_or_404(course_id)
    if platform == 'twitter':
        url = f'https://twitter.com/intent/tweet?text=I%20just%20enrolled%20in%20{course.title}%20on%20The%20Alien%20Tech!&url={url_for("course_detail", course_id=course.id, _external=True)}'
    elif platform == 'facebook':
        url = f'https://www.facebook.com/sharer/sharer.php?u={url_for("course_detail", course_id=course.id, _external=True)}'
    return redirect(url)

@app.route('/projects', methods=['GET'])
@login_required
def projects():
    projects = Project.query.filter(Project.end_date > datetime.utcnow()).all()
    return render_template('projects.html', projects=projects)

@app.route('/project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        submission_url = request.form['submission_url']
        submission = Submission(user_id=current_user.id, project_id=project.id, submission_url=submission_url)
        db.session.add(submission)
        db.session.commit()
        flash('Project submitted successfully', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    return render_template('project_detail.html', project=project)

@app.route('/admin/projects', methods=['GET', 'POST'])
@admin_required
def manage_projects():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        project = Project(title=title, description=description, start_time=start_time, end_time=end_time)
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully', 'success')
        return redirect(url_for('manage_projects'))
    projects = Project.query.all()
    return render_template('manage_projects.html', projects=projects)

@app.route('/project/<int:project_id>/submit', methods=['POST'])
@login_required
def submit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if datetime.utcnow() > project.end_time:
        flash('Submission period has ended', 'danger')
        return redirect(url_for('project_details', project_id=project_id))
    repo_url = request.form['repo_url']
    # Implement AI scoring logic
    score, details, suggestions = ai_project_scoring.score_and_suggest(repo_url)
    submission = ProjectSubmission(project_id=project.id, user_id=current_user.id, repo_url=repo_url, score=score, details=details, suggestions=suggestions)
    db.session.add(submission)
    db.session.commit()
    flash('Project submitted successfully', 'success')
    return redirect(url_for('project_details', project_id=project_id))


@app.route('/admin/project/<int:project_id>/submissions', methods=['GET'])
@login_required
def view_submissions(project_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('home'))
    project = Project.query.get_or_404(project_id)
    submissions = Submission.query.filter_by(project_id=project_id).all()
    return render_template('view_submissions.html', project=project, submissions=submissions)

@app.route('/admin/submission/<int:submission_id>/score', methods=['POST'])
@login_required
def score_submission(submission_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('home'))
    submission = Submission.query.get_or_404(submission_id)
    submission.score = request.form['score']
    submission.feedback = request.form['feedback']
    db.session.commit()
    flash('Submission scored successfully', 'success')
    return redirect(url_for('view_submissions', project_id=submission.project_id))

@app.route('/project_templates')
@login_required
def project_templates():
    templates = [
        {"title": "Web Development Starter Kit", "url": "/static/templates/web_dev_starter_kit.zip"},
        {"title": "Data Science Project Template", "url": "/static/templates/data_science_template.zip"},
        {"title": "Machine Learning Starter Pack", "url": "/static/templates/ml_starter_pack.zip"}
    ]
    return render_template('project_templates.html', templates=templates)


@app.route('/admin/analytics')
@login_required
def analytics_dashboard():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('home'))
    analytics_data = Analytics.query.all()
    return render_template('admin/analytics.html', analytics_data=analytics_data)

@app.route('/project/<int:project_id>/request_mentor', methods=['GET', 'POST'])
@login_required
def request_mentor(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        mentor_id = request.form['mentor_id']
        mentor_request = MentorRequest(user_id=current_user.id, project_id=project.id, mentor_id=mentor_id)
        db.session.add(mentor_request)
        db.session.commit()
        flash('Mentor request sent successfully', 'success')
        return redirect(url_for('project_details', project_id=project_id))
    mentors = User.query.filter_by(is_mentor=True).all()
    return render_template('request_mentor.html', project=project, mentors=mentors)

@app.route('/submission/<int:submission_id>/review_ai_score', methods=['GET', 'POST'])
@login_required
def review_ai_score(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    if request.method == 'POST':
        feedback = request.form['feedback']
        ai_score_review = AIScoreReview(submission_id=submission.id, user_id=current_user.id, feedback=feedback)
        db.session.add(ai_score_review)
        db.session.commit()
        flash('AI score review submitted successfully', 'success')
        return redirect(url_for('submission_details', submission_id=submission_id))
    return render_template('review_ai_score.html', submission=submission)

@app.route('/project/<int:project_id>/live_editor', methods=['GET', 'POST'])
@login_required
def live_editor(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        code = request.form['code']
        # Save the code to the user's submission (in the database or a file)
        submission = Submission(user_id=current_user.id, project_id=project_id, code=code)
        db.session.add(submission)
        db.session.commit()
        flash('Code submitted successfully', 'success')
        return redirect(url_for('project_details', project_id=project_id))
    return render_template('live_editor.html', project=project)

def push_to_github(code, repo_name):
    g = Github("your_github_token")
    user = g.get_user()
    repo = user.create_repo(repo_name)
    repo.create_file("main.py", "Initial commit", code)
    return repo.clone_url

@app.route('/project/<int:project_id>/submit_code', methods=['POST'])
@login_required
def submit_code(project_id):
    code = request.form['code']
    repo_name = f"{current_user.username}_project_{project_id}"
    github_url = push_to_github(code, repo_name)
    submission = Submission(user_id=current_user.id, project_id=project_id, submission_url=github_url)
    db.session.add(submission)
    db.session.commit()
    flash('Code pushed to GitHub and submitted successfully', 'success')
    return redirect(url_for('project_details', project_id=project_id))

@app.route('/admin/ai_score/<int:submission_id>', methods=['POST'])
@login_required
def ai_score_submission(submission_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('home'))
    submission = Submission.query.get_or_404(submission_id)
    score, suggestions = ai_project_scoring.score_and_suggest(submission.submission_url)
    submission.score = score
    submission.feedback = suggestions
    db.session.commit()
    flash('Submission scored using AI successfully', 'success')
    return redirect(url_for('view_submissions', project_id=submission.project_id))

@app.route('/project/<int:project_id>/collaborate', methods=['GET', 'POST'])
@login_required
def collaborate(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        collaborators = request.form.getlist('collaborators')
        for collaborator_id in collaborators:
            collaborator = User.query.get(collaborator_id)
            # Logic to add collaborator to the project repository
            add_collaborator_to_repo(project.repo_url, collaborator.github_username)
        flash('Collaborators added successfully', 'success')
        return redirect(url_for('project_details', project_id=project_id))
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('collaborate.html', project=project, users=users)

@app.route('/project/<int:project_id>/track', methods=['GET', 'POST'])
@login_required
def track_project(project_id):
    project = Project.query.get_or_404(project_id)
    tracking = ProjectTracking.query.filter_by(project_id=project.id, user_id=current_user.id).first()
    if request.method == 'POST':
        progress = request.form['progress']
        if tracking:
            tracking.progress = progress
            tracking.last_updated = datetime.utcnow()
        else:
            new_tracking = ProjectTracking(project_id=project.id, user_id=current_user.id, progress=progress)
            db.session.add(new_tracking)
        db.session.commit()
        flash('Project progress updated', 'success')
        return redirect(url_for('project_details', project_id=project_id))
    return render_template('track_project.html', project=project, tracking=tracking)

@app.route('/project/<int:project_id>/run_code', methods=['POST'])
@login_required
def run_code(project_id):
    code = request.form['code']
    language = request.form['language']  # e.g., 'python'
    logs = docker_manager.run_code(code, language)
    return render_template('run_code.html', logs=logs)

@app.route('/project/<int:project_id>/live_code_editor', methods=['GET', 'POST'])
@login_required
def live_code_editor(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        code = request.form['code']
        logs = docker_manager.run_code(code, 'python')
        # Push the code to GitHub
        push_code_to_github(project.repo_url, code)
        return render_template('live_code_editor.html', project=project, code=code, logs=logs)
    return render_template('live_code_editor.html', project=project)

def push_code_to_github(repo_url, code):
    # Clone the repo, update the code, commit, and push back
    subprocess.run(["git", "clone", repo_url, "repo"])
    with open("repo/main.py", "w") as f:
        f.write(code)
    subprocess.run(["git", "-C", "repo", "add", "main.py"])
    subprocess.run(["git", "-C", "repo", "commit", "-m", "Updated code from live code editor"])
    subprocess.run(["git", "-C", "repo", "push"])
    subprocess.run(["rm", "-rf", "repo"])
    
@app.route("/user/<username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html', user=user)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been reset!', 'success')
            return redirect(url_for('login'))
        else:
            flash('No account found with that email.', 'danger')
    return render_template('reset_password.html', title='Reset Password', form=form)
@app.route('/quizzes')
def quizzes():
    # logic to retrieve and display quizzes
    return render_template('quizzes.html')

@app.route('/assignments')
def assignments():
    # logic to retrieve and display assignments
    return render_template('assignments.html')

@app.route('/quiz/<int:quiz_id>')
def quiz(quiz_id):
    # logic to retrieve and display a specific quiz
    return render_template('quiz.html', quiz_id=quiz_id)


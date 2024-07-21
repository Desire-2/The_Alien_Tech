from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import func


# Use a unique name for the blueprint
analytics = Blueprint('analytics_blueprint', __name__)

@analytics.route('/admin/analytics')
@login_required
def show_analytics():
    if not current_user.is_admin:
        abort(403)
    
    # Example analytics data
    user_growth = User.query.with_entities(func.strftime('%Y-%m', User.date_created), func.count(User.id)).group_by(func.strftime('%Y-%m', User.date_created)).all()
    course_enrollments = Enrollment.query.with_entities(Course.title, func.count(Enrollment.id)).join(Course).group_by(Course.title).all()
    
    return render_template('admin/analytics.html', title='Analytics', user_growth=user_growth, course_enrollments=course_enrollments)

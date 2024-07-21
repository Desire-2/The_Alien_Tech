from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class UserModelView(AdminModelView):
    column_exclude_list = ['password']
    form_excluded_columns = ['password']
    column_searchable_list = ['username', 'email']
    column_filters = ['is_admin', 'is_instructor']

# Similarly, you can create custom views for other models.
class CourseModelView(AdminModelView):
    column_searchable_list = ['title', 'description']
    column_filters = ['title']
    form_excluded_columns = ['modules', 'reviews', 'date_created']

class ModuleModelView(AdminModelView):
    column_searchable_list = ['title', 'description']
    column_filters = ['title', 'course_id']
    form_excluded_columns = ['lessons', 'projects', 'date_created']

class ReviewModelView(AdminModelView):
    column_searchable_list = ['content']
    column_filters = ['course_id', 'user_id', 'rating']
    form_excluded_columns = ['date_created']

class QuizModelView(AdminModelView):
    column_searchable_list = ['title']
    column_filters = ['module_id']
    form_excluded_columns = ['questions']

class ProjectModelView(AdminModelView):
    column_searchable_list = ['title']
    column_filters = ['module_id']
    form_excluded_columns = ['date_created']

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.is_admin or current_user.is_support)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class InstructorModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.is_admin or current_user.is_instructor)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

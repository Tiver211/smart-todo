from datetime import datetime, timezone

from flask_login import UserMixin

from .extensions import db


# Users
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True, nullable=False)
    salt = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    tasks = db.relationship('Task', back_populates='user', cascade='all, delete-orphan')
    groups = db.relationship('Group', back_populates='user', cascade='all, delete-orphan')
    repeating_tasks = db.relationship('RepeatingTask', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return '<User %r>' % self.login

    def get_id(self):
        return self.user_id


# Shared Attributes
class SharedAttributes(db.Model):
    __tablename__ = 'shared_attributes'

    shared_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Integer)
    able_to_split = db.Column(db.Boolean, default=False)
    compilable = db.Column(db.Boolean, default=True)
    duration = db.Column(db.Interval)
    force_time_start = db.Column(db.DateTime)
    force_end_time = db.Column(db.DateTime)
    day_period = db.Column(db.String(50))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    tasks = db.relationship('Task', back_populates='shared_attributes', cascade='all, delete-orphan')
    groups = db.relationship('Group', back_populates='shared_attributes', cascade='all, delete-orphan')
    repeating_tasks = db.relationship('RepeatingTask', back_populates='shared_attributes', cascade='all, delete-orphan')


# Tasks
class Task(db.Model):
    __tablename__ = 'tasks'

    task_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    shared_id = db.Column(db.Integer, db.ForeignKey('shared_attributes.shared_id'), nullable=False)
    parent = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    repeated_from = db.Column(db.Integer, db.ForeignKey('repeating_tasks.repeat_id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='tasks')
    shared_attributes = db.relationship('SharedAttributes', back_populates='tasks')
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[task_id]))
    group = db.relationship('Group', back_populates='tasks')


# Groups
class Group(db.Model):
    __tablename__ = 'groups'

    group_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    shared_id = db.Column(db.Integer, db.ForeignKey('shared_attributes.shared_id'), nullable=False)
    parent = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    repeated_from = db.Column(db.Integer, db.ForeignKey('repeating_tasks.repeat_id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='groups')
    shared_attributes = db.relationship('SharedAttributes', back_populates='groups')
    subgroups = db.relationship('Group', backref=db.backref('parent_group', remote_side=[group_id]))
    tasks = db.relationship('Task', back_populates='group')


# Hashtags
class Hashtag(db.Model):
    __tablename__ = 'hashtags'

    hashtag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationships
    task_hashtags = db.relationship('TaskHashtag', back_populates='hashtag', cascade='all, delete-orphan')


# TaskHashtags
class TaskHashtag(db.Model):
    __tablename__ = 'task_hashtags'

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), primary_key=True)
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtags.hashtag_id'), primary_key=True)

    # Relationships
    task = db.relationship('Task', backref=db.backref('task_hashtags', cascade='all, delete-orphan'))
    hashtag = db.relationship('Hashtag', back_populates='task_hashtags')


# Repeating Tasks
class RepeatingTask(db.Model):
    __tablename__ = 'repeating_tasks'

    repeat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    shared_id = db.Column(db.Integer, db.ForeignKey('shared_attributes.shared_id'), nullable=False)
    repeat_pattern = db.Column(db.String(100), nullable=False)
    parent = db.Column(db.Integer, db.ForeignKey('repeating_tasks.repeat_id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', back_populates='repeating_tasks')
    shared_attributes = db.relationship('SharedAttributes', back_populates='repeating_tasks')
    sub_repeat_tasks = db.relationship('RepeatingTask',
                                       backref=db.backref('parent_repeat_task', remote_side=[repeat_id]))

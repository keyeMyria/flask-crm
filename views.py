from itertools import cycle
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm.collections import InstrumentedList
from flask_admin.model import typefmt
from jinja2 import Markup
from datetime import datetime
from models import Telephone as TelephoneModel, Email as EmailModel, Contact as ContactModel, Company as CompanyModel, Organization as OrganizationModel, Deal as DealModel, Deal as DealModel, Link as LinkModel, Project as ProjectModel, Sprint as SprintModel, Task as TaskModel, Comment as CommentModel, Message as MessageModel


def format_instrumented_list(view, context, model, name):
    value = getattr(model, name)
    out = ""
    if isinstance(value, InstrumentedList):
        out = "<ul>"
        for x in value:
            if x is None:  # items can be created from empty forms in the form. let's fix that in the model
                continue
            if hasattr(x, "admin_view_link"):
                out += "<li><a href='{}'>{}</a></li>".format(
                    getattr(x, "admin_view_link")(), x)
            else:
                out += str(x)
        out += "</ul>"
    return Markup(out)


def format_url(view, context, model, name):
    value = getattr(model, name)
    return Markup("<a href='{url}'>{url}</a>".format(url=value))


def format_datetime(view, context, model, name):
    value = getattr(model, name)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")


def format_comments(view, context, model, name):
    value = getattr(model, name)
    out = ""

    if isinstance(value, InstrumentedList):
        out = "<ul>"
        for x in value:
            if hasattr(x, "admin_view_link"):
                out += "<li>{commenttitle} {commentcontent}<a href='{commentadminlink}'> Read more...</a></li>".format(
                    commentadminlink=getattr(x, "admin_view_link")(), commenttitle=x.name, commentcontent=x.content)
            else:
                out += str(x)
        out += "</ul>"
    return Markup(out)


formatters = dict(list(zip(["telephones", "emails", "users", "contacts", "organizations", "projects",  "deals", "sprints",
                            "links", "tasks", "messages"], cycle([format_instrumented_list]))), comments=format_comments, url=format_url)

formatters = {**formatters, **
              dict(list(zip(["created_at", "updated_at", "closed_at", "start_date", "deadline", "eta"], cycle([format_datetime]))))}


class EnhancedModelView(ModelView):
    can_view_details = True
    column_formatters = formatters
    form_widget_args = {
        'created_at': {
            'readonly': True,
        },
        'updated_at': {
            'readonly': True,
        },
    }


class TelephoneModelView(EnhancedModelView):
    column_filters = column_list = column_details_list = (
        'number', 'contact', 'company')
    column_searchable_list = ('number',)


class EmailModelView(EnhancedModelView):
    form_rules = column_filters = column_list = column_details_list = (
        'email', 'contact', 'company', 'organization')
    column_searchable_list = ('email',)


class ContactModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('firstname', 'lastname', 'description', 'emails', 'telephones', 'message_channels',
                                                         'deals', 'comments', 'tasks', 'projects', 'messages', 'sprints', 'links', 'owner', 'ownerbackup')
    form_edit_rules = ('firstname', 'lastname', 'description', 'emails', 'telephones', 'tasks',
                       'message_channels', 'owner', 'ownerbackup')

    column_searchable_list = ('firstname', 'lastname',)
    column_list = ('firstname', 'lastname', 'emails',
                   'telephones', 'description')
    inline_models = [
        (TelephoneModel, {'form_columns': ['id', 'number']}), (EmailModel, {
            'form_columns': ['id', 'email']}),
        (TaskModel, {'form_columns': ['id', 'title', 'description', 'content', 'type', 'priority', 'eta']})]


class CompanyModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('name', 'description', 'emails', 'telephones',
                                                         'deals', 'messages', 'tasks', 'comments', 'owner', 'ownerbackup')

    form_edit_rules = ('name', 'description', 'emails', 'telephones', 'messages', 'tasks',
                       'owner', 'ownerbackup')

    column_searchable_list = ('name', 'description',)
    column_list = ('name', 'description', 'emails', 'telephones')

    inline_models = [
        (TelephoneModel, {'form_columns': ['id', 'number']}), (EmailModel, {
            'form_columns': ['id', 'email']}),
        (TaskModel, {'form_columns': [
         'id', 'title', 'description', 'content', 'type', 'priority', 'eta']}),
        (MessageModel, {'form_columns': ['id', 'title', 'content', 'channel']})
    ]


class OrganizationModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('name', 'description', 'emails',
                                                         'promoter', 'gaurdian', 'owner',
                                                         'sprints', 'tasks', 'users', 'messages', 'comments',
                                                         'links',)
    form_edit_rules = ('name', 'description', 'emails',
                       'promoter', 'gaurdian', 'owner', 'tasks', 'messages')
    column_list = ('name', 'emails', 'description', 'owner')
    column_searchable_list = ('name', 'description',)
    inline_models = [
        (EmailModel, {
            'form_columns': ['id', 'email']}),
        (TaskModel, {'form_columns': [
         'id', 'title', 'description', 'content', 'type', 'priority', 'eta']}),
        (MessageModel, {'form_columns': ['id', 'title', 'content', 'channel']})
    ]


class DealModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('name',  'amount', 'currency', 'deal_type', 'deal_state',
                                                         'contact', 'company', 'owner', 'ownerbackup',
                                                         'tasks', 'remarks', 'messages', 'comments',
                                                         'links', )
    form_edit_rules = ('name',  'amount', 'currency', 'deal_type', 'deal_state',
                       'contact', 'company', 'owner', 'ownerbackup', 'tasks', 'messages')

    columns_list = ('name', 'amount', 'currency', 'deal_type', 'deal_state')
    column_searchable_list = (
        'name', 'amount', 'currency', 'deal_type', 'deal_state')

    inline_models = [
        (TaskModel, {'form_columns': [
         'id', 'title', 'description', 'content', 'type', 'priority', 'eta']}),
        (MessageModel, {'form_columns': ['id', 'title', 'content', 'channel']})
    ]


class ProjectModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('name', 'description', 'start_date', 'deadline',
                                                         'promoter', 'sprint', 'tasks', 'gaurdian',
                                                         'users', 'comments', 'messages', 'links',)
    edit_form_rules = ('name', 'description',
                       'start_date', 'deadline',
                       'promoter', 'gaurdian',
                       'users', 'tasks', 'messages')

    column_list = ('name', 'description', 'start_date', 'deadline', )
    column_searchable_list = ('name', 'description', 'start_date', 'deadline')

    inline_models = [
        (TaskModel, {'form_columns': [
         'id', 'title', 'description', 'content', 'type', 'priority', 'eta']}),
        (MessageModel, {'form_columns': ['id', 'title', 'content', 'channel']})
    ]


class SprintModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('name', 'description', 'start_date', 'deadline',
                                                         'promoter', 'gaurdian', 'parent', 'users',
                                                         'comments', 'links', 'messages', )
    form_edit_rules = ('name', 'description', 'start_date', 'deadline',
                       'promoter', 'gaurdian', 'parent', 'users', 'tasks', 'messages')
    column_list = ('name', 'description', 'start_date', 'deadline')
    column_searchable_list = ('name', 'description', 'start_date', 'deadline')

    inline_models = [
        (TaskModel, {'form_columns': [
         'id', 'title', 'description', 'content', 'type', 'priority', 'eta']}),
        (MessageModel, {'form_columns': ['id', 'title', 'content', 'channel']})
    ]


class CommentModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('name', 'content',
                                                         'company', 'contact', 'organization', 'project', 'sprint', 'task',
                                                         'link', 'deal', 'sprint', 'remarks')
    form_edit_rules = ('name', 'content')
    column_list = ('name', 'content')
    column_searchable_list = ('name', 'content')


class LinkModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('url', 'contact', 'organization', 'task', 'project',
                                                         'deal', 'sprint', 'labels', 'comments')
    form_edit_rules = ('url', 'labels')
    column_list = ('url', 'labels')
    column_searchable_list = ('url', 'labels')


class TaskModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('title', 'description', 'content',
                                                         'type', 'priority', 'eta', 'time_done',
                                                         'assignee', 'company', 'organization', 'project', 'sprint', 'deal',
                                                         'comments', 'messages', 'remarks')
    form_edit_rules = ('title', 'description', 'content',
                       'type', 'priority', 'eta', 'time_done',
                       'assignee', 'company', 'organization', 'project', 'sprint', 'deal',
                       'remarks')
    column_list = ('title', 'description', 'assignee', 'eta', 'priority', 'time_done',
                   'organization', 'company', 'project', 'sprint', 'deal')
    column_searchable_list = ('title', 'description',
                              'content', 'type', 'priority', 'eta')
    column_sortable_list = ('eta', 'priority')


class MessageModelView(EnhancedModelView):
    form_rules = column_filters = column_details_list = ('title', 'content', 'channel', 'time_tosend', 'time_sent',
                                                         'company', 'contact', 'organization', 'project', 'sprint', 'deal', 'task')
    form_edit_rules = ('title', 'content', 'channel',
                       'time_tosend', 'time_sent',)
    column_list = ('title', 'content', 'channel', 'time_tosend', 'time_sent',
                   'company', 'contact', 'deal', 'organizaton', 'task', 'project', 'sprint')
    column_searchable_list = ('title', 'content', 'channel')

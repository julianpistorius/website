from flask import render_template
from flask_hookserver import Hooks

from .github import github
from .models import db, User


hooks = Hooks()


@hooks.hook('ping')
def ping(data, guid):
    return 'pong'


@hooks.hook('membership')
def membership(data, guid):
    if data['scope'] != 'team':
        return
    member = User.query.filter_by(id=data['member']['id']).first()
    if member is None:
        return
    if data['action'] == 'added':
        member.is_member = True
        db.session.commit()
    elif data['action'] == 'removed':
        member.is_member = False
        db.session.commit()
    return 'Thanks'


@hooks.hook('member')
def member(data, guid):
    # if no action was given or it was about removing a member
    if data.get('action') != 'added':
        return

    # if there is no repo data
    repo = data.get('repository')
    if repo is None:
        return

    # get list of roadies and set them as the default assignees
    roadies = User.query.filter_by(
        is_member=True,
        is_banned=False,
        is_roadie=True,
    )
    assignees = [roadie.login for roadie in roadies]
    # add sender of the hook as well if given
    if 'sender' in data:
        assignees.append(data['sender']['login'])

    data = {
        'title': render_template('hooks/project-title.txt', **data),
        'body': render_template('hooks/project-body.txt', **data),
        'labels': ['guidelines', 'review'],
        'assignees': assignees,
    }

    github.post(
        'repos/jazzband/roadies/issues',
        data,
        access_token=github.admin_access_token,
    )
    return 'Thanks'

from .github import github
from .models import db, User, Project


def projects():
    "Syncs projects"
    projects_data = github.get_projects()
    Project.sync(projects_data)


def members():
    "Syncs members"
    members_data = github.get_members()
    User.sync(members_data)

    stored_ids = set(user.id for user in User.query.all())
    fetched_ids = set(m['id'] for m in members_data)
    stale_ids = stored_ids - fetched_ids
    if stale_ids:
        User.query.filter(
            User.id.in_(stale_ids)
        ).update({'is_member': False}, 'fetch')
        db.session.commit()

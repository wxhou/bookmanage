
import click
from common.extensions import db


def register_initial(app):
    """初始化"""

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            db.drop_all()
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--email',
                  prompt=True,
                  help='The username used to login.')
    @click.option('--password',
                  prompt=True,
                  hide_input=True,
                  confirmation_prompt=True,
                  help='The password used to login.')
    def adminuser(email, password):
        """Create user."""
        from apps.auth.model import User, Role

        db.create_all()

        user = User.query.first()
        role = Role.query.filter_by(name='Admin').first()
        if user is not None:
            click.echo('Updating user...')
            user.email = email
            user.role = role
            user.active = True
            user.password = password
        else:
            click.echo('Creating user...')
            user = User(email=email, role=role)
            user.password = password
            user.active = True
            db.session.add(user)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    def initrole():
        from apps.auth.model import Role, Permission

        roles_permissions_map = {
            'Guest': ['SEE'],
            'User': ['LOGIN', 'SEE', 'LEASE'],
            'VIP': ['LOGIN', 'SEE', 'LEASE', 'BUY'],
            'Author': ['LOGIN', 'SEE', 'LEASE', 'BUY', 'WRITE', 'UPLOAD'],
            'Admin':
                ['LOGIN', 'SEE', 'LEASE', 'BUY', 'WRITE', 'UPLOAD', 'ADMIN']
        }
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(
                    name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()
        click.echo("Init Role Done!")

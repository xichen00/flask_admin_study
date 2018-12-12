from flask_security import UserMixin, RoleMixin
from iqupdate import db as database

# Define models
roles_users = database.Table(
    'roles_users',
    database.Column('user_id', database.Integer(), database.ForeignKey('user.id')),
    database.Column('role_id', database.Integer(), database.ForeignKey('role.id'))
)


class Role(database.Model, RoleMixin):
    id = database.Column(database.Integer(), primary_key=True)
    name = database.Column(database.String(80), unique=True)
    description = database.Column(database.String(255))

    def __str__(self):
        return self.name


class User(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    first_name = database.Column(database.String(255))
    last_name = database.Column(database.String(255))
    email = database.Column(database.String(255), unique=True)
    password = database.Column(database.String(255))
    active = database.Column(database.Boolean())
    roles = database.relationship('Role', secondary=roles_users,
                                  backref=database.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


class ServicePack(database.Model):
    id = database.Column(database.Integer(), primary_key=True)
    description = database.Column(database.String(20), unique=True, nullable=False)
    version_number = database.Column(database.Integer(), unique=True, nullable=False)
    release_date = database.Column(database.Date(), nullable=False)

    def __str__(self):
        return "{} - {}".format(self.description, self.release_date)


class ServicePackDetail(database.Model):
    id = database.Column(database.Integer(), primary_key=True)
    language = database.Column(database.Enum('de', 'en'), nullable=False)
    contents = database.Column(database.Text, nullable=False)
    service_pack_id = database.Column(database.Integer, database.ForeignKey(ServicePack.id), nullable=False)
    service_pack = database.relation(ServicePack, backref='details')

    def __str__(self):
        return "{} - {}".format(self.language, self.contents)

    def __repr__(self):
        return self.__str__

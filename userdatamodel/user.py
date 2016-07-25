from . import Base
import datetime
from sqlalchemy import Integer, String, Column, Table, Boolean,BigInteger, DateTime, text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgres import ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import LargeBinary


user_group = Table(
    'user_group', Base.metadata,
    Column('user_id', Integer, ForeignKey('User.id')),
    Column('group_id', Integer, ForeignKey('research_group.id'))
)


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    username = Column(String(40), unique=True)
    
    # id from identifier, which is not guarenteed to be unique across all identifiers
    # for most of the cases, it will be same as username
    id_from_idp = Column(String)
    email = Column(String)

    idp_id = Column(Integer, ForeignKey('identity_provider.id'))
    identity_provider = relationship('IdentityProvider', backref='users')

    department_id = Column(Integer, ForeignKey('department.id'))
    department = relationship('Department', backref='users')

    research_groups = relationship("ResearchGroup", secondary=user_group, backref='users')

    active = Column(Boolean)
    is_admin = Column(Boolean, default=False)

    project_access = association_proxy(
        "user_accesses",
        "project")

    buckets = association_proxy(
        "user_to_buckets",
        "bucket")

    application = relationship('Application', backref='user', uselist=False)


class UserAccess(Base):
    __tablename__ = "user_access"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, backref='user_accesses')

    project_id = Column(Integer, ForeignKey('project.id'))

    project = relationship('Project', backref='user_accesses')
    privilege = Column(ARRAY(String))

    provider_id = Column(Integer, ForeignKey('authorization_provider.id'))
    auth_provider = relationship('AuthorizationProvider', backref='acls')


class UserToBucket(Base):
    __tablename__ = "user_to_bucket"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, backref='user_to_buckets')

    bucket_id = Column(Integer, ForeignKey('bucket.id'))

    bucket = relationship('Bucket', backref='user_to_buckets')
    privilege = Column(ARRAY(String))


class ResearchGroup(Base):
    __tablename__ = "research_group"

    id = Column(Integer, primary_key=True)
    name = Column(Integer, unique=True)

    lead_id = Column(Integer, ForeignKey(User.id))
    lead = relationship('User', backref='lead_group')




class IdentityProvider(Base):
    __tablename__ = 'identity_provider'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    
class AuthorizationProvider(Base):
    __tablename__ = 'authorization_provider'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)

class Bucket(Base):
    __tablename__ = 'bucket'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    provider_id = Column(Integer, ForeignKey('storage_provider.id'))
    provider = relationship('StorageProvider', backref='buckets')
    users = association_proxy(
        "user_to_buckets",
        "user")




class StorageProvider(Base):
    __tablename__ = 'storage_provider'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    host = Column(String, unique=True)
    backend = Column(String)
    description = Column(String)


class ComputeProvider(Base):
    __tablename__ = 'compute_provider'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    auth_url = Column(String, unique=True)
    description = Column(String)


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    dbgap_accession_number = Column(String, unique=True)
    description = Column(String)
    parent_id = Column(Integer, ForeignKey('project.id'))
    parent = relationship('Project', backref='sub_projects', remote_side=[id])
    buckets = association_proxy(
    "project_to_buckets",
    "bucket")

class ProjectToBucket(Base):
    __tablename__ = "project_to_bucket"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(Project, backref='project_to_buckets')

    bucket_id = Column(Integer, ForeignKey('bucket.id'))

    bucket = relationship('Bucket', backref='project_to_buckets')
    privilege = Column(ARRAY(String))


class ComputeAccess(Base):
    __tablename__ = "compute_access"

    id = Column(Integer, primary_key=True)

    # compute access can be linked to a project/research group/user
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', backref='compute_access')

    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User', backref='compute_access')

    group_id = Column(Integer, ForeignKey('research_group.id'))
    research_group = relationship('ResearchGroup', backref='compute_access')

    provider_id = Column(Integer, ForeignKey('compute_provider.id'))
    provider = relationship('ComputeProvider', backref='compute_access')

    instances = Column(Integer)
    cores = Column(Integer)
    ram = Column(BigInteger)
    floating_ips = Column(Integer)
    additional_info = Column(JSONB)


class StorageAccess(Base):
    __tablename__ = "storage_access"

    id = Column(Integer, primary_key=True)

    # storage access can be linked to a project/research group/user
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', backref='storage_access')

    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User', backref='storage_access')

    group_id = Column(Integer, ForeignKey('research_group.id'))
    research_group = relationship('ResearchGroup', backref='storage_access')

    provider_id = Column(Integer, ForeignKey('storage_provider.id'))
    provider = relationship('StorageProvider', backref='storage_access')

    max_objects = Column(BigInteger)
    max_size = Column(BigInteger)
    max_buckets = Column(Integer)
    additional_info = Column(JSONB)


class EventLog(Base):
    __tablename__ = "event_log"

    id = Column(Integer, primary_key=True)
    action = Column(String)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    target = Column(String)
    target_type = Column(String)
    description = Column(String)


class Organization(Base):
    __tablename__ = 'organization'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)


class Department(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)

    org_id = Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', backref='departments')

# application related tables

class Application(Base):
    __tablename__ = "application"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    resources_granted = Column(ARRAY(String)) # eg: ["compute", "storage"]
    certificates_uploaded = relationship(
        "Certificate",
        backref='user',
    )
    message = Column(String)


class Certificate(Base):
    __tablename__ = "certificate"

    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('application.id'))
    name = Column(String(40))
    extension = Column(String)
    data = Column(LargeBinary)

    @property
    def filename(self):
        return '{}.{}'.format(self.name, self.extension)

class S3Credential(Base):
    __tablename__ = "s3credential"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship("User", backref="s3credentials")

    access_key = Column(String)
    
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    expire = Column(Integer)


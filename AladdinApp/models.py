
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    organization = db.relationship('Organization', backref='users')

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100))  # Hospital, Clinic, Research, etc.
    license_number = db.Column(db.String(100))
    regulatory_body = db.Column(db.String(100))  # DoH, DHA, TDRA
    parent_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    parent = db.relationship('Organization', remote_side=[id], backref='subsidiaries')

class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # IT, Clinical, Operational, Strategic
    likelihood = db.Column(db.Integer, nullable=False)  # 1-5 scale
    impact = db.Column(db.Integer, nullable=False)  # 1-5 scale
    risk_score = db.Column(db.Float)
    risk_level = db.Column(db.String(50))  # Low, Medium, High, Critical
    status = db.Column(db.String(50), default='Open')
    treatment_plan = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = db.relationship('User', backref='owned_risks')
    organization = db.relationship('Organization', backref='risks')
    
    def calculate_risk_score(self):
        self.risk_score = self.likelihood * self.impact
        if self.risk_score >= 20:
            self.risk_level = 'Critical'
        elif self.risk_score >= 15:
            self.risk_level = 'High'
        elif self.risk_score >= 10:
            self.risk_level = 'Medium'
        else:
            self.risk_level = 'Low'

class ComplianceFramework(db.Model):
    __tablename__ = 'compliance_frameworks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(50))
    description = db.Column(db.Text)
    regulatory_body = db.Column(db.String(100))
    is_mandatory = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Policy(db.Model):
    __tablename__ = 'policies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(50), default='1.0')
    status = db.Column(db.String(50), default='Draft')
    category = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_date = db.Column(db.DateTime)
    effective_date = db.Column(db.DateTime)
    review_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_policies')
    approver = db.relationship('User', foreign_keys=[approved_by])
    organization = db.relationship('Organization', backref='policies')

class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100))  # Server, Workstation, Network, Application
    category = db.Column(db.String(100))  # IT, Medical, Infrastructure
    ip_address = db.Column(db.String(45))
    mac_address = db.Column(db.String(17))
    operating_system = db.Column(db.String(100))
    location = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    criticality = db.Column(db.String(50), default='Medium')
    status = db.Column(db.String(50), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    owner = db.relationship('User', backref='owned_assets')
    organization = db.relationship('Organization', backref='assets')

class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(100))  # Security, Operational, Clinical
    severity = db.Column(db.String(50))  # Low, Medium, High, Critical
    status = db.Column(db.String(50), default='Open')
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    root_cause = db.Column(db.Text)
    resolution = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reported_incidents')
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_incidents')
    organization = db.relationship('Organization', backref='incidents')

class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    services_provided = db.Column(db.Text)
    risk_score = db.Column(db.Integer, default=0)
    risk_level = db.Column(db.String(50), default='Low')
    contract_start = db.Column(db.DateTime)
    contract_end = db.Column(db.DateTime)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    status = db.Column(db.String(50), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    organization = db.relationship('Organization', backref='vendors')

class Audit(db.Model):
    __tablename__ = 'audits'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100))  # Internal, External, Regulatory
    framework_id = db.Column(db.Integer, db.ForeignKey('compliance_frameworks.id'))
    auditor_name = db.Column(db.String(255))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='Planned')
    findings_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    framework = db.relationship('ComplianceFramework', backref='audits')
    organization = db.relationship('Organization', backref='audits')

class Finding(db.Model):
    __tablename__ = 'findings'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.Integer, db.ForeignKey('audits.id'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(50))  # Low, Medium, High, Critical
    status = db.Column(db.String(50), default='Open')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    due_date = db.Column(db.DateTime)
    remediation_plan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    audit = db.relationship('Audit', backref='findings')
    assignee = db.relationship('User', backref='assigned_findings')

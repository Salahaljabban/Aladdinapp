
from app import app, db
from models import User, Organization, ComplianceFramework
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Initialize the database with sample data"""
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default organization
        if not Organization.query.first():
            org = Organization(
                name="Aladdin Healthcare Group",
                type="Healthcare",
                license_number="DHA-12345",
                regulatory_body="DHA"
            )
            db.session.add(org)
            db.session.commit()
            
            # Create admin user
            admin = User(
                username="admin",
                email="admin@aladdin-grc.local",
                password_hash=generate_password_hash("admin123"),
                role="admin",
                organization_id=org.id,
                is_active=True
            )
            db.session.add(admin)
            
            # Create test user
            user = User(
                username="user",
                email="user@aladdin-grc.local",
                password_hash=generate_password_hash("user123"),
                role="user",
                organization_id=org.id,
                is_active=True
            )
            db.session.add(user)
            
            # Create compliance frameworks
            frameworks = [
                ComplianceFramework(
                    name="ADHICS v2",
                    version="2.0",
                    description="Abu Dhabi Health Information and Cyber Security Standard",
                    regulatory_body="DoH",
                    is_mandatory=True
                ),
                ComplianceFramework(
                    name="ISO 27001",
                    version="2022",
                    description="Information Security Management Systems",
                    regulatory_body="ISO",
                    is_mandatory=False
                ),
                ComplianceFramework(
                    name="UAE PDPL",
                    version="1.0",
                    description="UAE Personal Data Protection Law",
                    regulatory_body="UAE Government",
                    is_mandatory=True
                ),
                ComplianceFramework(
                    name="NIST CSF",
                    version="1.1",
                    description="NIST Cybersecurity Framework",
                    regulatory_body="NIST",
                    is_mandatory=False
                )
            ]
            
            for framework in frameworks:
                db.session.add(framework)
            
            db.session.commit()
            print("Database initialized with sample data!")
            print("Login credentials:")
            print("Admin: admin / admin123")
            print("User: user / user123")

if __name__ == "__main__":
    init_database()

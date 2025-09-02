"""
Database initialization and seeding script.
Creates roles, default admin user, and complaint ticket type with fields.
"""
from sqlmodel import Session, select
from datetime import datetime

from app.core.database import engine
from app.core.security import get_password_hash
from app.models.models import (
    Role, RoleEnum, User, RoleAssignment, 
    TicketType, FormField
)


def init_roles(session: Session):
    """Initialize roles."""
    roles_data = [
        (RoleEnum.ADMIN, "Full system access"),
        (RoleEnum.PUBLISHER, "Can create and edit tickets"),
        (RoleEnum.HANDLER, "Can view and handle assigned tickets"),
        (RoleEnum.VIEWER, "Read-only access to tickets")
    ]
    
    for role_name, description in roles_data:
        existing_role = session.exec(
            select(Role).where(Role.name == role_name)
        ).first()
        
        if not existing_role:
            role = Role(name=role_name, description=description)
            session.add(role)
            print(f"Created role: {role_name}")
    
    session.commit()


def init_admin_user(session: Session):
    """Create default admin user."""
    admin_email = "admin@example.com"
    admin_password = "Admin123!"
    
    existing_user = session.exec(
        select(User).where(User.email == admin_email)
    ).first()
    
    if existing_user:
        print(f"Admin user already exists: {admin_email}")
        return existing_user
    
    # Create admin user
    admin_user = User(
        email=admin_email,
        username="admin",
        full_name="System Administrator",
        hashed_password=get_password_hash(admin_password),
        is_active=True
    )
    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)
    
    # Assign admin role
    admin_role = session.exec(
        select(Role).where(Role.name == RoleEnum.ADMIN)
    ).first()
    
    if admin_role:
        role_assignment = RoleAssignment(
            user_id=admin_user.id,
            role_id=admin_role.id
        )
        session.add(role_assignment)
        session.commit()
    
    print(f"Created admin user: {admin_email} / {admin_password}")
    return admin_user


def init_complaint_ticket_type(session: Session):
    """Create complaint ticket type with fields."""
    ticket_type_name = "complaint"
    
    existing_type = session.exec(
        select(TicketType).where(TicketType.name == ticket_type_name)
    ).first()
    
    if existing_type:
        print(f"Ticket type already exists: {ticket_type_name}")
        return existing_type
    
    # Create ticket type
    ticket_type = TicketType(
        name=ticket_type_name,
        description="5G network complaint tickets"
    )
    session.add(ticket_type)
    session.commit()
    session.refresh(ticket_type)
    
    # Define form fields
    form_fields_data = [
        # Basic complaint fields
        ("complaint_number", "Complaint Number", "text", None, False, 1),
        ("district", "District", "text", None, False, 2),
        ("complainant_name", "Complainant Name", "text", None, True, 3),
        ("phone", "Contact Phone", "text", None, False, 4),
        ("address", "Address", "textarea", None, False, 5),
        ("complaint_type", "Complaint Type", "select", {
            "options": ["信号问题", "网络故障", "服务问题", "其他"]
        }, False, 6),
        ("complaint_content", "Complaint Content", "textarea", None, True, 7),
        ("handling_status", "Handling Status", "select", {
            "options": ["待处理", "处理中", "已完成", "已取消"]
        }, False, 8),
        
        # Test results array field
        ("test_results", "Test Results", "array", {
            "array_fields": [
                {"name": "pci", "label": "PCI", "type": "number"},
                {"name": "frequency", "label": "Frequency", "type": "number"},
                {"name": "cell_id", "label": "Cell ID", "type": "text"},
                {"name": "rsrp", "label": "RSRP (dBm)", "type": "number"},
                {"name": "sinr", "label": "SINR (dB)", "type": "number"},
                {"name": "uplink_rate", "label": "Uplink Rate (Mbps)", "type": "number"},
                {"name": "downlink_rate", "label": "Downlink Rate (Mbps)", "type": "number"},
                {"name": "interference_level", "label": "Interference Level", "type": "select", 
                 "options": ["低", "中", "高"]},
                {"name": "notes", "label": "Notes", "type": "textarea"}
            ]
        }, False, 9)
    ]
    
    for field_name, field_label, field_type, field_options, is_required, display_order in form_fields_data:
        form_field = FormField(
            ticket_type_id=ticket_type.id,
            field_name=field_name,
            field_label=field_label,
            field_type=field_type,
            field_options=field_options,
            is_required=is_required,
            display_order=display_order
        )
        session.add(form_field)
    
    session.commit()
    print(f"Created ticket type '{ticket_type_name}' with {len(form_fields_data)} fields")
    return ticket_type


def init_database():
    """Initialize database with default data."""
    print("Initializing database...")
    
    with Session(engine) as session:
        print("Creating roles...")
        init_roles(session)
        
        print("Creating admin user...")
        init_admin_user(session)
        
        print("Creating complaint ticket type...")
        init_complaint_ticket_type(session)
        
    print("Database initialization completed!")


if __name__ == "__main__":
    init_database()
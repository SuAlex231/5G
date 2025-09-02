import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, Role, RoleAssignment
from app.models.ticket import TicketType, FormField
from app.models import Base

def init_db():
    """Initialize database with seed data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create roles
        roles_data = [
            {
                "name": "admin",
                "description": "System administrator with full access",
                "permissions": {
                    "users": ["create", "read", "update", "delete"],
                    "tickets": ["create", "read", "update", "delete"],
                    "import_export": ["create", "read"],
                    "roles": ["create", "read", "update", "delete"]
                }
            },
            {
                "name": "publisher", 
                "description": "Can create, read, update tickets and import/export",
                "permissions": {
                    "tickets": ["create", "read", "update"],
                    "import_export": ["create", "read"]
                }
            },
            {
                "name": "handler",
                "description": "Can read and update tickets",
                "permissions": {
                    "tickets": ["read", "update"]
                }
            },
            {
                "name": "viewer",
                "description": "Can only view tickets",
                "permissions": {
                    "tickets": ["read"]
                }
            }
        ]
        
        roles = {}
        for role_data in roles_data:
            role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not role:
                role = Role(**role_data)
                db.add(role)
                db.commit()
                db.refresh(role)
            roles[role_data["name"]] = role
        
        # Create admin user
        admin_user = db.query(User).filter(User.email == "admin@5g-ticketing.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@5g-ticketing.com",
                password_hash=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Assign admin role
            admin_role_assignment = RoleAssignment(
                user_id=admin_user.id,
                role_id=roles["admin"].id
            )
            db.add(admin_role_assignment)
        
        # Create complaint ticket type
        complaint_type = db.query(TicketType).filter(TicketType.name == "complaint").first()
        if not complaint_type:
            complaint_type = TicketType(
                name="complaint",
                description="5G网络投诉工单",
                schema_config={
                    "category": "complaint",
                    "supports_images": True,
                    "max_images": 8,
                    "supports_matrix": True
                }
            )
            db.add(complaint_type)
            db.commit()
            db.refresh(complaint_type)
            
            # Create form fields for complaint type
            form_fields = [
                {
                    "field_name": "ticket_number",
                    "field_type": "text",
                    "field_label": "工单号",
                    "config": {"required": True, "readonly": True},
                    "order_index": 0,
                    "is_required": True
                },
                {
                    "field_name": "district",
                    "field_type": "select",
                    "field_label": "区县",
                    "config": {
                        "options": ["朝阳区", "海淀区", "东城区", "西城区", "丰台区", "石景山区", "通州区", "顺义区", "昌平区", "大兴区", "房山区", "门头沟区", "平谷区", "密云区", "延庆区"],
                        "required": True
                    },
                    "order_index": 1,
                    "is_required": True
                },
                {
                    "field_name": "problem_description",
                    "field_type": "textarea",
                    "field_label": "问题描述",
                    "config": {"required": True, "rows": 4},
                    "order_index": 2,
                    "is_required": True
                },
                {
                    "field_name": "location",
                    "field_type": "text",
                    "field_label": "位置",
                    "config": {"required": True},
                    "order_index": 3,
                    "is_required": True
                },
                {
                    "field_name": "contact_person",
                    "field_type": "text", 
                    "field_label": "联系人",
                    "config": {"required": True},
                    "order_index": 4,
                    "is_required": True
                },
                {
                    "field_name": "contact_phone",
                    "field_type": "text",
                    "field_label": "联系电话",
                    "config": {"required": True, "pattern": "^1[3-9]\\d{9}$"},
                    "order_index": 5,
                    "is_required": True
                },
                {
                    "field_name": "test_results",
                    "field_type": "array",
                    "field_label": "测试情况",
                    "config": {
                        "fields": [
                            {"name": "pci", "label": "PCI", "type": "number"},
                            {"name": "frequency", "label": "频率(MHz)", "type": "number"},
                            {"name": "cell_id", "label": "小区ID", "type": "text"},
                            {"name": "rsrp", "label": "RSRP(dBm)", "type": "number"},
                            {"name": "sinr", "label": "SINR(dB)", "type": "number"},
                            {"name": "upload_speed", "label": "上传速率(Mbps)", "type": "number"},
                            {"name": "download_speed", "label": "下载速率(Mbps)", "type": "number"},
                            {"name": "interference", "label": "干扰", "type": "text"},
                            {"name": "notes", "label": "备注", "type": "text"}
                        ]
                    },
                    "order_index": 6,
                    "is_required": False
                }
            ]
            
            for field_data in form_fields:
                field = FormField(
                    ticket_type_id=complaint_type.id,
                    **field_data
                )
                db.add(field)
        
        db.commit()
        print("Database initialized successfully!")
        print("Admin user created:")
        print("  Email: admin@5g-ticketing.com")
        print("  Password: admin123")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
# Import all models to ensure they are registered with SQLAlchemy
from .user import User, Role, RoleAssignment
from .ticket import Ticket, TicketType, FormField, TicketStatus
from .file import TicketImage, Attachment, OCRResult
from .audit import Job, AuditLog, JobStatus, JobType

__all__ = [
    "User", "Role", "RoleAssignment",
    "Ticket", "TicketType", "FormField", "TicketStatus", 
    "TicketImage", "Attachment", "OCRResult",
    "Job", "AuditLog", "JobStatus", "JobType"
]
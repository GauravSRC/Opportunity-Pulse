"""SQLAlchemy ORM models.

Importing this package registers every model on ``Base.metadata`` so Alembic
autogeneration and ``create_all`` see the full schema.
"""

from app.db.base import Base
from app.models.alert import Alert
from app.models.audit import AuditLog
from app.models.deadline import Deadline
from app.models.embedding import Embedding
from app.models.feedback import Feedback
from app.models.listing import DedupCluster, NormalizedListing, RawListing
from app.models.outreach import OutreachArtifact
from app.models.ranking import RankScore
from app.models.source import OpportunitySource
from app.models.user import Skill, User, UserProfile, profile_skills

__all__ = [
    "Base",
    "User",
    "UserProfile",
    "Skill",
    "profile_skills",
    "OpportunitySource",
    "RawListing",
    "NormalizedListing",
    "DedupCluster",
    "Deadline",
    "RankScore",
    "OutreachArtifact",
    "Feedback",
    "Alert",
    "Embedding",
    "AuditLog",
]

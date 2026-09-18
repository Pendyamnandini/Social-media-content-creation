from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from app.config.database import Base
import enum

class ConnectionStatus(str, enum.Enum):
    CONNECTED = "CONNECTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"

class PostStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    APPROVED = "APPROVED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class LinkedInConnection(Base):
    __tablename__ = "linkedin_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    linkedin_member_id = Column(String, index=True)
    linkedin_profile_name = Column(String)
    linkedin_profile_picture = Column(String)
    profile_url = Column(String, nullable=True)
    access_token_encrypted = Column(Text)
    refresh_token_encrypted = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True))
    scopes = Column(String)
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.DISCONNECTED)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class GeneratedPost(Base):
    __tablename__ = "generated_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    platform = Column(String, default="LINKEDIN")
    original_prompt = Column(Text)
    post_content = Column(Text)
    hashtags = Column(Text) # Stored as JSON string
    suggested_comment = Column(Text)
    suggested_message = Column(Text)
    image_url = Column(String, nullable=True)
    content_type = Column(String)
    tone = Column(String)
    audience = Column(String)
    content_analysis = Column(Text, nullable=True) # Stored as JSON string
    image_prompt = Column(Text, nullable=True)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class PublishingRecord(Base):
    __tablename__ = "publishing_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    generated_post_id = Column(Integer, ForeignKey("generated_posts.id"), index=True, nullable=False)
    platform = Column(String, default="LINKEDIN")
    status = Column(Enum(PostStatus), default=PostStatus.PUBLISHING)
    platform_post_id = Column(String, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    media_attached = Column(Boolean, default=False)
    linkedin_media_urn = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

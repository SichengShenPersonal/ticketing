from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class TicketTemplate(Base):
    __tablename__ = 'ticket_templates'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CustomField(Base):
    __tablename__ = 'custom_fields'
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('ticket_templates.id'))
    field_name = Column(String)
    field_type = Column(String)  # text, number, select, etc.
    is_required = Column(Boolean, default=False)

class WorkflowNode(Base):
    __tablename__ = 'workflow_nodes'
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('ticket_templates.id'))
    step_order = Column(Integer)
    role = Column(String)
    department = Column(String)
    instructions = Column(Text)

class TicketInstance(Base):
    __tablename__ = 'ticket_instances'
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('ticket_templates.id'))
    title = Column(String)
    status = Column(String)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TicketStep(Base):
    __tablename__ = 'ticket_steps'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('ticket_instances.id'))
    node_id = Column(Integer, ForeignKey('workflow_nodes.id'))
    assigned_to = Column(String)
    submitted_at = Column(DateTime)
    data = Column(JSON)
    status = Column(String)
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class user(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    level = Column(Integer, index=True, default=-1)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    is_enable = Column(Boolean, index=True, default=False)
    verify_code_enable = Column(Boolean, index=True, default=False)
    info = Column(JSON, index=True)

    # address = Column(String, index=True)
    # country = Column(String, index=True)
    # telephone_number = Column(String, index=True)
    # company_scale = Column(String, index=True)
    # usage = Column(String, index=True)
    # industry = Column(String, index=True)
    # email_alert = Column(Boolean, index=True)
    # language = Column(Integer, index=True)
    # verify_code_enable = Column(Boolean, index=True)

    def __init__(self, email, password, name, info, is_enable, level, group_id, **kwargs):
        self.email = email
        self.password = password
        self.name = name
        self.is_enable = is_enable
        self.info = info
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.level = level
        self.group_id = group_id
        self.verify_code_enable = False

    def __repr__(self):
        return 'id={},group_id={}, email={}, name={},info={}'.format(
            self.id, self.group_id, self.email, self.name, self.info, self.created_at, self.updated_at
        )

    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'email': self.email,
    #         'name': self.name,
    #         'address': self.address,
    #         'country': self.country,
    #         'telephone_number': self.telephone_number,
    #         'usage': self.usage,
    #         'is_enable': self.is_enable,
    #         'created_at': str(self.created_at),
    #         'updated_at': str(self.updated_at),
    #         'serial_number': self.serial_number,
    #         'industry': self.industry,
    #         'company_scale': self.company_scale,
    #         'email_alert': self.email_alert,
    #         'language': self.language
    #     }

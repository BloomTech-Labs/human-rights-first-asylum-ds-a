from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserObject(Base):
    __table__="users"
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)


class TagObject(Base):
    __table__='tagged_objects'
    case_id = Column(Integer, ForeignKey("cases.case_id"), primary_key=True)
    main_category_id = Column(Integer)
    sub_category_id = Column(Integer)
    tag_name = Column(String)

class CaseObject(Base):
    __table__='cases'

    case_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.user_id"))
    public = Column(Boolean)
    case_title = Column(String)
    case_number = Column(String)
    judge_name = Column(String)
    outcome = Column(String)
    country_of_origin = Column(String)
    pdf_file = Column(String)

class tags_by_case(Base):
    __table__="tags_by_case"
    case_id = Column(ForeignKey("tagged_objects.case_id"))

class main_categories(tags_by_case):
    main_category_name = Column(String)

class sub_categories(main_categories):
    sub_category_name = Column(String)
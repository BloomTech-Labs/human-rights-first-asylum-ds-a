from datetime import date
from pydantic import BaseModel
from typing import Optional, List

class UserObject(BaseModel):
    user_id: int
    first_name: str = "Your First Name"
    last_name: str = "Your Last Name"
    email: str = "Your Email"

class TagObject(BaseModel):
    main_category_id: int
    sub_category_id: int
    tag_name: str

    class Config:
        orm_mode = True

class CaseObject(BaseModel):
    case_id: int
    user_id: int
    public: Optional[bool]
    case_title: Optional[str] = "Felicia v. B.I.A."
    case_number: Optional[int] = 4321
    judge_name: Optional[str] = "Dorothy Day"
    outcome: Optional[str] = "Granted"
    country_of_origin: Optional[str] = "Kazakhstan"
    pdf_file: Optional[str] = 'File path'
    tags: List[TagObject] = []

    class Config:
        orm_mode = True

class tags_by_case(BaseModel):
    case_id: int

    class Config:
        orm_mode = True

class main_categories(tags_by_case):
    main_category_name: str

    class Config:
        orm_mode = True

class sub_categories(main_categories):
    sub_category_name: str

    class Config:
        orm_mode = True
from dataclasses import dataclass
from datetime import date
from typing import (
    List,
    Optional,
)


@dataclass
class User:
    id: str
    origin_id: str
    name: str
    email: Optional[str]
    birthday: Optional[date]
    gender: Optional[str]
    nationality: Optional[str]
    picture_url: Optional[str]
    visit_count: int
    allowed_push_message: bool
    can_share: bool
    extra: Optional[str]


@dataclass
class UserPage:
    id: str
    name: Optional[str]
    section: int
    owner: int
    book_code: int
    page_number: int
    note_id: str
    last_stroke_at: Optional[int]
    last_stroke_user_id: Optional[str]
    digital: bool
    favorite: bool
    trans_text: Optional[str]
    trans_text_word: Optional[str]
    trans_time: Optional[int]
    created_at: int
    modified_at: int


@dataclass
class UserNote:
    id: str
    name: Optional[str]
    section: int
    owner: int
    book_code: int
    start_page: int
    end_page: int
    application_id: int
    paper_group_id: Optional[str]
    user_id: Optional[str]
    description: Optional[str]
    active: bool
    category: Optional[str]
    cover: Optional[str]
    digital: bool
    hwr_lang: Optional[str]
    last_stroke_at: Optional[int]
    last_stroke_user_id: Optional[str]
    page_number: Optional[int]
    resource_owner_id: Optional[str]
    total_pages: Optional[int]
    using_pages: Optional[int]
    created_at: int
    modified_at: int


@dataclass
class Stroke:
    version: int
    write_id: str
    dot_count: int
    dots: str
    mac: str
    pen_tip_type: int
    start_time: int
    updated: int
    stroke_type: int
    thickness: int
    color: int
    delete_flag: int


@dataclass
class Ink:
    note_uuid: str
    section: int
    owner: int
    book_code: int
    page_number: int
    strokes: List[Stroke]

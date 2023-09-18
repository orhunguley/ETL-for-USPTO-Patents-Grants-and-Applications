from dataclasses import dataclass, field, fields
from typing import List, Type, Optional, Dict
import datetime


class DataIntegrityError(Exception):
    pass


@dataclass
class USPatent:
    date_produced: datetime.date = field(default=None)
    date_published: datetime.date = field(default=None)
    date_applied: datetime.date = field(default=None)
    ipcr_list: Optional[List[Dict]] = field(default=None)
    cpc_list: Optional[List[Dict]] = field(default=None)
    pub_doc_id: str = field(default=None)
    app_doc_id: str = field(default=None)
    patent_type: str = field(default=None)
    invention_title: str = field(default=None)
    inventors: Optional[List[Dict]] = field(default=None)
    assignees: Optional[List[Dict]] = field(default=None)
    abstract: str = field(default=None)

    def check_data_integrity(self):
        errors = []

        # Check date fields
        date_fields = ['date_produced', 'date_published', 'date_applied']
        for field_name in date_fields:
            date_value = getattr(self, field_name)
            if date_value is not None and not isinstance(
                    date_value, datetime.date):
                errors.append(f"{field_name} should be of type datetime.date")

        # Check list fields
        list_fields = ['ipcr_list', 'cpc_list', 'inventors', 'assignees']
        for field_name in list_fields:
            list_value = getattr(self, field_name)
            if list_value is not None and not isinstance(list_value, list):
                errors.append(f"{field_name} should be of type List")

        # Check string fields
        string_fields = [
            'pub_doc_id', 'app_doc_id', 'patent_type', 'invention_title',
            'abstract'
        ]
        for field_name in string_fields:
            string_value = getattr(self, field_name)
            if string_value is not None and not isinstance(string_value, str):
                errors.append(f"{field_name} should be of type str")

        if errors:
            raise DataIntegrityError(errors)

    def __post_init__(self):
        self.check_data_integrity()


def test_data_model_success():
    patent_data = USPatent(date_produced=datetime.date(2023, 1, 1),
                           date_published=datetime.date(2023, 2, 1),
                           date_applied=datetime.date(2023, 2, 1),
                           ipcr_list=[{
                               "code": "A01B1/00"
                           }, {
                               "code": "C03C3/00"
                           }],
                           cpc_list=[{
                               "code": "A01B3/02"
                           }, {
                               "code": "C03C5/04"
                           }],
                           pub_doc_id="US1234567A",
                           app_doc_id="US9876543B",
                           patent_type="Utility",
                           invention_title="Example Invention",
                           inventors=[{
                               "name": "John Doe"
                           }, {
                               "name": "Jane Smith"
                           }],
                           assignees=[{
                               "name": "Example Inc."
                           }],
                           abstract="This is a test abstract.")

    try:
        patent_data.check_data_integrity()
        print("Data integrity check passed!")
    except DataIntegrityError as e:
        print(f"Data integrity error: {e}")


def test_data_model_fail():
    patent_data = USPatent(date_produced=datetime.date(2023, 1, 1),
                           date_published=datetime.date(2023, 2, 1),
                           date_applied=2,
                           ipcr_list=[{
                               "code": "A01B1/00"
                           }, {
                               "code": "C03C3/00"
                           }],
                           cpc_list=[{
                               "code": "A01B3/02"
                           }, {
                               "code": "C03C5/04"
                           }],
                           pub_doc_id="US1234567A",
                           app_doc_id="US9876543B",
                           patent_type="Utility",
                           invention_title="Example Invention",
                           inventors=[{
                               "name": "John Doe"
                           }, {
                               "name": "Jane Smith"
                           }],
                           assignees=[{
                               "name": "Example Inc."
                           }],
                           abstract="This is a test abstract.")

    try:
        patent_data.check_data_integrity()
        print("Data integrity check passed!")
    except DataIntegrityError as e:
        print(f"Data integrity error: {e}")

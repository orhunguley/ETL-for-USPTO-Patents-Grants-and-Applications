from dataclasses import dataclass, field
from typing import Optional, List
import datetime


@dataclass
class USPatent:
    """_summary_

    Returns:
        _type_: _description_
    """
    date_produced: datetime.date = field(default=None)
    date_published: datetime.date = field(default=None)
    date_applied: datetime.date = field(default=None)
    ipcr_list: List = field(default=None)
    cpc_list: List = field(default=None)
    pub_doc_id: str = field(default=None)
    app_doc_id: str = field(default=None)
    patent_type: str = field(default=None)
    invention_title: str = field(default=None)
    inventors: List = field(default=None)
    assignees: List = field(default=None)
    abstract: str = field(default=None)

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand

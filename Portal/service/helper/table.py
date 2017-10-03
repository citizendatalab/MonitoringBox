from typing import Dict, List
from enum import Enum


class TableSortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


class TableHeading:
    def __init__(self, name: str, order: TableSortOrder, order_setable=False):
        self.name = name
        self.order = order
        self.order_setable = order_setable

    def as_dict(self):
        return {
            "name": self.name,
            "order": self.order.value,
            "order_setable": self.order_setable
        }


class TableResponse:
    def __init__(self, count_total: int, results_per_page: int,
                 results_start_at_position: int,
                 possible_results_per_page=[10, 50, 100],
                 default_results_per_page=10):
        self._count_total = count_total
        self._results_per_page = results_per_page
        self._results_start_at_position = results_start_at_position
        self._possible_results_per_page = possible_results_per_page
        self._default_results_per_page = default_results_per_page
        self.table_headings = []  # type: List[TableHeading]
        self.table_body = []  # type: List[List[any]]

    def get_heading(self, name: str) -> TableHeading:
        out = None
        for heading in self.table_headings:
            if heading.name == name:
                out = heading
        if out is None:
            raise Exception("Heading not found")

        return out

    def as_dict(self) -> Dict:
        headings = []

        for heading in self.table_headings:
            headings.append(heading.as_dict())
        return {
            "info": {
                "count_total": str(self._count_total),
                "per_page": str(self._results_per_page),
                "current_start": str(self._results_start_at_position),
                "possible_results_per_page": self._possible_results_per_page,
                "default_results_per_page": str(self._default_results_per_page),
            },
            "headers": headings,
            "body": self.table_body
        }


def generate_table(count_total: int, results_per_page: int,
                   results_start_at_position: int,
                   table_heading: List[any],
                   possible_results_per_page=[10, 50, 100],
                   default_results_per_page=10) -> TableResponse:
    headings = []
    for heading in table_heading:
        if isinstance(heading, str):
            headings.append(TableHeading(heading, TableSortOrder.ASC))
        else:
            headings.append(heading)

    response = TableResponse(count_total, results_per_page,
                             results_start_at_position,
                             possible_results_per_page,
                             default_results_per_page)
    response.table_headings = headings
    return response

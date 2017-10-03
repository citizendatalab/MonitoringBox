from typing import Dict, List
from enum import Enum

"""
This module contains helper functions for generating tables.
"""


class TableSortOrder(Enum):
    """
    Gives the table sort order.
    """
    ASC = "ASC"
    DESC = "DESC"


class TableHeading:
    """
    Describes a table heading.
    """

    def __init__(self, name: str, order: TableSortOrder, order_setable=False):
        """
        :param name: The name of the heading.
        :param order: The order of the heading.
        :param order_setable: If the heading is changeable in order.
        """
        self.name = name
        self.order = order
        self.order_setable = order_setable

    def as_dict(self) -> Dict[str, any]:
        """
        :return: The dict representation of this heading.
        """
        return {
            "name": self.name,
            "order": self.order.value,
            "order_setable": self.order_setable
        }


class TableResponse:
    """
    Describes a table response.
    """

    def __init__(self, count_total: int, results_per_page: int,
                 results_start_at_position: int,
                 possible_results_per_page=[10, 50, 100],
                 default_results_per_page=10):
        """
        :param count_total: The total amount of results.
        :param results_per_page: The number of results that will be shown.
        :param results_start_at_position: The position it is showing from.
        :param possible_results_per_page: The different amounts of result counts.
        :param default_results_per_page: The default number of results if none was set.
        """
        self._count_total = count_total
        self._results_per_page = results_per_page
        self._results_start_at_position = results_start_at_position
        self._possible_results_per_page = possible_results_per_page
        self._default_results_per_page = default_results_per_page
        self.table_headings = []  # type: List[TableHeading]
        self.table_body = []  # type: List[List[any]]

    def get_heading(self, name: str) -> TableHeading:
        """
        Will give a table heading based on the name of the heading.

        :param name: Name of the table heading to search for.
        :return: The table heading.
        :raises Exception: When the heading wasn't found.
        """

        # Find the heading.
        out = None
        for heading in self.table_headings:
            if heading.name == name:
                out = heading

        # Return the result.
        if out is None:
            raise Exception("Heading not found")
        return out

    def as_dict(self) -> Dict:
        """
        :return: The representation of this table as a dict.
        """
        # Get the headings as a dict.
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
    """
    Will generate a table based on the given information.

    :param count_total: The total amount of results.
    :param results_per_page: The number of results per page.
    :param results_start_at_position: The current position in the results.
    :param table_heading: Heading of the table (can be string or TableHeading).
    :param possible_results_per_page: The choosable number of results.
    :param default_results_per_page: The default number of results per page.
    :return: The table without any body yet.
    """
    response = TableResponse(count_total, results_per_page,
                             results_start_at_position,
                             possible_results_per_page,
                             default_results_per_page)

    # Put all headings into the TableHeading list.
    for heading in table_heading:
        if isinstance(heading, str):
            response.table_headings.append(TableHeading(heading, TableSortOrder.ASC))
        else:
            response.table_headings.append(heading)

    return response

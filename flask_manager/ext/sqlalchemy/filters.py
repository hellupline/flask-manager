from itertools import chain
from sqlalchemy import or_
from flask_manager import controller


class SearchFilter(controller.SearchFilter):
    def __init__(self, columns, join_tables=None):
        self.columns = columns
        self.join_tables = join_tables

    def filter(self, query, value):
        clauses = [column.contains(value) for column in self.columns]
        return query.filter(or_(*clauses))


class FieldFilter(controller.FieldFilter):
    def __init__(self, column, join_tables=None):
        # I know its evil, and bad, but will inject session in
        # SQLAlchemyController.__ini__
        self.db_session = None
        self.column = column
        self.join_tables = join_tables

    def filter(self, query, value):
        return query.filter(self.column == value)

    def get_choices(self):
        values = self.db_session.query(self.column).distinct()
        for value in chain.from_iterable(values):
            title = str(value).capitalize()
            if isinstance(value, bool):
                value = str(int(value))
            yield value, title

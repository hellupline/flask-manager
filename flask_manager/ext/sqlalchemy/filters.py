from itertools import chain

import wtforms
from sqlalchemy import or_

from flask_manager.controller import Filter


class SearchFilter(Filter):
    def __init__(self, columns, join_tables=None):
        self.columns = columns
        self.join_tables = join_tables

    def filter(self, query, value):
        clauses = [column.contains(value) for column in self.columns]
        return query.filter(or_(*clauses))

    def get_form_field(self, key, query):
        return wtforms.TextField()


class ColumnFilter(Filter):
    def __init__(self, column, join_tables=None):
        self.column = column
        self.join_tables = join_tables

    def filter(self, query, value):
        return query.filter(self.column == value)

    def get_form_field(self, key, query):
        choices = [('', 'All')]
        for value in self.get_values(query):
            title = str(value).capitalize()
            if isinstance(value, bool):
                value = str(int(value))
            choices.append((value, title))
        return wtforms.SelectField(key.title(), choices=choices)

    def get_values(self, query):
        values = query.session.query(self.column).distinct()
        return chain.from_iterable(values)

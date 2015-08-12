#!/usr/bin/env python
from flask import Flask

import le_crud
import data


def build_crud():
    le_crud_admin = le_crud.Group(name='Admin', url='/admin/', items=[
        le_crud.Group(name='Aperture', url='aperture/', items=[
            le_crud.Crud(
                name='Glados', url='glados/',
                controller=data.model1_controller,
                display=data.model1_display,
            ),
            le_crud.Crud(
                name='Wheatley', url='wheatley/',
                controller=data.model1_controller,
                display=data.model1_display,
            ),
            le_crud.Crud(
                name='Chell', url='chell/',
                controller=data.model1_controller,
                display=data.model1_display,
            ),
            le_crud.Crud(
                name='Cave Johnson', url='cave-johnson/',
                controller=data.model1_controller,
                display=data.model1_display,
            ),
        ]),
        le_crud.Group(name='Black Mesa', url='black-mesa/', items=[
            le_crud.Crud(
                name='Gordon Freeman', url='gordon-freeman/',
                controller=data.model1_controller,
                display=data.model1_display,
            ),
        ]),
        le_crud.Crud(
            name='Valve', url='valve/',
            controller=data.model1_controller,
            display=data.model1_display,
        ),
    ])
    return le_crud_admin


def root():
    routes = [
        '{} -> {}'.format(rule, rule.endpoint)
        for rule in app.url_map.iter_rules()
    ]
    return '<html><body><pre>\n{}\n</pre></body></html>\n'.format(
        '\n'.join(sorted(routes)).
        replace('<', '&lt;').
        replace('>', '&gt;')
    )


if __name__ == '__main__' or True:
    app = Flask(__name__, template_folder='templates')
    app.add_url_rule('/sitemap', view_func=root)

    app.register_blueprint(build_crud().get_blueprint())

    data.metadata.create_all()
    app.run(debug=True)

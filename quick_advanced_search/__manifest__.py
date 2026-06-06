# -*- coding: utf-8 -*-
{
    'name': 'Advance Search & Quick Search',
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Dynamic advanced search fields for any Odoo model list view',
    'description': """
Advance Search & Quick Search
=============================
Define which fields should participate in quick searches for each model.

Features
--------
* Configure quick search fields for any dynamic Odoo model.
* Show configured fields directly above tree/list views.
* Choose operators such as contains, equals, starts with, ends with and between.
* Search datetime fields by date with full-day matching.
* Manager access group for Settings users.
    """,
    'author': 'Odoovix',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Odoovix',
    'support': 'odoovix@gmail.com',
    'depends': ['base', 'web'],
    'data': [
        'security/quick_search_security.xml',
        'security/ir.model.access.csv',
        'views/quick_search_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'quick_advanced_search/static/src/js/advanced_search_panel.js',
            'quick_advanced_search/static/src/xml/advanced_search_panel.xml',
            'quick_advanced_search/static/src/scss/advanced_search_panel.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

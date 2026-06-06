# -*- coding: utf-8 -*-
{
    'name': 'All-in-One Exporter',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Configurable Excel, CSV and XML exports for any Odoo model',
    'description': """
Universal Record Exporter
=========================
Build reusable export actions for Odoo records by selecting the exact fields
and related lines that should appear in each output file.

Features
--------
* Configure specific fields for any model to export.
* Add and define actions directly on target models (Action menu).
* Export data in Excel (.xlsx), CSV or XML formats.
* Support for sub-models (relational fields / order lines).
* Drag-and-drop field ordering.
    """,
   'author': 'Odoovix',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Odoovix',
    'support': 'odoovix@gmail.com',
    'depends': ['base'],
    'external_dependencies': {
        'python': ['openpyxl'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/universal_export_views.xml',
        'views/menu.xml',
    ],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

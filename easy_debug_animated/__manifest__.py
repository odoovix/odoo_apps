# -*- coding: utf-8 -*-
{
    'name': 'Easy Debug Animated',
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Throw party paper when the Odoo debug icon is clicked',
    'description': 'Adds a small celebration burst to the existing Odoo 19 debug menu button.',
    'author': 'Odoovix',
    'company': 'Odoovix',
    'maintainer': 'Odoovix',
    'support': 'odoovix@gmail.com',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Odoovix',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'easy_debug_animated/static/src/js/easy_debug_animated.js',
            'easy_debug_animated/static/src/scss/easy_debug_animated.scss',
            'easy_debug_animated/static/src/xml/easy_debug_animated.xml',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

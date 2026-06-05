# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoovix
#
#    Copyright (C) 2025-TODAY Odoovix (<https://apps.odoo.com/apps/modules/browse?author=Odoovix>)
#    Author: Odoovix (odoovix@gmail.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Easy Switch Login',
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Allow administrators to switch into any user account instantly',
    'description': 'The "Easy Switch Login" module allows administrators to '
                   'switch into any user account without passwords so they can '
                   'review access, troubleshoot issues, and validate flows.',
    'author': 'Odoovix',
    'company': 'Odoovix',
    'maintainer': 'Odoovix',
    'support': 'odoovix@gmail.com',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Odoovix',
    'depends': ['web'],
    'data': [
        'security/ir.model.access.csv',
        'views/user_selection_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'easy_switch_login/static/src/js/systray_button.js',
            'easy_switch_login/static/src/scss/systray_button.scss',
            'easy_switch_login/static/src/xml/systray_button_templates.xml',
        ]},
    'images': [
        'static/description/banner.svg'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto-install': False,
    'application': False,
}

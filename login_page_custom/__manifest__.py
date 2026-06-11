# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoovix
#
#    Copyright (C) 2026-TODAY Odoovix(<https://apps.odoo.com/apps/modules/browse?author=Odoovix>)
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
    'name': 'All in login page custom',
    'version': '17.0.2.0.1',
    'category': 'Extra Tools',
    'summary': 'Customize the Odoo 17 login page with layout and background styles',
    'description': """
All in login page custom
==========================

Customize the Odoo 17 login page from General Settings.

Main capabilities:
- Use default, left, middle, or right login box orientation.
- Set the login page background with a color, uploaded image, or image URL.
- Keep Odoo's standard login, database selector, message, and footer behavior.
- Configure branding-friendly login screens without editing Odoo core files.
    """,
    'author': 'Odoovix',
    'company': 'Odoovix',
    'maintainer': 'Odoovix',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Odoovix',
    'support': 'support@odoovix.com',
    'depends': ['base', 'base_setup', 'web'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/webclient_templates_right.xml',
        'views/webclient_templates_left.xml',
        'views/webclient_templates_middle.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

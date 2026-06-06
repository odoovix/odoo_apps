# -*- coding: utf-8 -*-
#############################################################################
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
#############################################################################
{
    'name': 'Hide Menu User',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Hide selected Odoo menu items for specific users',
    'description': 'Control menu visibility user-wise by hiding selected menu '
                   'and submenu items for specific users.',
    'author': 'Odoovix',
    'company': 'Odoovix',
    'maintainer': 'Odoovix',
    'support': 'odoovix@gmail.com',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=Odoovix',
    'depends': ['base'],
    'data': [
        'views/res_users_views.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

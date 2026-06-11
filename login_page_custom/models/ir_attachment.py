# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoovix
#
#    Copyright (C) 2026-TODAY Odoovix(<https://apps.odoo.com/apps/modules/browse?author=Odoovix>)
#    
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
from odoo import fields, models


class IrAttachment(models.Model):
    """Mark generated login background attachments."""
    _inherit = 'ir.attachment'

    is_background = fields.Boolean(
        string="Is Background",
        default=False,
        help="Technical marker for uploaded login background images.",
    )

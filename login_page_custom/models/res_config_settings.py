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
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Add login page style settings."""
    _inherit = 'res.config.settings'

    orientation = fields.Selection(selection=[('default', 'Default'),
                                              ('left', 'Left'),
                                              ('middle', 'Middle'),
                                              ('right', 'Right')],
                                   string="Orientation",
                                   help="Choose where the login box appears.",
                                   config_parameter="login_page_custom.orientation")
    background = fields.Selection(selection=[('color', 'Color Picker'),
                                             ('image', 'Image'),
                                             ('url', 'URL')],
                                  string="Background",
                                  help="Choose the login page background source.",
                                  config_parameter="login_page_custom.background")
    image = fields.Binary(string="Image",
                          help="Upload a login page background image.")
    url = fields.Char(string="URL", help="Set a background image URL.",
                      config_parameter="login_page_custom.url")
    color = fields.Char(string="Color",
                        help="Set a login page background color.",
                        config_parameter="login_page_custom.color")

    @api.model
    def get_values(self):
        """Load the stored background image."""
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(image=params.get_param('login_page_custom.image'))
        return res

    def set_values(self):
        """Save the uploaded background image."""
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('login_page_custom.image', self.image)

    @api.onchange('orientation')
    def onchange_orientation(self):
        """Hide background options when the standard Odoo login page is used."""
        if self.orientation == 'default':
            self.background = False

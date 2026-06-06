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
from odoo import fields, models, api


class ResUsers(models.Model):
    """
    Model to handle hiding specific menu items for certain users.
    """
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        if any('hide_menu_ids' in vals for vals in vals_list):
            self.env.registry.clear_cache()
        return users

    def write(self, vals):
        res = super().write(vals)
        if 'hide_menu_ids' in vals:
            self.env.registry.clear_cache()
        return res

    def _get_is_admin(self):
        """
        Compute method to check if the user is an admin.
        The Hide specific menu tab will be hidden for the Admin user form.
        """
        for rec in self:
            rec.is_admin = False
            if rec.id == self.env.ref('base.user_admin').id:
                rec.is_admin = True

    hide_menu_ids = fields.Many2many(
        'ir.ui.menu',
        'menu_hide_user_wise_rel',
        'user_id',
        'menu_id',
        string="Hidden Menu",
        store=True, help='Select menu items that need to '
                         'be hidden to this user.')
    is_admin = fields.Boolean(compute='_get_is_admin', string="Is Admin",
                              help='Check if the user is an admin.')


class IrUiMenu(models.Model):
    """
    Model to restrict the menu for specific users.
    """
    _inherit = 'ir.ui.menu'

    restrict_user_ids = fields.Many2many(
        'res.users',
        'menu_hide_user_wise_rel',
        'menu_id',
        'user_id',
        string="Restricted Users",
        help='Users restricted from accessing this menu.')

    @api.returns('self')
    def _filter_visible_menus(self):
        """
        Override to filter out menus restricted for current user.
        Applies only to the current user context.
        """
        menus = super(IrUiMenu, self)._filter_visible_menus()

        # Allow system admin to see everything
        if self.env.user.has_group('base.group_system'):
            return menus

        restricted_menu_ids = set(
            menus.sudo().filtered(
                lambda menu: self.env.user.id in menu.restrict_user_ids.ids
            ).ids
        )
        return menus.filtered(lambda menu: menu.id not in restricted_menu_ids)

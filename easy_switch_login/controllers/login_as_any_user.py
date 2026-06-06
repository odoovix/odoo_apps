# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class UserSwitch(http.Controller):
    """Controller to switch user and switch back to admin"""

    @http.route('/switch/user', type='json', auth='user')
    def user_switch(self):
        """Check if current user is admin"""
        return request.env.user._is_admin()

    @http.route('/switch/admin', type='json', auth='user')
    def switch_admin(self):
        """Switch back to previous admin user"""
        session = request.session
        pre_uid = session.get('previous_user')
        pre_user = request.env['res.users'].sudo().browse(pre_uid).exists()
        if pre_user and pre_user._is_admin():
            session.authenticate_without_password(request.env.cr.dbname,
                                                  pre_user.login, request.env)
        return True

    @http.route('/switch/user/list', type='json', auth='user')
    def user_list(self):
        """Return list of all users except the current one"""
        if not request.env.user._is_admin():
            return []
        users = request.env['res.users'].sudo().search([
            ('id', '!=', request.env.user.id),
            ('active', '=', True),
            ('share', '=', False),
        ])
        return [{'id': u.id, 'name': u.name, 'login': u.login} for u in users]

    @http.route('/switch/user/direct', type='json', auth='user')
    def switch_user_direct(self, user_id):
        """Directly switch to the selected user by id"""
        if not request.env.user._is_admin():
            return False
        user = request.env['res.users'].sudo().browse(int(user_id)).exists()
        if not user:
            return False
        session = request.session
        session.update({'previous_user': request.env.user.id})
        session.authenticate_without_password(request.env.cr.dbname,
                                              user.login, request.env)
        return True

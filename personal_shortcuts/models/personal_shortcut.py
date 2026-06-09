import re
from urllib.parse import parse_qs, urlsplit


from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class PersonalShortcut(models.Model):
    _name = "personal.shortcut"
    _description = "User Dashboard Shortcut"
    _order = "sequence, id"

    name = fields.Char(string="Name", required=True)
    url = fields.Char(string="URL", required=True)
    icon = fields.Image(string="Icon", max_width=128, max_height=128)
    use_parent_icon = fields.Boolean(string="Use Parent App Icon", default=True)
    menu_id = fields.Many2one("ir.ui.menu", string="Parent Menu", ondelete="set null")
    sequence = fields.Integer(string="Sequence", default=10)
    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user,
        required=True,
        ondelete="cascade",
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("user_id", self.env.user.id)
            vals.setdefault("use_parent_icon", True)
            if vals.get("use_parent_icon") and "menu_id" not in vals:
                vals["menu_id"] = self._guess_menu_id(vals.get("url"))
            self._check_user_ownership(vals.get("user_id"))
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if "user_id" in vals:
            self._check_user_ownership(vals["user_id"])
        if "menu_id" not in vals and len(self) == 1 and (
            "url" in vals or "use_parent_icon" in vals
        ):
            use_parent_icon = vals.get("use_parent_icon", self.use_parent_icon)
            vals["menu_id"] = (
                self._guess_menu_id(vals.get("url", self.url)) if use_parent_icon else False
            )
        return super().write(vals)

    def _check_user_ownership(self, user_id):
        if self.env.su or self.env.user.has_group("base.group_system"):
            return
        if user_id and user_id != self.env.user.id:
            raise AccessError(_("You can only manage your own shortcuts."))

    def _guess_menu_id(self, url):
        if not url:
            return False

        menu_id = self._extract_int_param(url, "menu_id")
        if menu_id:
            menu = self.env["ir.ui.menu"].browse(menu_id).exists()
            if menu:
                return menu.id

        action_id = self._extract_int_param(url, "action_id")
        if not action_id:
            match = re.search(r"/action-(\d+)(?:[/?#]|$)", url)
            action_id = int(match.group(1)) if match else False

        if action_id:
            menu = self.env["ir.ui.menu"].search(
                [("action", "like", ",%s" % action_id)],
                limit=1,
            )
            return menu.id or False

        action_path = self._extract_odoo_action_path(url)
        if action_path:
            action = self.env["ir.actions.actions"].sudo().search(
                [("path", "=", action_path)],
                limit=1,
            )
            if action:
                menu = self.env["ir.ui.menu"].search(
                    [("action", "=", "%s,%s" % (action.type, action.id))],
                    limit=1,
                )
                return menu.id or False

        return False

    def _extract_int_param(self, url, name):
        try:
            parsed = urlsplit(url)
        except ValueError:
            return False

        query_values = parse_qs(parsed.query).get(name)
        if query_values and query_values[0].isdigit():
            return int(query_values[0])

        fragment_values = parse_qs(parsed.fragment).get(name)
        if fragment_values and fragment_values[0].isdigit():
            return int(fragment_values[0])

        return False

    def _extract_odoo_action_path(self, url):
        try:
            parsed = urlsplit(url)
        except ValueError:
            return False

        prefix = "/odoo/"
        if prefix not in parsed.path:
            return False

        path = parsed.path.split(prefix, 1)[1].strip("/")
        return path.split("/", 1)[0] or False

import re

from odoo import Command, api, fields, models, _
from odoo.exceptions import AccessError, UserError



class ResUsers(models.Model):
    _inherit = "res.users"

    HEADER_COLOR_FIELDS = {
        "shortcut_header_color",
        "apps_header_color",
    }
    GLOBAL_HEADER_COLOR_FIELDS = {
        "global_shortcut_header_color",
        "global_apps_header_color",
    }
    GLOBAL_HEADER_COLOR_PARAMS = {
        "shortcuts": "personal_shortcuts.shortcut_header_color",
        "apps": "personal_shortcuts.apps_header_color",
    }
    HEADER_COLOR_SECTIONS = {
        "shortcuts": "shortcut_header_color",
        "apps": "apps_header_color",
    }
    GLOBAL_HEADER_COLOR_SECTIONS = {
        "shortcuts": "global_shortcut_header_color",
        "apps": "global_apps_header_color",
    }
    HEADER_COLOR_MODES = {"global", "personal"}

    shortcut_ids = fields.One2many(
        "personal.shortcut",
        "user_id",
        string="Shortcuts",
    )
    shortcut_color_mode = fields.Selection(
        [
            ("global", "Global Colors"),
            ("personal", "Personal Colors"),
        ],
        string="Dashboard Color Mode",
        default="global",
    )
    shortcut_header_color = fields.Char(string="Shortcuts Header Color")
    apps_header_color = fields.Char(string="Apps Header Color")
    global_shortcut_header_color = fields.Char(
        string="Global Shortcuts Header Color",
        compute="_compute_global_header_colors",
        inverse="_inverse_global_shortcut_header_color",
        readonly=False,
    )
    global_apps_header_color = fields.Char(
        string="Global Apps Header Color",
        compute="_compute_global_header_colors",
        inverse="_inverse_global_apps_header_color",
        readonly=False,
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            "shortcut_ids",
            "shortcut_color_mode",
            "shortcut_header_color",
            "apps_header_color",
            "global_shortcut_header_color",
            "global_apps_header_color",
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + [
            "shortcut_ids",
            "shortcut_color_mode",
            "shortcut_header_color",
            "apps_header_color",
            "global_shortcut_header_color",
            "global_apps_header_color",
        ]

    def write(self, values):
        values = dict(values)
        if self.HEADER_COLOR_FIELDS.intersection(values) or "shortcut_color_mode" in values:
            self._check_personal_color_access()
        if "shortcut_color_mode" in values:
            values["shortcut_color_mode"] = self._normalize_header_color_mode(
                values["shortcut_color_mode"]
            )
        for field_name in self.HEADER_COLOR_FIELDS:
            if field_name in values:
                values[field_name] = self._normalize_header_color(values[field_name])
        if not self.env.su and self == self.env.user and "shortcut_ids" in values:
            values = dict(values)
            values["shortcut_ids"] = self._sanitize_self_shortcut_commands(
                values["shortcut_ids"]
            )
        return super().write(values) if values else True

    def _sanitize_self_shortcut_commands(self, commands):
        allowed_fields = {
            "name",
            "url",
            "icon",
            "use_parent_icon",
            "menu_id",
            "sequence",
        }
        own_shortcuts = self.env["personal.shortcut"].sudo().search(
            [("user_id", "=", self.env.user.id)]
        )
        own_ids = set(own_shortcuts.ids)
        sanitized = []

        for command in commands or []:
            if not isinstance(command, (tuple, list)):
                sanitized.append(command)
                continue

            action = command[0]
            record_id = command[1] if len(command) > 1 else 0

            if action == Command.CREATE:
                vals = {
                    key: value
                    for key, value in (command[2] or {}).items()
                    if key in allowed_fields
                }
                vals["user_id"] = self.env.user.id
                sanitized.append(Command.create(vals))
            elif action == Command.UPDATE:
                self._check_own_shortcut_id(record_id, own_ids)
                vals = {
                    key: value
                    for key, value in (command[2] or {}).items()
                    if key in allowed_fields
                }
                sanitized.append(Command.update(record_id, vals))
            elif action in (Command.DELETE, Command.UNLINK, Command.LINK):
                self._check_own_shortcut_id(record_id, own_ids)
                sanitized.append(tuple(command))
            elif action == Command.SET:
                ids = command[2] or []
                for shortcut_id in ids:
                    self._check_own_shortcut_id(shortcut_id, own_ids)
                sanitized.append(Command.set(ids))
            elif action == Command.CLEAR:
                sanitized.append(Command.clear())

        return sanitized

    def _check_own_shortcut_id(self, shortcut_id, own_ids):
        if shortcut_id not in own_ids:
            raise AccessError(_("You can only manage your own shortcuts."))

    def _check_personal_color_access(self):
        if self.env.su or self.env.user.has_group("base.group_system"):
            return
        if self == self.env.user:
            return
        raise AccessError(_("You can only change your own dashboard colors."))

    def _check_global_color_access(self):
        if self.env.su or self.env.user.has_group("base.group_system"):
            return
        raise AccessError(_("Only administrators can change global dashboard colors."))

    @api.model
    def get_shortcut_dashboard_colors(self):
        user = self.env.user
        color_mode = self._normalize_header_color_mode(user.shortcut_color_mode)
        global_colors = self._get_global_header_colors()
        personal_colors = self._get_user_header_colors(user)
        effective_colors = self._get_effective_header_colors(
            color_mode, global_colors, personal_colors
        )
        return {
            "mode": color_mode,
            "can_edit_global": self.env.user.has_group("base.group_system"),
            "global": global_colors,
            "personal": personal_colors,
            "effective": effective_colors,
        }

    @api.model
    def set_shortcut_dashboard_color_mode(self, mode):
        self.env.user.write({"shortcut_color_mode": self._normalize_header_color_mode(mode)})
        return self.get_shortcut_dashboard_colors()

    @api.model
    def set_shortcut_dashboard_color(self, scope, section, color):
        field_name = self.HEADER_COLOR_SECTIONS.get(section)
        if not field_name:
            raise UserError(_("Unknown dashboard color section."))

        color = self._normalize_header_color(color)
        if scope == "global":
            self._set_global_header_color(section, color)
        elif scope == "personal":
            self.env.user.write({field_name: color})
        else:
            raise UserError(_("Unknown dashboard color scope."))

        return self.get_shortcut_dashboard_colors()

    def _compute_global_header_colors(self):
        global_colors = self._get_global_header_colors()
        for user in self:
            user.global_shortcut_header_color = global_colors["shortcuts"]
            user.global_apps_header_color = global_colors["apps"]

    def _inverse_global_shortcut_header_color(self):
        for user in self:
            user._set_global_header_color("shortcuts", user.global_shortcut_header_color)

    def _inverse_global_apps_header_color(self):
        for user in self:
            user._set_global_header_color("apps", user.global_apps_header_color)

    def _normalize_header_color(self, color):
        if not color:
            return False
        color = str(color).strip()
        if re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            return color.upper()
        return False

    def _normalize_header_color_mode(self, mode):
        return mode if mode in self.HEADER_COLOR_MODES else "global"

    def _set_global_header_color(self, section, color):
        self._check_global_color_access()
        if section not in self.GLOBAL_HEADER_COLOR_PARAMS:
            raise UserError(_("Unknown dashboard color section."))
        color = self._normalize_header_color(color)
        param_name = self.GLOBAL_HEADER_COLOR_PARAMS[section]
        self.env["ir.config_parameter"].sudo().set_param(param_name, color or "")

    def _get_section_from_global_field(self, field_name):
        for section, global_field_name in self.GLOBAL_HEADER_COLOR_SECTIONS.items():
            if global_field_name == field_name:
                return section
        raise UserError(_("Unknown dashboard color field."))

    def _get_global_header_colors(self):
        config = self.env["ir.config_parameter"].sudo()
        return {
            section: self._normalize_header_color(config.get_param(param_name))
            for section, param_name in self.GLOBAL_HEADER_COLOR_PARAMS.items()
        }

    def _get_user_header_colors(self, user):
        return {
            section: self._normalize_header_color(user[field_name])
            for section, field_name in self.HEADER_COLOR_SECTIONS.items()
        }

    def _get_effective_header_colors(self, mode, global_colors, personal_colors):
        if mode == "personal":
            return {
                section: personal_colors.get(section) or global_colors.get(section)
                for section in self.HEADER_COLOR_SECTIONS
            }
        return global_colors

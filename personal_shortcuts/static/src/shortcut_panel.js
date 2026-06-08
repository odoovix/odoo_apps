/** @odoo-module **/

import { Component, onWillStart, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { useSortable } from "@web/core/utils/sortable_owl";
import { ShortcutDialog } from "./shortcut_dialog";

export class ShortcutPanel extends Component {
    static template = "personal_shortcuts.ShortcutPanel";
    static props = {
        showAppsHeader: { type: Boolean, optional: true },
    };

    setup() {
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.menus = useService("menu");
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.user = useService("user");
        this.rootRef = useRef("shortcutRoot");

        this.state = useState({
            shortcuts: [],
            loading: true,
            dragId: null,
            shortcutHeaderColor: false,
            appsHeaderColor: false,
            globalShortcutHeaderColor: false,
            globalAppsHeaderColor: false,
            personalShortcutHeaderColor: false,
            personalAppsHeaderColor: false,
            colorMode: "global",
            canEditHeaderColors: false,
        });

        useSortable({
            ref: this.rootRef,
            elements: ".o_tsc_sortable_item",
            cursor: "move",
            delay: 500,
            tolerance: 10,
            placeholderClasses: ["o_tsc_placeholder"],
            followingElementClasses: ["o_tsc_dragging"],
            onDragStart: ({ element }) => {
                this.state.dragId = Number(element.dataset.shortcutId);
            },
            onDragEnd: () => {
                this.state.dragId = null;
            },
            onDrop: (params) => this.onSortableDrop(params),
        });

        onWillStart(async () => {
            await Promise.all([this.loadShortcuts(), this.loadHeaderColors()]);
        });
    }

    async loadShortcuts() {
        this.state.loading = true;
        try {
            this.state.shortcuts = await this.orm.searchRead(
                "personal.shortcut",
                [["user_id", "=", this.user.userId]],
                [
                    "id",
                    "name",
                    "url",
                    "icon",
                    "use_parent_icon",
                    "menu_id",
                    "sequence",
                    "write_date",
                ],
                { order: "sequence, id", context: { bin_size: true } }
            );
        } finally {
            this.state.loading = false;
        }
    }

    async loadHeaderColors() {
        const colors = await this.orm.call("res.users", "get_shortcut_dashboard_colors", []);
        this.applyHeaderColorPayload(colors);
    }

    getIconUrl(shortcut) {
        const unique = encodeURIComponent(shortcut.write_date || shortcut.id);
        return `/web/image/personal.shortcut/${shortcut.id}/icon?unique=${unique}`;
    }

    getHeaderColor(section) {
        return section === "apps" ? this.state.appsHeaderColor : this.state.shortcutHeaderColor;
    }

    getHeaderInputValue(section) {
        return this.getHeaderColor(section) || "#4B6D89";
    }

    getEditingScope() {
        return this.state.colorMode === "personal" ? "personal" : "global";
    }

    getHeaderStyle(section) {
        const color = this.getHeaderColor(section);
        if (!color) {
            return "";
        }
        const textColor = this.getTextColor(color);
        return [
            `background-color: ${color}`,
            `border-left-color: ${color}`,
            `color: ${textColor}`,
            `--o-tsc-header-bg: ${color}`,
            `--o-tsc-header-border: ${color}`,
            `--o-tsc-header-text: ${textColor}`,
        ].join("; ") + ";";
    }

    getHeaderTitleStyle(section) {
        const color = this.getHeaderColor(section);
        return color ? `color: ${this.getTextColor(color)};` : "";
    }

    previewHeaderColor(section, ev) {
        if (!this.state.canEditHeaderColors) {
            return;
        }
        const color = this.normalizeColor(ev.target.value);
        if (color) {
            this.setScopedHeaderColor(this.getEditingScope(), section, color);
            this.setEffectiveHeaderColor(section, color);
        }
    }

    async saveHeaderColor(section, ev) {
        if (!this.state.canEditHeaderColors) {
            return;
        }
        const color = this.normalizeColor(ev.target.value);
        if (!color) {
            return;
        }
        const scope = this.getEditingScope();
        this.setScopedHeaderColor(scope, section, color);
        this.setEffectiveHeaderColor(section, color);
        try {
            const colors = await this.orm.call("res.users", "set_shortcut_dashboard_color", [
                scope,
                section,
                color,
            ]);
            this.applyHeaderColorPayload(colors);
        } catch {
            this.notification.add("Could not save dashboard color.", { type: "danger" });
            await this.loadHeaderColors();
        }
    }

    async changeColorMode(ev) {
        if (!this.state.canEditHeaderColors) {
            return;
        }
        const mode = ev.target.value === "personal" ? "personal" : "global";
        this.state.colorMode = mode;
        this.applyEffectiveHeaderColors();
        try {
            const colors = await this.orm.call("res.users", "set_shortcut_dashboard_color_mode", [
                mode,
            ]);
            this.applyHeaderColorPayload(colors);
        } catch {
            this.notification.add("Could not save dashboard color mode.", { type: "danger" });
            await this.loadHeaderColors();
        }
    }

    applyHeaderColorPayload(colors = {}) {
        const globalColors = colors.global || {};
        const personalColors = colors.personal || {};
        const effectiveColors = colors.effective || {};
        this.state.colorMode = colors.mode === "personal" ? "personal" : "global";
        this.state.canEditHeaderColors = Boolean(colors.can_edit_global);
        this.state.globalShortcutHeaderColor = this.normalizeColor(globalColors.shortcuts);
        this.state.globalAppsHeaderColor = this.normalizeColor(globalColors.apps);
        this.state.personalShortcutHeaderColor = this.normalizeColor(personalColors.shortcuts);
        this.state.personalAppsHeaderColor = this.normalizeColor(personalColors.apps);
        this.state.shortcutHeaderColor = this.normalizeColor(effectiveColors.shortcuts);
        this.state.appsHeaderColor = this.normalizeColor(effectiveColors.apps);
    }

    applyEffectiveHeaderColors() {
        if (this.state.colorMode === "personal") {
            this.state.shortcutHeaderColor =
                this.state.personalShortcutHeaderColor || this.state.globalShortcutHeaderColor;
            this.state.appsHeaderColor =
                this.state.personalAppsHeaderColor || this.state.globalAppsHeaderColor;
        } else {
            this.state.shortcutHeaderColor = this.state.globalShortcutHeaderColor;
            this.state.appsHeaderColor = this.state.globalAppsHeaderColor;
        }
    }

    setScopedHeaderColor(scope, section, color) {
        if (scope === "personal") {
            if (section === "apps") {
                this.state.personalAppsHeaderColor = color;
            } else {
                this.state.personalShortcutHeaderColor = color;
            }
            return;
        }
        if (section === "apps") {
            this.state.globalAppsHeaderColor = color;
        } else {
            this.state.globalShortcutHeaderColor = color;
        }
    }

    setEffectiveHeaderColor(section, color) {
        if (section === "apps") {
            this.state.appsHeaderColor = color;
        } else {
            this.state.shortcutHeaderColor = color;
        }
    }

    normalizeColor(color) {
        return /^#[0-9a-fA-F]{6}$/.test(color || "") ? color.toUpperCase() : false;
    }

    getTextColor(color) {
        const value = color.replace("#", "");
        const red = parseInt(value.slice(0, 2), 16);
        const green = parseInt(value.slice(2, 4), 16);
        const blue = parseInt(value.slice(4, 6), 16);
        const luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255;
        return luminance > 0.62 ? "#263238" : "#FFFFFF";
    }

    getParentApp(shortcut) {
        if (!shortcut.use_parent_icon) {
            return null;
        }
        const menuId = shortcut.menu_id?.[0] || this.getMenuIdFromUrl(shortcut.url);
        const menu = menuId ? this.menus.getMenu(menuId) : null;
        if (!menu) {
            return null;
        }
        return this.menus.getMenu(menu.appID || menu.id) || menu;
    }

    getParentIconData(shortcut) {
        const iconData = this.getParentApp(shortcut)?.webIconData;
        return this.normalizeMenuIconData(iconData);
    }

    getParentIcon(shortcut) {
        const app = this.getParentApp(shortcut);
        if (!app?.webIcon || typeof app.webIcon !== "string") {
            return null;
        }
        const [iconClass, color, backgroundColor] = app.webIcon.split(",");
        return backgroundColor === undefined ? null : { iconClass, color, backgroundColor };
    }

    normalizeMenuIconData(iconData) {
        if (!iconData) {
            return false;
        }
        if (iconData.startsWith("/") || iconData.startsWith("data:image")) {
            return iconData;
        }
        const prefix = iconData.startsWith("P")
            ? "data:image/svg+xml;base64,"
            : "data:image/png;base64,";
        return prefix + iconData.replace(/\s/g, "");
    }

    getMenuIdFromUrl(url) {
        const menuId = this.getIntUrlParam(url, "menu_id");
        if (menuId && this.menus.getMenu(menuId)) {
            return menuId;
        }

        let actionId = this.getIntUrlParam(url, "action_id");
        if (!actionId) {
            const match = (url || "").match(/\/action-(\d+)(?:[/?#]|$)/);
            actionId = match ? Number(match[1]) : false;
        }
        if (!actionId) {
            return false;
        }
        const menu = this.menus.getAll().find((candidate) => candidate.actionID === actionId);
        return menu?.id || false;
    }

    getIntUrlParam(url, name) {
        try {
            const target = new URL(url || "", window.location.origin);
            const searchValue = target.searchParams.get(name);
            if (searchValue && /^\d+$/.test(searchValue)) {
                return Number(searchValue);
            }
            const hashParams = new URLSearchParams((target.hash || "").replace(/^#/, ""));
            const hashValue = hashParams.get(name);
            return hashValue && /^\d+$/.test(hashValue) ? Number(hashValue) : false;
        } catch {
            return false;
        }
    }

    openAddDialog() {
        this.dialog.add(ShortcutDialog, {
            onSave: async (data) => {
                const menuId = data.use_parent_icon ? this.getMenuIdFromUrl(data.url) : false;
                await this.orm.create("personal.shortcut", [
                    {
                        ...data,
                        menu_id: menuId,
                        user_id: this.user.userId,
                        sequence: (this.state.shortcuts.length + 1) * 10,
                    },
                ]);
                await this.loadShortcuts();
            },
        });
    }

    async navigateTo(shortcut) {
        const url = (shortcut.url || "").trim();
        if (!url) {
            return;
        }
        if (/^https?:\/\//i.test(url)) {
            try {
                const target = new URL(url, window.location.origin);
                if (target.origin === window.location.origin) {
                    window.location.assign(target.href);
                    return;
                }
            } catch {
                // Fall through to Odoo's URL action for malformed internal paths.
            }
            window.open(url, "_blank", "noopener");
            return;
        }
        await this.action.doAction({
            type: "ir.actions.act_url",
            url,
            target: "self",
        });
    }

    async onSortableDrop({ element, previous }) {
        const movedId = Number(element.dataset.shortcutId);
        if (!movedId) {
            return;
        }

        const orderedIds = this.state.shortcuts.map((shortcut) => shortcut.id);
        const fromIndex = orderedIds.indexOf(movedId);
        if (fromIndex < 0) {
            return;
        }
        orderedIds.splice(fromIndex, 1);

        if (previous) {
            const previousId = Number(previous.dataset.shortcutId);
            const previousIndex = orderedIds.indexOf(previousId);
            orderedIds.splice(previousIndex + 1, 0, movedId);
        } else {
            orderedIds.unshift(movedId);
        }

        const shortcutsById = Object.fromEntries(
            this.state.shortcuts.map((shortcut) => [shortcut.id, shortcut])
        );
        const shortcuts = orderedIds.map((shortcutId) => shortcutsById[shortcutId]);

        this.state.shortcuts = shortcuts;
        await this.saveSequence(shortcuts);
    }

    async saveSequence(shortcuts) {
        try {
            await Promise.all(
                shortcuts.map((shortcut, index) =>
                    this.orm.write("personal.shortcut", [shortcut.id], {
                        sequence: (index + 1) * 10,
                    })
                )
            );
        } catch {
            this.notification.add("Could not save shortcut order.", { type: "danger" });
            await this.loadShortcuts();
        }
    }
}

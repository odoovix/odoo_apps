/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { getDataURLFromFile } from "@web/core/utils/urls";

export class ShortcutDialog extends Component {
    static template = "personal_shortcuts.ShortcutDialog";
    static components = { Dialog };
    static props = {
        shortcut: { type: Object, optional: true },
        onSave: Function,
        close: Function,
    };

    setup() {
        this.state = useState({
            name: this.props.shortcut?.name || "",
            url: this.props.shortcut?.url || "",
            useParentIcon: this.props.shortcut?.use_parent_icon ?? true,
            icon: false,
            iconPreview:
                this.props.shortcut?.id && this.props.shortcut?.icon
                    ? `/web/image/personal.shortcut/${this.props.shortcut.id}/icon`
                    : false,
            iconChanged: false,
            isSaving: false,
        });
    }

    get title() {
        return this.props.shortcut ? "Edit Shortcut" : "Add Shortcut";
    }

    get buttonLabel() {
        return this.props.shortcut ? "Save" : "Add";
    }

    async onIconChange(ev) {
        const file = ev.target.files?.[0];
        if (!file) {
            this.state.icon = false;
            this.state.iconPreview = false;
            this.state.iconChanged = true;
            return;
        }
        const dataUrl = await getDataURLFromFile(file);
        this.state.icon = dataUrl.split(",", 2)[1] || false;
        this.state.iconPreview = dataUrl;
        this.state.iconChanged = true;
    }

    async onSave() {
        const name = this.state.name.trim();
        const url = this.state.url.trim();
        if (!name || !url || this.state.isSaving) {
            return;
        }
        this.state.isSaving = true;
        const data = {
            name,
            url,
            use_parent_icon: this.state.useParentIcon,
        };
        if (this.state.iconChanged) {
            data.icon = this.state.icon || false;
        }
        await this.props.onSave(data);
        this.props.close();
    }

}

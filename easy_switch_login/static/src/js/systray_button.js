/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";

export class UserSwitchWidget extends Component {
    static template = "easy_switch_login.UserSwitchSystray";

    setup() {
        this.rpc = useService("rpc");
        this.root = useRef("root");
        this.state = useState({
            isAdmin: false,
            open: false,
            loading: false,
            users: [],
        });
        this.onWindowClick = (ev) => {
            if (this.root.el && !this.root.el.contains(ev.target)) {
                this.state.open = false;
            }
        };

        onMounted(async () => {
            window.addEventListener("click", this.onWindowClick);
            this.state.isAdmin = await this.rpc("/switch/user", {});
        });

        onWillUnmount(() => {
            window.removeEventListener("click", this.onWindowClick);
        });
    }

    async toggleDropdown() {
        if (this.state.open) {
            this.state.open = false;
            return;
        }
        this.state.open = true;
        if (this.state.users.length === 0) {
            this.state.loading = true;
            try {
                this.state.users = await this.rpc("/switch/user/list", {});
            } finally {
                this.state.loading = false;
            }
        }
    }

    async handleSwitchClick() {
        await this.toggleDropdown();
    }

    async handleUserClick(ev) {
        const userId = parseInt(ev.currentTarget.dataset.userId, 10);
        if (!userId) {
            return;
        }
        await this.switchToUser(userId);
    }

    async switchToUser(userId) {
        this.state.open = false;
        await this.rpc("/switch/user/direct", { user_id: userId });
        location.reload();
    }

    async switchBack() {
        await this.rpc("/switch/admin", {});
        location.reload();
    }
}

const systrayItem = {
    Component: UserSwitchWidget,
};

registry.category("systray").add("UserSwitchSystray", systrayItem, { sequence: 2 });

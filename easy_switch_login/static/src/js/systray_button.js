/** @odoo-module **/
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

const { Component, useState, useRef, onMounted, onWillUnmount } = owl;

export class UserSwitchWidget extends Component {
    setup() {
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
            this.state.isAdmin = await rpc("/switch/user", {});
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
                this.state.users = await rpc("/switch/user/list", {});
            } finally {
                this.state.loading = false;
            }
        }
    }

    async switchToUser(userId) {
        this.state.open = false;
        await rpc("/switch/user/direct", { user_id: userId });
        location.reload();
    }

    async switchBack() {
        await rpc("/switch/admin", {});
        location.reload();
    }
}

UserSwitchWidget.template = "UserSwitchSystray";

registry.category("systray").add("UserSwitchSystray", {
    Component: UserSwitchWidget,
});

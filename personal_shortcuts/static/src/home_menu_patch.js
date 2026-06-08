/** @odoo-module **/

import { HomeMenu } from "@web_enterprise/webclient/home_menu/home_menu";
import { ShortcutPanel } from "./shortcut_panel";

HomeMenu.components = {
    ...HomeMenu.components,
    ShortcutPanel,
};

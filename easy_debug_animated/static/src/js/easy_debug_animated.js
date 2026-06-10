/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

const COLORS = ["#00a09d", "#875a7b", "#fbb945", "#f05a5f", "#2f80ed", "#22c55e"];
const PAPER_COUNT = 240;

function throwPartyPaper(target, fullPage = false) {
    const rect = target.getBoundingClientRect();
    const originX = rect.left + rect.width / 2;
    const originY = rect.top + rect.height / 2;
    const pageWidth = window.innerWidth;
    const pageHeight = window.innerHeight;

    for (let index = 0; index < PAPER_COUNT; index++) {
        const paper = document.createElement("span");
        const startX = fullPage ? Math.random() * pageWidth : originX;
        const startY = fullPage ? pageHeight + 30 + Math.random() * pageHeight * 0.2 : originY;
        const x = fullPage ? (Math.random() - 0.5) * 180 : (Math.random() - 0.5) * 190;
        const y = fullPage ? -pageHeight - 120 - Math.random() * 260 : -40 - Math.random() * 170;
        const rotation = Math.random() * 720 - 360;
        const width = 5 + Math.random() * 8;
        const height = 8 + Math.random() * 11;

        paper.className = "easy_debug_animated__piece";
        paper.style.left = `${startX}px`;
        paper.style.top = `${startY}px`;
        paper.style.width = `${width}px`;
        paper.style.height = `${height}px`;
        paper.style.backgroundColor = COLORS[index % COLORS.length];
        paper.style.setProperty("--dpp-x", `${x}px`);
        paper.style.setProperty("--dpp-y", `${y}px`);
        paper.style.setProperty("--dpp-r", `${rotation}deg`);
        paper.style.setProperty("--dpp-delay", `${Math.random() * 70}ms`);
        document.body.appendChild(paper);
        window.setTimeout(() => paper.remove(), 2800);
    }
}

document.addEventListener(
    "click",
    (ev) => {
        const debugButton = ev.target.closest(".o_debug_manager .dropdown-toggle");
        if (!debugButton) {
            return;
        }
        throwPartyPaper(debugButton, true);
    },
    true
);

export class DebugPartyPaperSystray extends Component {
    static template = "easy_debug_animated.Systray";

    get debugActive() {
        return Boolean(this.env.debug);
    }

    toggleDebug(ev) {
        throwPartyPaper(ev.currentTarget, true);
        window.setTimeout(() => {
            const url = new URL(window.location.href);
            if (this.debugActive) {
                url.searchParams.delete("debug");
            } else {
                url.searchParams.set("debug", "1");
            }
            window.location.href = url.toString();
        }, 520);
    }
}

registry.category("systray").add(
    "easy_debug_animated.DebugButton",
    {
        Component: DebugPartyPaperSystray,
    },
    { sequence: 1 }
);

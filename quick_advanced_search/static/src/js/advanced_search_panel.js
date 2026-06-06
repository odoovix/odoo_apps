/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { serializeDateTime } from "@web/core/l10n/dates";
import { useService } from "@web/core/utils/hooks";
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { onWillStart, useState } from "@odoo/owl";

const { DateTime } = luxon;

patch(ControlPanel.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = this.orm || useService("orm");
        this.quickAdvancedSearch = useState({
            ready: false,
            lines: [],
            values: {},
        });

        onWillStart(async () => {
            const resModel = this.env.searchModel?.resModel;
            if (!resModel || !this.orm) {
                this.quickAdvancedSearch.ready = true;
                return;
            }
            const configs = await this.orm.searchRead(
                "quick.search.config",
                [["model_name", "=", resModel], ["active", "=", true]],
                ["line_ids"],
                { limit: 1 }
            );
            if (!configs.length || !configs[0].line_ids.length) {
                this.quickAdvancedSearch.ready = true;
                return;
            }
            const lines = await this.orm.searchRead(
                "quick.search.line",
                [["id", "in", configs[0].line_ids], ["active", "=", true]],
                ["label", "field_name", "field_type", "operator"],
                { order: "sequence, id" }
            );
            this.quickAdvancedSearch.lines = lines;
            for (const line of lines) {
                this.quickAdvancedSearch.values[line.id] = this._qasEmptyValue(line);
            }
            this.quickAdvancedSearch.ready = true;
        });
    },

    get qasVisible() {
        return (
            this.env.config?.viewType === "list" &&
            this.quickAdvancedSearch?.ready &&
            this.quickAdvancedSearch.lines.length
        );
    },

    _qasEmptyValue(line) {
        return line.operator === "between" ? { start: "", end: "" } : "";
    },

    _qasOperator(line) {
        return {
            contains: "ilike",
            not_contains: "not ilike",
            equal: "=",
            not_equal: "!=",
            starts_with: "=ilike",
            ends_with: "=ilike",
            greater: ">",
            less: "<",
        }[line.operator] || "ilike";
    },

    _qasValue(line, value) {
        if (line.operator === "starts_with") {
            return `${value}%`;
        }
        if (line.operator === "ends_with") {
            return `%${value}`;
        }
        return value;
    },

    qasInputType(line) {
        return ["date", "datetime"].includes(line.field_type) ? "date" : "text";
    },

    qasPlaceholder(line) {
        return `${(line.operator || "contains").replace("_", " ")}...`;
    },

    qasSetValue(line, ev, key = null) {
        if (line.operator === "between") {
            this.quickAdvancedSearch.values[line.id][key] = ev.target.value;
        } else {
            this.quickAdvancedSearch.values[line.id] = ev.target.value;
        }
    },

    _qasDateTime(value, boundary) {
        const date = DateTime.fromISO(value);
        if (!date.isValid) {
            return false;
        }
        return serializeDateTime(boundary === "end" ? date.endOf("day") : date.startOf("day"));
    },

    _qasDateTimeStart(value) {
        return this._qasDateTime(value, "start");
    },

    _qasDateTimeEnd(value) {
        return this._qasDateTime(value, "end");
    },

    _qasPushDateDomain(domain, line, value) {
        if (line.field_type === "datetime") {
            if (line.operator === "between") {
                if (value.start) {
                    domain.push([line.field_name, ">=", this._qasDateTimeStart(value.start)]);
                }
                if (value.end) {
                    domain.push([line.field_name, "<=", this._qasDateTimeEnd(value.end)]);
                }
                return true;
            }
            if (line.operator === "equal") {
                domain.push([line.field_name, ">=", this._qasDateTimeStart(value)]);
                domain.push([line.field_name, "<=", this._qasDateTimeEnd(value)]);
                return true;
            }
        }
        if (line.field_type === "date" && line.operator === "between") {
            if (value.start) {
                domain.push([line.field_name, ">=", value.start]);
            }
            if (value.end) {
                domain.push([line.field_name, "<=", value.end]);
            }
            return true;
        }
        return false;
    },

    async qasSearch() {
        const domain = [];
        const labels = [];
        for (const line of this.quickAdvancedSearch.lines) {
            if (!line.field_name) {
                continue;
            }
            const value = this.quickAdvancedSearch.values[line.id];
            if (line.operator === "between") {
                if (!this._qasPushDateDomain(domain, line, value)) {
                    if (value.start) {
                        domain.push([line.field_name, ">=", value.start]);
                    }
                    if (value.end) {
                        domain.push([line.field_name, "<=", value.end]);
                    }
                }
                if (value.start || value.end) {
                    labels.push(`${line.label}: ${value.start || "..."} - ${value.end || "..."}`);
                }
            } else if (value !== undefined && value !== null && value !== "") {
                if (!this._qasPushDateDomain(domain, line, value)) {
                    domain.push([line.field_name, this._qasOperator(line), this._qasValue(line, value)]);
                }
                labels.push(`${line.label}: ${value}`);
            }
        }
        if (domain.length) {
            this.qasClearAdvancedFilter();
            this.env.searchModel.createNewFilters([{
                description: labels.join(", ") || "Advanced Search",
                domain,
                invisible: "True",
                qasAdvanced: true,
                tooltip: labels.join("\n") || "Advanced Search",
            }]);
        }
    },

    qasClearAdvancedFilter() {
        const searchModel = this.env.searchModel;
        if (!searchModel?.searchItems || !searchModel?.query) {
            return;
        }
        const groupIds = new Set();
        for (const queryElem of searchModel.query) {
            const item = searchModel.searchItems[queryElem.searchItemId];
            if (item?.qasAdvanced) {
                groupIds.add(item.groupId);
            }
        }
        for (const groupId of groupIds) {
            searchModel.deactivateGroup(groupId);
        }
    },

    qasReset() {
        for (const line of this.quickAdvancedSearch.lines) {
            this.quickAdvancedSearch.values[line.id] = this._qasEmptyValue(line);
        }
        this.qasClearAdvancedFilter();
        this.env.searchModel.search();
    },
});

/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class TransportDashboard extends Component {
    static template = "transport_management.TransportDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            stats: {
                total_trips: 0,
                active_trips: 0,
                total_vehicles: 0,
                total_drivers: 0,
                monthly_revenue: 0,
                monthly_expenses: 0,
                monthly_profit: 0,
            },
            currency: null,
            loading: true,
        });

        this.loadDashboardData();
    }

    async loadDashboardData() {
        try {
            // Load system currency first
            await this.getSystemCurrency();

            // Load trip statistics - use searchCount for more reliable results
            const totalTrips = await this.orm.searchCount("transport.trip", []);
            const activeTrips = await this.orm.searchCount("transport.trip", [
                ["state", "=", "in_progress"]
            ]);

            // Load vehicle count
            const vehicleCount = await this.orm.searchCount("fleet.vehicle", []);

            // Load driver count
            const driverCount = await this.orm.searchCount("hr.employee", [
                ["is_driver", "=", true]
            ]);

            // Load financial data for current month
            const currentDate = new Date();
            const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
            const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

            const monthlyRevenue = await this.orm.readGroup(
                "transport.trip.revenue",
                [
                    ["date", ">=", firstDayOfMonth.toISOString().split('T')[0]],
                    ["date", "<=", lastDayOfMonth.toISOString().split('T')[0]],
                ],
                ["amount"],
                []
            );

            const monthlyExpenses = await this.orm.readGroup(
                "transport.trip.expense",
                [
                    ["date", ">=", firstDayOfMonth.toISOString().split('T')[0]],
                    ["date", "<=", lastDayOfMonth.toISOString().split('T')[0]],
                ],
                ["amount"],
                []
            );

            const revenue = monthlyRevenue.length > 0 ? monthlyRevenue[0].amount : 0;
            const expenses = monthlyExpenses.length > 0 ? monthlyExpenses[0].amount : 0;

            this.state.stats = {
                total_trips: totalTrips,
                active_trips: activeTrips,
                total_vehicles: vehicleCount,
                total_drivers: driverCount,
                monthly_revenue: revenue,
                monthly_expenses: expenses,
                monthly_profit: revenue - expenses,
            };

        } catch (error) {
            console.error("Error loading dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    async getSystemCurrency() {
        try {
            // Get the current company
            const companies = await this.orm.searchRead(
                "res.company",
                [["id", "=", 1]], // Usually company ID 1 is the main company
                ["currency_id"]
            );

            if (companies.length > 0) {
                const currencyId = companies[0].currency_id[0];
                
                // Get currency details
                const currencies = await this.orm.searchRead(
                    "res.currency",
                    [["id", "=", currencyId]],
                    ["name", "symbol", "position"]
                );

                if (currencies.length > 0) {
                    this.state.currency = {
                        name: currencies[0].name,
                        symbol: currencies[0].symbol,
                        position: currencies[0].position
                    };
                }
            }
        } catch (error) {
            console.error("Error loading currency:", error);
            // Fallback to USD
            this.state.currency = {
                name: "USD",
                symbol: "$",
                position: "before"
            };
        }
    }

    formatCurrency(amount) {
        if (!this.state.currency) return amount.toString();
        
        const formattedAmount = amount.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        if (this.state.currency.position === 'before') {
            return `${this.state.currency.symbol}${formattedAmount}`;
        } else {
            return `${formattedAmount}${this.state.currency.symbol}`;
        }
    }

    openTrips() {
        this.action.doAction("transport_management.action_transport_trip");
    }

    openVehicles() {
        this.action.doAction("fleet.fleet_vehicle_action");
    }

    openDrivers() {
        this.action.doAction("transport_management.action_hr_employee_drivers");
    }

    openRevenues() {
        this.action.doAction("transport_management.action_transport_trip_revenue");
    }

    openExpenses() {
        this.action.doAction("transport_management.action_transport_trip_expense");
    }
}

registry.category("actions").add("transport_dashboard", TransportDashboard);

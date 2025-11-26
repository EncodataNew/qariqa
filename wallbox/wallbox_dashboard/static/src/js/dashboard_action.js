/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";

class WallboxDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.chartRefs = {
            installation: useRef("installationChart"),
            station: useRef("stationChart"),
            energy: useRef("energyChart"),
            revenue: useRef("revenueChart"),
            taskStatus: useRef("taskStatusChart"),
        };
        this.chartInstances = {};
        this.state = useState({
            summary: {},
            recentOrders: [],
            installationStatus: [],
            chargingActivity: {},
            stationStatus: [],
            alerts: {},
            loading: true,
            activeTab: "overview",
            chartLoaded: false
        });

        onWillStart(async () => {
            try {
                await loadJS("/web/static/lib/Chart/Chart.js");
                this.state.chartLoaded = true;
            } catch (error) {
                console.error("Failed to load Chart.js:", error);
            }
            await this.loadData();
        });

        onMounted(() => {
            if (this.state.chartLoaded) {
                this.renderCharts();
            }
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            const data = await rpc("/wallbox_dashboard/data");
            this.state.summary = data.summary;
            this.state.recentOrders = data.recent_orders;
            this.state.installationStatus = data.installation_status;
            this.state.chargingActivity = data.charging_activity;
            this.state.stationStatus = data.station_status;
            this.state.alerts = data.alerts;

            if (this.state.chartLoaded) {
                this.destroyCharts();
                this.renderCharts();
            }
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    destroyCharts() {
        Object.values(this.chartInstances).forEach(chart => {
            try {
                chart?.destroy();
            } catch (e) {
                console.warn("Error destroying chart:", e);
            }
        });
        this.chartInstances = {};
    }

    renderCharts() {
        if (!window.Chart) {
            console.error("Chart.js not available");
            return;
        }

        // Installation Status Chart
        if (this.state.installationStatus?.length && this.chartRefs.installation.el) {
            this.renderPieChart(
                "installation",
                this.state.installationStatus.map(item => item.state),
                this.state.installationStatus.map(item => item.state_count),
                "Installation Status"
            );
        }

        // Station Status Chart
        if (this.state.stationStatus?.length && this.chartRefs.station.el) {
            this.renderPieChart(
                "station",
                this.state.stationStatus.map(item => item.status),
                this.state.stationStatus.map(item => item.status_count),
                "Station Status"
            );
        }

        // Energy Consumption Chart
        if (this.state.chargingActivity.sessions?.length && this.chartRefs.energy.el) {
            this.renderLineChart(
                "energy",
                this.state.chargingActivity.sessions.map(s => new Date(s.start_time).toLocaleDateString()),
                this.state.chargingActivity.sessions.map(s => (s.total_energy || 0) / 1000),
                "Energy Consumption (kWh)"
            );
        }

        // Revenue Chart
        if (this.chartRefs.revenue.el) {
            this.renderRevenueChart();
        }

        if (this.chartRefs.taskStatus.el) {
            this.renderTaskStatusChart();
        }
    }

    renderPieChart(chartName, labels, data, title) {
        try {
            const ctx = this.chartRefs[chartName].el.getContext('2d');
            this.chartInstances[chartName] = new window.Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'
                        ],
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: title,
                            font: {
                                size: 14
                            }
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        } catch (error) {
            console.error(`Error rendering ${chartName} chart:`, error);
        }
    }

    renderLineChart(chartName, labels, data, title) {
        try {
            const ctx = this.chartRefs[chartName].el.getContext('2d');
            this.chartInstances[chartName] = new window.Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: title,
                        data: data,
                        backgroundColor: 'rgba(78, 115, 223, 0.05)',
                        borderColor: 'rgba(78, 115, 223, 1)',
                        pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                        lineTension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        }
                    }
                }
            });
        } catch (error) {
            console.error(`Error rendering ${chartName} chart:`, error);
        }
    } // ✅ This was missing

    renderRevenueChart() {
        try {
            const ctx = this.chartRefs.revenue.el.getContext("2d");

            this.chartInstances["revenue"] = new window.Chart(ctx, {
                type: "line",
                data: {
                    labels: ["0", "1", "2", "3", "4", "5", "6", "7"],
                    datasets: [
                        {
                            label: "Total Wallbox Order",
                            data: [1, 0.9, 0.5, 0, -0.5, -1, -0.5, 0],
                            borderColor: "#f44336",
                            backgroundColor: "rgba(244, 67, 54, 0.1)",
                            tension: 0.4,
                            fill: true,
                            pointRadius: 4
                        },
                        {
                            label: "Invoice",
                            data: [0, -0.5, -1, -0.5, 0, 0.5, 1, 0.7],
                            borderColor: "#4caf50",
                            backgroundColor: "rgba(76, 175, 80, 0.1)",
                            tension: 0.4,
                            fill: true,
                            pointRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: "bottom"
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error rendering revenue chart:", error);
        }
    }

    renderTaskStatusChart() {
        try {
            const ctx = this.chartRefs.taskStatus.el.getContext("2d");
            this.chartInstances["taskStatus"] = new window.Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: ["Condominium", "Building", "Parking Space"],
                    datasets: [{
                        data: [this.state.summary.condominium_count,this.state.summary.building_count,this.state.summary.parking_space_count],
                        backgroundColor: ["#4CAF50", "#FFC107", "#03A9F4"],
                        borderWidth: 2,
                        hoverOffset: 10,
                    }]
                },
                options: {
                    responsive: true,
                    cutout: "65%",
                    plugins: {
                        legend: { position: "right" },
                        tooltip: {
                            callbacks: {
                                label: (context) => `${context.label}: ${context.raw}%`
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error rendering task status chart:", error);
        }
    }

    openModel(model, domain) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: model,
            res_model: model,
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            domain: domain,
        });
    }
}

WallboxDashboard.template = "wallbox_dashboard.DashboardTemplate";
registry.category("actions").add("wallbox_dashboard", WallboxDashboard);

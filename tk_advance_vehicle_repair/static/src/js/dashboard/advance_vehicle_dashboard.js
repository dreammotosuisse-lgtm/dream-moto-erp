/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { session } from "@web/session";
import { Domain } from "@web/core/domain";
import { sprintf } from "@web/core/utils/strings";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;
import { loadJS, loadCSS } from "@web/core/assets"

class AdvanceVehicleDashboard extends Component {
    setup() {
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            bookingStats: { 'total_vehicle_booking': 0, 'vehicle_inspection': 0, 'vehicle_repair': 0, 'vehicle_inspection_repair': 0, 'booking_cancel': 0 },
            inspectionJobCardStatus: { 'inspection_draft': 0, 'total_inspection_job_card': 0, 'inspection_in_progress': 0, 'inspection_complete': 0, 'inspection_cancel': 0 },
            repairJobCardStatus: { 'repair_job_card': 0 },
            serviceTeams: { 'service_teams': 0 },
            vehicleCustomers: { 'vehicle_customers': 0 },
            inspectionTypes: { 'type_full_inspection': 0, 'type_specific_inspection': 0 },
            bookingDetailsStatus: { 'x-axis': [], 'y-axis': [] },
            bookingSource: { 'x-axis': [], 'y-axis': [] },
            commonVehicleFuels: { 'x-axis': [], 'y-axis': [] },
            repairStatusGraph: { 'x-axis': [], 'y-axis': [] },
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        this.bookingDetailsStatus = useRef('booking_details_graph');
        this.bookingSource = useRef('booking_source_graph');
        this.commonVehicleFuels = useRef('most_common_fuel_used_in_vehicle');
        this.repairStatusGraph = useRef('repair_status_graph');

        onWillStart(async () => {
            let bookingData = await this.orm.call('advance.vehicle.repair.dashboard', 'get_advance_vehicle_repair_dashboard', []);
            if (bookingData) {
                this.state.bookingStats = bookingData;
                this.state.inspectionJobCardStatus = bookingData;
                this.state.repairJobCardStatus = bookingData;
                this.state.serviceTeams = bookingData;
                this.state.vehicleCustomers = bookingData;
                this.state.inspectionTypes = bookingData;
                this.state.bookingDetailsStatus = { 'x-axis': bookingData['booking_details'][0], 'y-axis': bookingData['booking_details'][1] }
                this.state.bookingSource = { 'x-axis': bookingData['booking_source'][0], 'y-axis': bookingData['booking_source'][1] }
                this.state.commonVehicleFuels = { 'x-axis': bookingData['common_fuel_used_in_vehicle'][0], 'y-axis': bookingData['common_fuel_used_in_vehicle'][1] }
                this.state.repairStatusGraph = { 'x-axis': bookingData['repair_job_card_details'][0], 'y-axis': bookingData['repair_job_card_details'][1] }
            }
        });
        onMounted(() => {
            this.renderBookingDetailsGraph();
            this.renderBookingSource(this.bookingSource.el, this.state.bookingSource);
            this.renderRepairStatusGraph(this.repairStatusGraph.el, this.state.repairStatusGraph);
            this.renderCommonVehicleFuels(this.commonVehicleFuels.el, this.state.commonVehicleFuels);
        })
    }

    viewVehicleBooking(type) {
        let domain, context;
        let name = this.getBookingStatus(type);
        if (type === 'all') {
            domain = []
        } else {
            domain = [['booking_stages', '=', type]]
        }
        context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: name,
            res_model: 'vehicle.booking',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'pivot'], [false, 'activity']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getBookingStatus(type) {
        let name;
        if (type === 'all') {
            name = 'Total Bookings'
        } else if (type === 'vehicle_inspection') {
            name = 'Only Vehicles Inspection'
        } else if (type === 'vehicle_repair') {
            name = 'Only Vehicles Repair'
        } else if (type === 'vehicle_inspection_repair') {
            name = 'Vehicles Inspection and Repair'
        } else if (type === 'cancel') {
            name = 'Booking Cancelled'
        }
        return name;
    }

    viewInspectionJobCard(type) {
        let domain, context;
        let name = this.getInspectionJobCardStatus(type);
        if (type === 'all') {
            domain = []
        } else {
            domain = [['stages', '=', type]]
        }
        context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: name,
            res_model: 'inspection.job.card',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'pivot'], [false, 'activity']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getInspectionJobCardStatus(type) {
        let name;
        if (type === 'all') {
            name = 'Inspection Job Cards'
        } else if (type === 'a_draft') {
            name = 'New Inspection Job Card'
        } else if (type === 'b_in_progress') {
            name = 'Inspection In Progress'
        } else if (type === 'c_complete') {
            name = 'Inspection Completed'
        } else if (type === 'd_cancel') {
            name = 'Inspection Cancelled'
        }
        return name;
    }

    viewInspectionTypes(type) {
        let domain, context;
        let name = this.getInspectionTypes(type);
        if (type === 'all') {
            domain = []
        } else {
            domain = [['inspection_type', '=', type]]
        }
        context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: name,
            res_model: 'inspection.job.card',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'pivot'], [false, 'activity']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }
    getInspectionTypes(type) {
        let name;
        if (type === 'full_inspection') {
            name = 'Full Inspections'
        } else if (type === 'specific_inspection') {
            name = 'Specific Inspections'
        }
        return name;
    }

    viewRepairJobCard(type) {
        let context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Repair Job Cards',
            res_model: 'repair.job.card',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'pivot'], [false, 'activity']],
            target: 'current',
            context: context,
        });
    }

    viewServiceTeams() {
        let context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Service Teams',
            res_model: 'service.team',
            views: [[false, 'list'], [false, 'form'], [false, 'activity']],
            target: 'current',
            context: context,
        });
    }

    viewVehicleCustomers() {
         let context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Customers',
            res_model: 'res.partner',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'activity']],
            target: 'current',
            context: context,
        });
    }

    renderGraph(el, options) {
        const graphData = new ApexCharts(el, options);
        graphData.render();
    }

    renderBookingDetailsGraph() {
        const options = {
            series: this.state.bookingDetailsStatus['y-axis'],
            chart: {
                type: 'pie',
                height: 250
            },
            dataLabels: {
                enabled: false
            },
            labels: this.state.bookingDetailsStatus['x-axis'],
            legend: {
                position: 'bottom',
                fontSize: '10px',
                horizontalAlign: 'left',
            },
            title: {
                text: 'Booking Details',
                align: 'center',
                margin: 10,
                style: {
                    fontSize: '10px',
                    color: '#2b3547'
                },
            }
        };
        this.renderGraph(this.bookingDetailsStatus.el, options);
    }

    renderBookingSource(div, bookingData) {
        const root = am5.Root.new(div);
        root.setThemes([
            am5themes_Animated.new(root)
        ]);
        const chart = root.container.children.push(am5xy.XYChart.new(root, {
            panX: false,
            panY: false,
            wheelX: "panX",
            paddingLeft: 0,
            layout: root.verticalLayout
        }));

        const colors = chart.get("colors");
        const data = [{
            bookingSourceType: "Direct",
            value: bookingData['y-axis'][0],
            columnSettings: { fill: colors.next() }
        }, {
            bookingSourceType: "Website",
            value: bookingData['y-axis'][1],
            columnSettings: { fill: colors.next() }
        }];

        const xRenderer = am5xy.AxisRendererX.new(root, {
            minGridDistance: 30,
            minorGridEnabled: true
        })
        const xAxis = chart.xAxes.push(am5xy.CategoryAxis.new(root, {
            categoryField: "bookingSourceType",
            renderer: xRenderer,
            bullet: function (root, axis, dataItem) {
                return am5xy.AxisBullet.new(root, {
                    location: 0.5,
                    sprite: am5.Picture.new(root, {
                        width: 24,
                        height: 24,
                        centerY: am5.p50,
                        centerX: am5.p50,
                        src: dataItem.dataContext.icon
                    })
                });
            }
        }));
        xRenderer.grid.template.setAll({
            location: 1
        })
        xRenderer.labels.template.setAll({
            paddingTop: 20
        });
        xAxis.data.setAll(data);
        const yAxis = chart.yAxes.push(am5xy.ValueAxis.new(root, {
            renderer: am5xy.AxisRendererY.new(root, {
                strokeOpacity: 0.1
            })
        }));
        const series = chart.series.push(am5xy.ColumnSeries.new(root, {
            xAxis: xAxis,
            yAxis: yAxis,
            valueYField: "value",
            categoryXField: "bookingSourceType"
        }));
        series.columns.template.setAll({
            tooltipText: "{categoryX}: {valueY}",
            tooltipY: 0,
            strokeOpacity: 0,
            width: 30,
            templateField: "columnSettings"
        });
        series.data.setAll(data);
        series.appear();
        chart.appear(1000, 100);
    }

    renderCommonVehicleFuels(div, bookingData) {
        var chartData = [];
        var root = am5.Root.new(div);

        root.setThemes([
            am5themes_Animated.new(root)
        ]);

        var chart = root.container.children.push(am5percent.PieChart.new(root, {
            layout: root.verticalLayout
        }));

        var series = chart.series.push(am5percent.PieSeries.new(root, {
            valueField: "value",
            categoryField: "category"
        }));

        series.ticks.template.setAll({
            forceHidden: true,
        });
        series.labels.template.setAll({
            forceHidden: true,
        });

        for (var i = 0; i < bookingData['x-axis'].length; i++) {
            chartData.push({
                value: bookingData['y-axis'][i],
                category: bookingData['x-axis'][i],
            });
        }
        series.data.setAll(chartData);

        var legend = chart.children.push(am5.Legend.new(root, {
            centerX: am5.percent(50),
            x: am5.percent(50),
            marginTop: 15,
            marginBottom: 15
        }));

        legend.data.setAll(series.dataItems);
        series.appear(1000, 100);
    }

    renderRepairStatusGraph(div, bookingData) {
        const root = am5.Root.new(div);
        root.setThemes([
            am5themes_Animated.new(root)
        ]);
        const chart = root.container.children.push(am5xy.XYChart.new(root, {
            panX: false,
            panY: false,
            wheelX: "panX",
            paddingLeft: 0,
            layout: root.verticalLayout
        }));

        const colors = chart.get("colors");
        const data = [{
            status: "Assign",
            value: bookingData['y-axis'][0],
            columnSettings: { fill: colors.next() }
        }, {
            status: "In Diagnosis",
            value: bookingData['y-axis'][1],
            columnSettings: { fill: colors.next() }
        }, {
            status: "In Inspection",
            value: bookingData['y-axis'][2],
            columnSettings: { fill: colors.next() }
        }, {
            status: "Hold",
            value: bookingData['y-axis'][3],
            columnSettings: { fill: colors.next() }
        }, {
            status: "Completed",
            value: bookingData['y-axis'][4],
            columnSettings: { fill: colors.next() }
        }, {
            status: "Cancelled",
            value: bookingData['y-axis'][5],
            columnSettings: { fill: colors.next() }
        }];

        const xRenderer = am5xy.AxisRendererX.new(root, {
            minGridDistance: 30,
            minorGridEnabled: true
        })
        const xAxis = chart.xAxes.push(am5xy.CategoryAxis.new(root, {
            categoryField: "status",
            renderer: xRenderer,
            bullet: function (root, axis, dataItem) {
                return am5xy.AxisBullet.new(root, {
                    location: 0.5,
                    sprite: am5.Picture.new(root, {
                        width: 24,
                        height: 24,
                        centerY: am5.p50,
                        centerX: am5.p50,
                        src: dataItem.dataContext.icon
                    })
                });
            }
        }));
        xRenderer.grid.template.setAll({
            location: 1
        })
        xRenderer.labels.template.setAll({
            paddingTop: 20
        });
        xAxis.data.setAll(data);
        const yAxis = chart.yAxes.push(am5xy.ValueAxis.new(root, {
            renderer: am5xy.AxisRendererY.new(root, {
                strokeOpacity: 0.1
            })
        }));
        const series = chart.series.push(am5xy.ColumnSeries.new(root, {
            xAxis: xAxis,
            yAxis: yAxis,
            valueYField: "value",
            categoryXField: "status"
        }));
        series.columns.template.setAll({
            tooltipText: "{categoryX}: {valueY}",
            tooltipY: 0,
            strokeOpacity: 0,
            width: 30,
            templateField: "columnSettings"
        });
        series.data.setAll(data);
        series.appear();
        chart.appear(1000, 100);
    }

}
AdvanceVehicleDashboard.template = "tk_advance_vehicle_repair.adv_dashboard";
registry.category("actions").add("advance_vehicle_repair_dashboard", AdvanceVehicleDashboard);
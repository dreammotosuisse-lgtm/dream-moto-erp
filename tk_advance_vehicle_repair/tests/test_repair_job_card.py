import datetime
import psycopg2
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from .common import VehicleRepairData


@tagged("repair_job_card")
class TestRepairJobCard(VehicleRepairData):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.repair_job_card = cls._create_repair_job_card({
            "customer_id": cls.customer.id, "vehicle_brand_id":
            cls.vehicle_brand.id, "vehicle_model_id": cls.vehicle_model.id,
            "vehicle_fuel_type_id": cls.fuel_type.id,
            "registration_no": "613211621354", "email": "Email@gmail.com",
            "street": "Street One", "street2": "Street Two",
            "city": "City", "country_id": 104, "state_id": 12,
            "zip": "305013", "phone": "1234567890", })
        cls.vehicle_service_team_one = cls._create_vehicle_service_team({
            "vehicle_service_id": cls.vehicle_service_one.id,
            "vehicle_service_team_members_ids": [
                (6, 0, [cls.user.id])], "start_date": datetime.datetime.today().
            date(), "end_date": datetime.datetime.today().
            date() + relativedelta(days=1), "service_charge": 10,
            "repair_job_card_id": cls.repair_job_card.id})
        cls.repair_check_list = cls._create_repair_checklist({
            "name": "RC", "description": "Description", "repair_job_card_id":
            cls.repair_job_card.id})
        cls.repair_check_list_two = cls._create_repair_checklist({
            "name": "RC", "description": "Description", "repair_job_card_id":
            cls.repair_job_card.id})
        cls.repair_spare_part = cls._create_vehicle_order_spare_part({
            "product_id": cls.product.id, "qty": 3, "unit_price": 10,
            "repair_job_card_id": cls.repair_job_card.id, })

    def test_create_job_card(self):
        self.assertTrue(self.repair_job_card)
        with self.assertLogs("odoo.sql_db", level="ERROR"):
            with self.assertRaises(psycopg2.errors.NotNullViolation):
                self._create_repair_job_card({})
        self.assertNotEqual(self.repair_job_card.sequence_number, 'New')

    def test_write_methods(self):
        self.repair_job_card.write({})
        self.assertEqual(self.customer.street, "Street One")
        self.assertEqual(self.customer.street2, "Street Two")
        self.assertEqual(self.customer.city, "City")
        self.assertEqual(self.customer.country_id.id, 104)
        self.assertEqual(self.customer.state_id.id, 12)
        self.assertEqual(self.customer.zip, "305013")
        self.assertEqual(self.customer.phone, "1234567890")
        self.assertEqual(self.customer.email, "Email@gmail.com")

    def test_expand_groups(self):
        data = self.repair_job_card._expand_groups(None, None)
        for val in ('draft', 'assign_to_technician', 'in_diagnosis',
                    'supervisor_inspection', 'reject', 'complete', 'hold',
                    'locked', 'cancel'):
            self.assertIn(val, data)


    def test_assign_to_technician_to_in_diagnosis(self):
        self.repair_job_card.assign_to_technician_to_in_diagnosis()
        self.assertEqual(self.repair_job_card.stages, 'in_diagnosis')

    def test_in_diagnosis_to_supervisor_inspection(self):
        message = self.repair_job_card.in_diagnosis_to_supervisor_inspection()
        self.assertIsInstance(message, dict)
        self.assertEqual(message["params"]["message"],
                         "Please complete all team tasks")
        self.repair_job_card.vehicle_service_team_ids[0].work_is_done = \
            True
        self.repair_job_card.in_diagnosis_to_supervisor_inspection()
        self.assertEqual(self.repair_job_card.stages, 'supervisor_inspection')

    def test_supervisor_inspection_to_reject(self):
        self.repair_job_card.vehicle_service_team_ids[0].work_is_done = \
            True
        self.repair_job_card.supervisor_inspection_to_reject()
        self.assertEqual(self.repair_job_card.stages, 'reject')
        self.assertFalse(
            self.vehicle_service_team_one.team_task_id.work_is_done)

    def test_reject_to_complete(self):
        message = self.repair_job_card.reject_to_complete()
        self.assertIsInstance(message, dict)
        self.assertEqual(message["params"]["message"],
                         "Please complete the checklist template")
        for rec in self.repair_job_card.repair_checklist_ids:
            rec.display_type = "line_section"
            rec.is_check = True
        self.repair_job_card.reject_to_complete()
        self.assertEqual(self.repair_job_card.stages, "complete")

    def test_complete_to_hold(self):
        self.repair_job_card.complete_to_hold()
        self.assertEqual(self.repair_job_card.stages, "hold")

    def test_complete_to_locked(self):
        self.repair_job_card.complete_to_locked()
        self.assertEqual(self.repair_job_card.stages, "locked")

    def test_hold_to_cancel(self):
        self.repair_job_card.hold_to_cancel()
        self.assertEqual(self.repair_job_card.stages, "cancel")

    def test_onchange_fleet_vehicle(self):

        fleet_brand = self.env["fleet.vehicle.model.brand"].create({
            "name": "Fleet Brand", })
        fleet_model = self.env['fleet.vehicle.model'].create({
            "name": "Fleet Model", "brand_id": fleet_brand.id})
        fleet = self.env["fleet.vehicle"].create({
            "model_id": fleet_model.id, "license_plate": "License",
            "vehicle_brand_id": self.vehicle_brand.id, "vehicle_fuel_type_id":
            self.fuel_type.id, "vehicle_model_id": self.vehicle_model.id,
            "vin_no": "123", "transmission_type": "manual"})
        self.repair_job_card._onchange_fleet_vehicle()
        self.assertFalse(self.repair_job_card.vehicle_brand_id)
        self.assertFalse(self.repair_job_card.vehicle_model_id)
        self.assertFalse(self.repair_job_card.vehicle_fuel_type_id)
        self.assertFalse(self.repair_job_card.transmission_type)
        self.assertFalse(self.repair_job_card.registration_no)
        self.assertFalse(self.repair_job_card.vin_no)
        self.repair_job_card.vehicle_from = "fleet_vehicle"
        self.repair_job_card.fleet_vehicle_id = fleet.id
        self.repair_job_card._onchange_fleet_vehicle()
        self.assertEqual(self.repair_job_card.vehicle_brand_id.id,
                         fleet.vehicle_brand_id.id)
        self.assertEqual(self.repair_job_card.vehicle_model_id.id,
                         fleet.vehicle_model_id.id)
        self.assertEqual(self.repair_job_card.vehicle_fuel_type_id.id,
                         fleet.vehicle_fuel_type_id.id)
        self.assertEqual(self.repair_job_card.transmission_type,
                         fleet.transmission_type)
        self.assertEqual(self.repair_job_card.registration_no,
                         fleet.license_plate)
        self.assertEqual(self.repair_job_card.vin_no, fleet.vin_no)

    def test_onchange_customer_vehicle(self):
        self.repair_job_card._onchange_customer_vehicle()
        self.assertFalse(self.repair_job_card.vehicle_brand_id)
        self.assertFalse(self.repair_job_card.vehicle_model_id)
        self.assertFalse(self.repair_job_card.vehicle_fuel_type_id)
        self.assertFalse(self.repair_job_card.transmission_type)
        self.assertFalse(self.repair_job_card.registration_no)
        self.assertFalse(self.repair_job_card.vin_no)
        self.repair_job_card.register_vehicle_id = self.register_vehicle.id
        self.repair_job_card.vehicle_from = 'customer_vehicle'
        self.repair_job_card._onchange_customer_vehicle()
        self.assertEqual(self.repair_job_card.vehicle_brand_id.id,
                         self.register_vehicle.vehicle_brand_id.id)
        self.assertEqual(self.repair_job_card.vehicle_model_id.id,
                         self.register_vehicle.vehicle_model_id.id)
        self.assertEqual(self.repair_job_card.vehicle_fuel_type_id.id,
                         self.register_vehicle.vehicle_fuel_type_id.id)
        self.assertEqual(self.repair_job_card.transmission_type,
                         self.register_vehicle.transmission_type)
        self.assertEqual(self.repair_job_card.registration_no,
                         self.register_vehicle.registration_no)
        self.assertEqual(self.repair_job_card.vin_no,
                         self.register_vehicle.vin_no)

    def test_onchange_vehicle_brand_id(self):
        self.assertTrue(self.repair_job_card.vehicle_brand_id)
        self.repair_job_card.vehicle_brand_id = False
        self.repair_job_card._onchange_vehicle_brand_id()
        self.assertFalse(self.repair_job_card.vehicle_fuel_type_id)
        self.assertFalse(self.repair_job_card.vehicle_model_id)

    def test_onchange_vehicle_model_id(self):
        self.assertTrue(self.repair_job_card.vehicle_model_id)
        self.repair_job_card.vehicle_model_id = False
        self.repair_job_card._onchange_vehicle_model_id()
        self.assertFalse(self.repair_job_card.vehicle_fuel_type_id)

    def test_onchange_customer_details(self):
        self.assertTrue(self.repair_job_card.customer_id)
        self.repair_job_card._onchange_customer_details()
        self.assertEqual(self.repair_job_card.phone, self.customer.phone)
        self.assertEqual(self.repair_job_card.email, self.customer.email)
        self.assertEqual(self.repair_job_card.street, self.customer.street)
        self.assertEqual(self.repair_job_card.street2, self.customer.street2)
        self.assertEqual(self.repair_job_card.city, self.customer.city)
        self.assertEqual(self.repair_job_card.state_id.id,
                         self.customer.state_id.id)
        self.assertEqual(self.repair_job_card.country_id.id,
                         self.customer.country_id.id)
        self.assertEqual(self.repair_job_card.zip, self.customer.zip)
        self.assertFalse(self.repair_job_card.register_vehicle_id)
        self.assertFalse(self.repair_job_card.fleet_vehicle_id)

    def test_onchange_check_list_template_id(self):
        self.repair_job_card.check_list_template_id = self.checklist_template.id
        self.repair_job_card._onchange_check_list_template_id()
        self.assertEqual(len(self.repair_job_card.repair_checklist_ids), 5)
        for name in self.checklist_template.checklist_template_item_ids.mapped(
                'name'):
            self.assertIn(
                name, self.repair_job_card.repair_checklist_ids.mapped(
                    'name'))

    def test_compute_service_charge(self):
        self.repair_job_card._compute_service_charge()
        self.assertEqual(self.repair_job_card.service_charge, 10)

    def test_compute_spare_part_price(self):
        self.repair_job_card._compute_spare_part_price()
        self.assertEqual(self.repair_job_card.part_price, 30)

    def test_compute_sub_total(self):
        self.repair_job_card._compute_sub_total()
        self.assertEqual(self.repair_job_card.sub_total, 40)

    def test_compute_vehicle_booking(self):
        booking = self._create_booking({
            "customer_id": self.customer.id, "vehicle_brand_id":
            self.vehicle_brand.id, "registration_no": "12345",
            "vehicle_model_id": self.vehicle_model.id, "vehicle_fuel_type_id":
            self.fuel_type.id,
            "street": "Street One", "street2": "Street Two",
            "city": "City", "country_id": 104, "state_id": 12,
            "zip": "305013", "phone": "1234567890", "email": "Email@gmail.com",
            "repair_job_card_id": self.repair_job_card.id})
        self.repair_job_card._compute_vehicle_booking()
        self.assertEqual(
            self.repair_job_card.vehicle_booking_id.id, booking.id)

    def test_action_create_vehicle_registration(self):
        self.repair_job_card.action_create_vehicle_registration()
        self.assertTrue(self.repair_job_card.register_vehicle_id)
        register_vehicle = self.repair_job_card.register_vehicle_id
        self.assertEqual(register_vehicle.customer_id.id,
                         self.repair_job_card.customer_id.id)
        self.assertEqual(register_vehicle.vehicle_brand_id.id,
                         self.repair_job_card.vehicle_brand_id.id)
        self.assertEqual(register_vehicle.vehicle_model_id.id,
                         self.repair_job_card.vehicle_model_id.id)
        self.assertEqual(register_vehicle.vehicle_fuel_type_id.id,
                         self.repair_job_card.vehicle_fuel_type_id.id)
        self.assertEqual(register_vehicle.registration_no,
                         self.repair_job_card.registration_no)
        self.assertEqual(register_vehicle.vin_no, self.repair_job_card.vin_no)
        self.assertEqual(register_vehicle.transmission_type,
                         self.repair_job_card.transmission_type)

        self.repair_job_card.vehicle_brand_id = False
        self.repair_job_card.vehicle_model_id = False
        message = self.repair_job_card.action_create_vehicle_registration()
        self.assertIsInstance(message, dict)

    def test_compute_team_task_count(self):
        self.repair_job_card.assign_to_technician_to_in_diagnosis()
        self.repair_job_card._compute_team_task_count()
        self.assertEqual(self.repair_job_card.team_task_count, 1)

    def test_view_team_tasks(self):
        action = self.repair_job_card.view_team_tasks()
        self.assertIsInstance(action, dict)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Tasks")
        self.assertEqual(action["view_mode"],
                         "list,form,kanban,calendar,pivot,graph,activity")
        self.assertEqual(action["res_model"], "project.task")
        team_task_ids = self.repair_job_card.inspection_job_card_id. \
            inspection_repair_team_ids.mapped('team_task_id').ids
        self.assertIn('|', action.get('domain', []))
        self.assertIn(('repair_job_card_id', '=', self.repair_job_card.id),
                      action.get('domain', []))
        self.assertIn(('id', 'in', team_task_ids), action.get('domain', []))
        self.assertFalse(action["context"]["create"])

    def test_compute_vehicle_inspection_job_card(self):
        inspection_job_card = self._create_inspection_job_card({
            "vehicle_brand_id": self.vehicle_brand.id, "vehicle_model_id":
            self.vehicle_model.id, "vehicle_fuel_type_id": self.fuel_type.id,
            "customer_id": self.customer.id, "email": "Email@gmail.com",
            "street": "Street One", "street2": "Street Two",
            "city": "City", "country_id": 104, "state_id": 12,
            "zip": "305013", "phone": "1234567890", "inspect_type":
            "only_inspection", "vin_no":
            "1234", "transmission_type": "automatic", "repair_job_card_id":
            self.repair_job_card.id})
        self.repair_job_card._compute_vehicle_inspection_job_card()
        self.assertEqual(self.repair_job_card.inspection_job_card_id.id,
                         inspection_job_card.id)

    def test_action_repair_sale_order(self):
        action = self.repair_job_card.action_repair_sale_order()
        self.assertIsInstance(action, dict)
        self.assertEqual(action["type"], 'ir.actions.act_window')
        self.assertEqual(action["name"], 'Sale Order')
        self.assertEqual(action["res_model"], 'sale.order')
        self.assertEqual(action["view_mode"], 'form')
        self.assertEqual(action["target"], 'current')
        sale_order = self.env["sale.order"].browse(action["res_id"])
        self.assertEqual(sale_order.amount_untaxed, 40)
        self.assertEqual(sale_order.amount_total, 40)

        self.repair_job_card.vehicle_service_team_ids = False
        message = self.repair_job_card.action_repair_sale_order()
        self.assertIsInstance(message, dict)
        self.assertEqual(message["params"]["message"],
                         "Please add the necessary services.")
        self.repair_job_card.vehicle_order_spare_part_ids = False
        message = self.repair_job_card.action_repair_sale_order()
        self.assertIsInstance(message, dict)

    def test_update_repair_quotation(self):
        message = self.repair_job_card.update_repair_quotation()
        self.assertIsInstance(message, dict)
        for val in ('type', 'tag', 'params'):
            self.assertIn(val, message)
        self.assertEqual(message["type"], "ir.actions.client")
        self.assertEqual(message["tag"], "display_notification")
        self.assertEqual(message["params"]["type"], "success")
        self.assertEqual(message["params"]["message"],
                         "Quotation is successfully updated")
        self.assertFalse(message["params"]["sticky"])

    def test_compute_repair_delivery_orders(self):
        self.repair_job_card.action_repair_sale_order()
        self.repair_job_card.repair_sale_order_id.action_confirm()
        self.repair_job_card._compute_repair_delivery_orders()
        self.assertEqual(self.repair_job_card.repair_delivery_orders, 0)

    def test_action_view_repair_delivery(self):
        action = self.repair_job_card.action_view_repair_delivery()
        self.assertIsInstance(action, dict)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Delivery")
        self.assertEqual(action["res_model"], "stock.picking")
        self.assertIn(('id', 'in', self.repair_job_card.repair_sale_order_id.
                       picking_ids.ids), action.get("domain", []))
        self.assertEqual(action["view_mode"], "list,form,kanban")
        self.assertEqual(action["target"], "current")
        self.assertFalse(action["context"]["create"])

    def test_create_repair_job_card_invoice(self):
        self.repair_job_card.action_repair_sale_order()
        self.repair_job_card.repair_sale_order_id.action_confirm()
        invoice = self.repair_job_card.create_repair_job_card_invoice()
        self.assertEqual(invoice.amount_residual, 40)
        self.repair_job_card._compute_repair_invoices()
        self.assertEqual(self.repair_job_card.repair_invoices, 1)

    def test_view_repair_invoice(self):
        action = self.repair_job_card.view_repair_invoice()
        self.assertIsInstance(action, dict)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Invoices")
        self.assertEqual(action["res_model"], "account.move")
        self.assertIn(('repair_job_card_id', '=', self.repair_job_card.id),
                      action.get("domain", []))
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["target"], "current")
        self.assertFalse(action["context"]["create"])

    def test_unlink(self):
        self.repair_job_card.stages = 'locked'
        with self.assertRaisesRegex(ValidationError, 'You cannot delete the '
                                    'locked order.'):
            self.repair_job_card.unlink()

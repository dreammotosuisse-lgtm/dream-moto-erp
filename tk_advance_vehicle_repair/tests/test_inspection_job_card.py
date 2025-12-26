import datetime
import psycopg2
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from .common import VehicleRepairData


@tagged("inspection_job_card")
class TestInspectionJobCard(VehicleRepairData):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspection_job_card = cls._create_inspection_job_card({
            "vehicle_brand_id": cls.vehicle_brand.id, "vehicle_model_id":
            cls.vehicle_model.id, "vehicle_fuel_type_id": cls.fuel_type.id,
            "customer_id": cls.customer.id, "email": "Email@gmail.com",
            "street": "Street One", "street2": "Street Two",
            "city": "City", "country_id": 104, "state_id": 12,
            "zip": "305013", "phone": "1234567890", "inspect_type":
            "only_inspection", "vin_no":
            "1234", "transmission_type": "automatic"})
        cls.booking = cls._create_booking({
            "customer_id": cls.customer.id, "vehicle_brand_id":
            cls.vehicle_brand.id, "registration_no": "12345",
            "vehicle_model_id": cls.vehicle_model.id, "vehicle_fuel_type_id":
            cls.fuel_type.id, "inspection_job_card_id":
            cls.inspection_job_card.id})
        cls.inspection_checklist = cls._create_inspection_checklist({
            "name": "IT", "description": "Description",
            "inspection_job_card_id": cls.inspection_job_card.id, })
        cls.inspection_repair_team_one = cls._create_inspection_repair_team({
            "vehicle_service_id": cls.vehicle_service_one.id,
            "inspection_job_card_id": cls.inspection_job_card.id})
        cls.inspection_repair_team_two = cls._create_inspection_repair_team({
            "vehicle_service_id": cls.vehicle_service_two.id,
            "inspection_job_card_id": cls.inspection_job_card.id})
        cls.inspection_spare_part = cls._create_vehicle_spare_part({
            "product_id": cls.product.id, "qty": 2,  "inspection_job_card_id":
            cls.inspection_job_card.id})
        cls.inspection_spare_part_two = cls._create_vehicle_spare_part({
            "product_id": cls.product_two.id, "qty": 2,
            "inspection_job_card_id": cls.inspection_job_card.id})

    def test_create_method(self):
        self.assertNotEqual(self.inspection_job_card.inspection_number, "New")
        with self.assertLogs("odoo.sql_db", level="ERROR"):
            with self.assertRaises(psycopg2.errors.NotNullViolation):
                self._create_inspection_job_card({})

    def test_write_method(self):
        self.inspection_job_card.write({})
        self.assertEqual(self.customer.street, "Street One")
        self.assertEqual(self.customer.street2, "Street Two")
        self.assertEqual(self.customer.city, "City")
        self.assertEqual(self.customer.country_id.id, 104)
        self.assertEqual(self.customer.state_id.id, 12)
        self.assertEqual(self.customer.zip, "305013")
        self.assertEqual(self.customer.phone, "1234567890")
        self.assertEqual(self.customer.email, "Email@gmail.com")

    def test_expand_groups(self):
        data = self.inspection_job_card._expand_groups(None, None)
        for val in ('a_draft', 'b_in_progress', 'in_review', 'reject',
                    'c_complete', 'locked', 'd_cancel'):
            self.assertIn(val, data)

    def test_stage_action_buttons(self):

        # a_draft_to_b_in_progress ---------------------------------------------
        self.inspection_job_card.a_draft_to_b_in_progress()
        self.assertEqual(self.inspection_job_card.stages, 'b_in_progress')

        # b_in_progress_to_in_review -------------------------------------------
        self.inspection_job_card.b_in_progress_to_in_review()
        self.assertEqual(self.inspection_job_card.stages, 'in_review')
        self.assertFalse(self.inspection_job_card.is_skip_quotation)

        # skip_quotation -------------------------------------------------------
        self.inspection_job_card.skip_quotation()
        self.assertEqual(self.inspection_job_card.stages, 'in_review')
        self.assertFalse(self.inspection_job_card.is_skip_quotation)

        # in_review_to_reject --------------------------------------------------
        self.inspection_job_card.in_review_to_reject()
        self.assertEqual(self.inspection_job_card.stages, "reject")

        # reject_to_c_complete -------------------------------------------------
        message = self.inspection_job_card.reject_to_c_complete()
        self.assertIsInstance(message, dict)
        for val in ('type', 'tag', 'params'):
            self.assertIn(val, message)
        self.assertEqual(message["type"], "ir.actions.client")
        self.assertEqual(message["tag"], "display_notification")
        self.assertEqual(message["params"]["type"], "warning")
        self.assertEqual(message["params"]["message"],
                         "Please complete the checklist template")
        self.assertFalse(message["params"]["sticky"])

        self.inspection_job_card.inspection_checklist_ids[0].display_type = \
            "line_section"

        self.inspection_job_card.inspection_checklist_ids[0].is_check = \
            True
        self.inspection_job_card.reject_to_c_complete()
        self.assertFalse(self.inspection_job_card.is_skip_quotation)
        self.assertEqual(self.inspection_job_card.stages, "c_complete")

        # c_complete_to_d_cancel -----------------------------------------------
        self.inspection_job_card.c_complete_to_d_cancel()
        self.assertEqual(self.inspection_job_card.stages, "d_cancel")

        # d_cancel_to_locked ---------------------------------------------------
        self.inspection_job_card.d_cancel_to_locked()
        self.assertEqual(self.inspection_job_card.stages, 'locked')

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
        self.inspection_job_card.fleet_vehicle_id = fleet.id
        self.inspection_job_card.vehicle_from = "fleet_vehicle"
        self.inspection_job_card._onchange_fleet_vehicle()
        self.assertEqual(self.inspection_job_card.vehicle_brand_id.id,
                         fleet.vehicle_brand_id.id)
        self.assertEqual(self.inspection_job_card.vehicle_model_id.id,
                         fleet.vehicle_model_id.id)
        self.assertEqual(self.inspection_job_card.vehicle_fuel_type_id.id,
                         fleet.vehicle_fuel_type_id.id)
        self.assertEqual(self.inspection_job_card.transmission_type,
                         fleet.transmission_type)
        self.assertEqual(self.inspection_job_card.registration_no,
                         fleet.license_plate)
        self.assertEqual(self.inspection_job_card.vin_no,
                         fleet.vin_no)
        self.inspection_job_card.fleet_vehicle_id = None
        self.inspection_job_card._onchange_fleet_vehicle()
        self.assertFalse(self.inspection_job_card.vehicle_brand_id)
        self.assertFalse(self.inspection_job_card.vehicle_model_id)
        self.assertFalse(self.inspection_job_card.vehicle_fuel_type_id)
        self.assertFalse(self.inspection_job_card.transmission_type)
        self.assertFalse(self.inspection_job_card.registration_no)
        self.assertFalse(self.inspection_job_card.vin_no)

    def test_onchange_customer_vehicle(self):
        self.inspection_job_card.register_vehicle_id = self.register_vehicle.id
        self.inspection_job_card.vehicle_from = "customer_vehicle"
        self.inspection_job_card._onchange_customer_vehicle()
        self.assertEqual(self.inspection_job_card.vehicle_brand_id.id,
                         self.vehicle_brand.id)
        self.assertEqual(self.inspection_job_card.vehicle_model_id.id,
                         self.vehicle_model.id)
        self.assertEqual(self.inspection_job_card.vehicle_fuel_type_id.id,
                         self.fuel_type.id)
        self.assertEqual(self.inspection_job_card.transmission_type,
                         "automatic")
        self.assertEqual(self.inspection_job_card.registration_no,
                         "1234567890")
        self.assertEqual(self.inspection_job_card.vin_no, "123456789")

        self.inspection_job_card.register_vehicle_id = None
        self.inspection_job_card._onchange_customer_vehicle()
        self.assertFalse(self.inspection_job_card.vehicle_brand_id)
        self.assertFalse(self.inspection_job_card.vehicle_model_id)
        self.assertFalse(self.inspection_job_card.vehicle_fuel_type_id)
        self.assertFalse(self.inspection_job_card.transmission_type)
        self.assertFalse(self.inspection_job_card.registration_no)
        self.assertFalse(self.inspection_job_card.vin_no)

    def test_onchange_vehicle_brand_id(self):
        self.inspection_job_card.vehicle_brand_id = False
        self.inspection_job_card._onchange_vehicle_brand_id()
        self.assertFalse(self.inspection_job_card.vehicle_fuel_type_id)
        self.assertFalse(self.inspection_job_card.vehicle_model_id)

    def test_onchange_vehicle_model_id(self):
        self.inspection_job_card.vehicle_model_id = False
        self.inspection_job_card._onchange_vehicle_model_id()
        self.assertFalse(self.inspection_job_card.vehicle_fuel_type_id)

    def test_onchange_customer_details(self):
        self.inspection_job_card._onchange_customer_details()
        self.assertEqual(self.inspection_job_card.phone, self.customer.phone)
        self.assertEqual(self.inspection_job_card.email, self.customer.email)
        self.assertEqual(self.inspection_job_card.street, self.customer.street)
        self.assertEqual(self.inspection_job_card.street2,
                         self.customer.street2)
        self.assertEqual(self.inspection_job_card.city, self.customer.city)
        self.assertEqual(self.inspection_job_card.state_id.id,
                         self.customer.state_id.id)
        self.assertEqual(self.inspection_job_card.country_id.id,
                         self.customer.country_id.id)
        self.assertEqual(self.inspection_job_card.zip, self.customer.zip)

    def test_onchange_check_list_template_id(self):
        self.inspection_job_card.check_list_template_id = \
            self.checklist_template.id
        self.inspection_job_card._onchange_check_list_template_id()
        self.assertEqual(len(self.inspection_job_card.inspection_checklist_ids),
                         5)
        for name in self.checklist_template.checklist_template_item_ids.mapped(
                'name'):
            self.assertIn(
                name, self.inspection_job_card.inspection_checklist_ids.mapped(
                    'name'))

    def test_onchange_inspection_report_type(self):
        self.inspection_job_card._onchange_inspection_report_type()
        self.assertEqual(self.inspection_job_card.inspection_type,
                         "specific_inspection")

    def test_onchange_inspection_type(self):
        self.inspection_job_card._onchange_inspection_type()
        self.assertEqual(self.inspection_job_card.inspection_type,
                         "specific_inspection")
        
        self.inspection_job_card.interior_item_condition_ids = [(0, 0, {
            "vehicle_item_id": self.item_interior.id
        })]
        self.inspection_job_card.vehicle_condition_line_ids = [(0, 0, {
            "vehicle_condition_id": self.vehicle_condition.id
        })]
        self.inspection_job_card.tyre_inspection_ids = [(0, 0, {
            "tyre": "lf"
        })]
        self.inspection_job_card.mechanical_item_condition_ids = [(0, 0, {
            "vehicle_item_id": self.item_mechanical.id
        })]
        self.inspection_job_card.vehicle_components_ids = [(0, 0, {
            "vehicle_component_id": self.component_bottom_side.id,
            "c_vehicle_side": "bottom_side"
        })]
        self.inspection_job_card.vehicle_fluids_ids = [(0, 0, {
            "vehicle_fluid_id": self.fluids_top_side.id,
            "f_vehicle_side": "top_side"
        })]

        self.inspection_job_card.part_assessment = True
        self.inspection_job_card.inner_body_inspection = True
        self.inspection_job_card.outer_body_inspection = True
        self.inspection_job_card.mechanical_condition = True
        self.inspection_job_card.vehicle_component = True
        self.inspection_job_card.vehicle_fluid = True
        self.inspection_job_card.tyre_inspection = True

        self.inspection_job_card._onchange_inspection_type()
        self.assertEqual(self.inspection_job_card.inspection_type,
                         "full_inspection")

    def test_check_inspect_type(self):
        with self.assertRaises(ValidationError) as ve:
            self.inspection_job_card.inspect_type = None
        self.assertEqual(
            ve.exception.args[0],
            "Select inspection type: 'Only Inspection' or 'Inspection + "
            "Repair' Make a choice to proceed.")


    def test_compute_spare_part_price(self):
        self.inspection_spare_part._onchange_spare_part_price()
        self.assertEqual(self.inspection_spare_part.unit_price, 10)
        self.inspection_spare_part._compute_sub_total()
        self.assertEqual(self.inspection_spare_part.sub_total, 20)
        self.inspection_spare_part_two._onchange_spare_part_price()
        self.assertEqual(self.inspection_spare_part_two.unit_price, 20)
        self.inspection_spare_part_two._compute_sub_total()
        self.assertEqual(self.inspection_spare_part_two.sub_total, 40)
        self.inspection_job_card._compute_spare_part_price()
        self.assertEqual(self.inspection_job_card.part_price, 60)

    def test_compute_vehicle_booking(self):
        self.inspection_job_card._compute_vehicle_booking()
        self.assertEqual(self.inspection_job_card.vehicle_booking_id.id,
                         self.booking.id)

    def test_action_create_vehicle_registration(self):
        with self.assertRaises(ValidationError) as ve:
            self.inspection_job_card.registration_no = "1234567890"
            self.inspection_job_card.action_create_vehicle_registration()

        self.inspection_job_card.registration_no = "098745631"
        self.inspection_job_card.action_create_vehicle_registration()
        self.assertTrue(self.inspection_job_card.register_vehicle_id)
        self.assertEqual(self.inspection_job_card.vehicle_from,
                         "customer_vehicle")
        self.assertTrue(self.inspection_job_card.is_registered_vehicle)
        register_vehicle = self.inspection_job_card.register_vehicle_id
        self.assertEqual(register_vehicle.customer_id.id, self.customer.id)
        self.assertEqual(register_vehicle.vehicle_brand_id.id,
                         self.vehicle_brand.id)
        self.assertEqual(register_vehicle.vehicle_model_id.id,
                         self.vehicle_model.id)
        self.assertEqual(
            register_vehicle.vehicle_fuel_type_id.id, self.fuel_type.id)
        self.assertEqual(register_vehicle.registration_no, "098745631")
        self.assertEqual(register_vehicle.vin_no, "1234")
        self.assertEqual(register_vehicle.transmission_type, "automatic")

        self.inspection_job_card.vehicle_brand_id = False
        self.inspection_job_card.vehicle_model_id = False
        message = self.inspection_job_card.action_create_vehicle_registration()
        self.assertIsInstance(message, dict)
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'warning')
        self.assertFalse(message["params"]["sticky"])

    def test_create_repair_job_card(self):
        self.inspection_spare_part._onchange_spare_part_price()
        self.inspection_spare_part._compute_sub_total()
        self.inspection_spare_part_two._onchange_spare_part_price()
        self.inspection_spare_part_two._compute_sub_total()
        self.inspection_job_card._compute_spare_part_price()
        fleet_brand = self.env["fleet.vehicle.model.brand"].create({
            "name": "Fleet Brand", })
        fleet_model = self.env['fleet.vehicle.model'].create({
            "name": "Fleet Model", "brand_id": fleet_brand.id})
        fleet = self.env["fleet.vehicle"].create({
            "model_id": fleet_model.id, "license_plate": "License",
            "vehicle_brand_id": self.vehicle_brand.id, "vehicle_fuel_type_id":
            self.fuel_type.id, "vehicle_model_id": self.vehicle_model.id,
            "vin_no": "123", "transmission_type": "manual"})
        self.inspection_job_card.register_vehicle_id = self.register_vehicle.id
        self.inspection_job_card.fleet_vehicle_id = fleet.id
        self.inspection_job_card.registration_no = "1234567890"
        self.inspection_job_card.customer_observation = "Customer Observation"
        self.inspection_job_card.is_skip_quotation = False
        self.inspection_job_card.is_registered_vehicle = True
        self.inspection_job_card.inspection_date = datetime.datetime.\
            today().date()

        action = self.inspection_job_card.create_repair_job_card()
        self.assertIsInstance(action, dict)
        for val in ("type", "name", "res_model", "res_id",
                    "view_mode", "target",):
            self.assertIn(val, action)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], 'Repair Job Card')
        self.assertEqual(action["res_model"], 'repair.job.card')
        self.assertIn('form', action["view_mode"])
        self.assertEqual(action["target"], 'current')
        repair_job_card = self.env["repair.job.card"].browse(
            action["res_id"])

        self.assertEqual(repair_job_card.vehicle_brand_id, self.vehicle_brand)
        self.assertEqual(repair_job_card.vehicle_model_id, self.vehicle_model)
        self.assertEqual(repair_job_card.vehicle_fuel_type_id, self.fuel_type)
        self.assertEqual(repair_job_card.register_vehicle_id,
                         self.register_vehicle)
        self.assertEqual(repair_job_card.fleet_vehicle_id, fleet)
        self.assertEqual(repair_job_card.registration_no, "1234567890")
        self.assertEqual(repair_job_card.vin_no, "1234")
        self.assertEqual(repair_job_card.transmission_type, "automatic")
        self.assertEqual(repair_job_card.inspect_repair_date, datetime.datetime.
                         today().date())
        self.assertEqual(repair_job_card.vehicle_from, "new")
        self.assertTrue(repair_job_card.is_registered_vehicle,)
        self.assertEqual(repair_job_card.customer_id, self.customer)
        self.assertEqual(repair_job_card.street, "Street One")
        self.assertEqual(repair_job_card.street2, "Street Two")
        self.assertEqual(repair_job_card.city, "City")
        self.assertEqual(repair_job_card.state_id.id, 12)
        self.assertEqual(repair_job_card.country_id.id, 104)
        self.assertEqual(repair_job_card.zip, "305013")
        self.assertEqual(repair_job_card.phone, "1234567890")
        self.assertEqual(repair_job_card.email, "Email@gmail.com")
        self.assertFalse(repair_job_card.repair_sale_order_id)
        self.assertEqual(repair_job_card.repair_amount, 0)
        self.assertFalse(repair_job_card.repair_order_state)
        self.assertEqual(repair_job_card.sub_total, 60)
        self.assertFalse(repair_job_card.is_skip_quotation)
        self.assertEqual(repair_job_card.customer_observation,
                         "Customer Observation")

        self.inspection_job_card.vehicle_brand_id = False
        self.inspection_job_card.registration_no = False
        self.inspection_job_card.vehicle_model_id = False
        message = self.inspection_job_card.create_repair_job_card()
        self.assertIsInstance(message, dict)
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'warning')
        self.assertEqual(message["params"]["message"], "Required: Vehicle, "
                         "Registration No., and Model information.")
        self.assertFalse(message["params"]["sticky"])

    def test_create_inspection_repair_quotation(self):

        # In case booking for only inspection and not add any amount ---
        self.inspection_job_card.inspect_type = "only_inspection"
        self.inspection_job_card.inspection_charge_type = "paid"
        message = self.inspection_job_card.create_inspection_repair_quotation()
        self.assertIsInstance(message, dict)
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'warning')
        self.assertEqual(message["params"]["message"], "Kindly include the "
                         "inspection charge amount.")
        self.assertFalse(message["params"]["sticky"])

        # In case booking for inspection and repair both but not add any mount -
        self.inspection_job_card.inspect_type = "inspection_and_repair"
        message = self.inspection_job_card.create_inspection_repair_quotation()
        self.assertIsInstance(message, dict)
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'warning')
        self.assertEqual(message["params"]["message"], "Kindly include the "
                         "inspection charge amount.")
        self.assertFalse(message["params"]["sticky"])

        # In case booking for inspection and repair and price given but required
        # spare parts are not given
        self.inspection_job_card.vehicle_spare_part_ids = False
        self.inspection_job_card.inspection_charge = 100
        message = self.inspection_job_card.create_inspection_repair_quotation()
        self.assertIsInstance(message, dict)
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'warning')
        self.assertFalse(message["params"]["sticky"])

        # In case booking for inspection and repair and price given but
        # inspection repair services are not given
        self.inspection_job_card.vehicle_spare_part_ids = [(0, 0, {
            "product_id": self.product.id, "qty": 2, }), (0, 0, {
                "product_id": self.product.id, "qty": 2, })]
        self.inspection_job_card.inspection_repair_team_ids = False
        self.inspection_job_card.inspection_charge = 100
        message = self.inspection_job_card.create_inspection_repair_quotation()
        self.assertIsInstance(message, dict)
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'warning')
        self.assertFalse(message["params"]["sticky"])

        # In case booking for inspection and repair all the value are given
        self.inspection_job_card.inspection_repair_team_ids = [(0, 0, {
            "vehicle_service_id": self.vehicle_service_one.id, }), (0, 0, {
                "vehicle_service_id": self.vehicle_service_one.id, })]
        action = self.inspection_job_card.create_inspection_repair_quotation()
        self.assertIsInstance(action, dict)
        for val in ("type", "name", "res_model", "res_id",
                    "view_mode", "target",):
            self.assertIn(val, action)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], 'Sale Order')
        self.assertEqual(action["res_model"], 'sale.order')
        self.assertIn('form', action["view_mode"])
        self.assertEqual(action["target"], 'current')
        sale_order = self.env["sale.order"].browse(
            action["res_id"])
        self.assertEqual(sale_order.amount_untaxed, 100)

    def test_update_inspection_repair_quotation(self):

        # In case inspection charge type is given but inspection charge
        # is not given
        self.inspection_job_card.inspect_type = "inspection_and_repair"
        self.inspection_job_card.inspection_charge_type = "paid"
        message = self.inspection_job_card.update_inspection_repair_quotation()
        self.assertIsInstance(message, dict)
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'warning')
        self.assertEqual(message["params"]["message"],
                         "Kindly include the inspection charge amount.")
        self.assertFalse(message["params"]["sticky"])

        # In case inspection chage type and inspection charge both are given
        # but vehicle spare parts are not given
        self.inspection_job_card.vehicle_spare_part_ids = False
        self.inspection_job_card.inspection_charge = 100
        message = self.inspection_job_card.update_inspection_repair_quotation()
        self.assertIsInstance(message, dict)
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'warning')
        self.assertFalse(message["params"]["sticky"])
        # In case booking for inspection and repair and price given but
        # inspection repair services are not given

        self.inspection_job_card.vehicle_spare_part_ids = [(0, 0, {
            "product_id": self.product.id, "qty": 2, }), (0, 0, {
                "product_id": self.product.id, "qty": 2, })]
        self.inspection_job_card.inspection_repair_team_ids = False
        self.inspection_job_card.inspection_charge = 100
        message = self.inspection_job_card.update_inspection_repair_quotation()
        self.assertIsInstance(message, dict)
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'warning')
        self.assertFalse(message["params"]["sticky"])

        # In case booking for inspection and repair all the value are given
        self.inspection_job_card.inspection_repair_team_ids = [(0, 0, {
            "vehicle_service_id": self.vehicle_service_one.id, }), (0, 0, {
                "vehicle_service_id": self.vehicle_service_one.id, })]
        message = self.inspection_job_card.update_inspection_repair_quotation()
        for val in ("type", "tag", "params"):
            self.assertIn(val, message)
        self.assertEqual(message["type"], 'ir.actions.client')
        self.assertEqual(message["tag"], 'display_notification')
        self.assertEqual(message["params"]["type"], 'success')
        self.assertEqual(message["params"]["message"],
                         "Quotation is successfully updated")
        self.assertFalse(message["params"]["sticky"])

    def test_compute_inspection_delivery_orders(self):
        self.inspection_job_card._compute_inspection_delivery_orders()
        self.assertEqual(
            self.inspection_job_card.inspection_delivery_orders, 0)

    def test_action_view_inspection_delivery(self):
        action = self.inspection_job_card.action_view_inspection_delivery()
        self.assertIsInstance(action, dict)
        for val in ("type", "name", "res_model", "domain",
                    "view_mode", "target", "context"):
            self.assertIn(val, action)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], 'Delivery')
        self.assertEqual(action["res_model"], 'stock.picking')
        self.assertIn(('id', 'in', self.inspection_job_card.
                       sale_order_id.picking_ids.ids), action.get("domain", []))
        self.assertEqual(action["view_mode"], 'list,form,kanban')
        self.assertEqual(action["target"], "current")
        self.assertFalse(action["context"]["create"])

    def test_create_inspection_job_card_invoice(self):
        self.inspection_job_card.inspection_charge = 100
        self.inspection_job_card.inspection_charge_type = "paid"
        self.inspection_job_card.create_inspection_repair_quotation()
        self.inspection_job_card.sale_order_id.action_confirm()
        invoice = self.inspection_job_card.create_inspection_job_card_invoice()
        self.assertEqual(invoice.amount_residual, 100)

    def test_compute_inspection_invoices(self):
        self.inspection_job_card.inspection_charge = 100
        self.inspection_job_card.inspection_charge_type = "paid"
        self.inspection_job_card.create_inspection_repair_quotation()
        self.inspection_job_card.sale_order_id.action_confirm()
        invoice = self.inspection_job_card.create_inspection_job_card_invoice()
        self.assertEqual(invoice.amount_residual, 100)
        self.inspection_job_card._compute_inspection_invoices()
        self.assertEqual(self.inspection_job_card.inspection_invoices, 1)

    def test_view_inspection_invoice(self):
        action = self.inspection_job_card.view_inspection_invoice()
        self.assertIsInstance(action, dict)
        for val in ('type', 'name', 'res_model', 'domain',
                    'view_mode', 'target', 'context', ):
            self.assertIn(val, action)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], 'Invoices')
        self.assertEqual(action["res_model"], 'account.move')
        self.assertIn(('inspection_job_card_id', '=', self.inspection_job_card
                       .id), action.get("domain", []))
        self.assertEqual(action["view_mode"], 'list,form')
        self.assertEqual(action["target"], "current")
        self.assertFalse(action["context"]["create"])

    def test_unlink_method(self):

        with self.assertRaises(ValidationError) as ve:
            self.inspection_job_card.stages = 'locked'
            self.inspection_job_card.unlink()
        self.assertEqual(
            ve.exception.args[0],
            "You cannot delete the locked order.")

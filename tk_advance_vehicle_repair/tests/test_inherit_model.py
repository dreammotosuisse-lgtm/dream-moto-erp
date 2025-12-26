import datetime
import psycopg2
from dateutil.relativedelta import relativedelta
from odoo.tests.common import tagged
from .common import VehicleRepairData


@tagged('vehicle_repair_inherit')
class TestVehicleRepairInherit(VehicleRepairData):

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
        
    def test_inherited_fleet_vehicle(self):
        fleet_brand = self.env["fleet.vehicle.model.brand"].create({
            "name": "Fleet Brand", })
        fleet_model = self.env['fleet.vehicle.model'].create({
            "name": "Fleet Model", "brand_id": fleet_brand.id})
        fleet = self.env["fleet.vehicle"].create({
            "model_id": fleet_model.id, "license_plate": "License",
            "vehicle_brand_id": self.vehicle_brand.id, "vehicle_fuel_type_id":
            self.fuel_type.id, "vehicle_model_id": self.vehicle_model.id,
            "vin_no": "123", "transmission_type": "manual"})
        
        # _onchange_vehicle_brand_id -------------------------------------------
        self.assertTrue(fleet.vehicle_model_id)
        fleet._onchange_vehicle_brand_id()
        self.assertFalse(fleet.vehicle_model_id)

    def test_inherited_project_task(self):
        task = self.env["project.task"].create({
            "repair_job_card_id": self.repair_job_card.id, "r_vehicle_brand_id":
            self.vehicle_brand.id, "r_vehicle_model_id": self.vehicle_model.id,
            "r_vehicle_fuel_type_id": self.fuel_type.id, "r_registration_no": 
            "64215198413", "r_vin_no": "332342", "r_transmission_type": "manual",
            "work_is_done": False, })
        task.repair_service_work_done()
        self.assertTrue(task.work_is_done)

    def test_inherited_res_user(self):

        # _compute_vehicle_count -----------------------------------------------
        self.customer._compute_vehicle_count()
        self.assertEqual(self.customer.vehicle_count, self.env[
            'register.vehicle'].search_count([(
                'customer_id', '=', self.customer.id)]))

        action = self.customer.action_view_vehicle_details()
        self.assertIsInstance(action, dict)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["name"], "Vehicles")
        self.assertEqual(action["res_model"], "register.vehicle")
        self.assertIn(('customer_id', '=', self.customer.id), 
                      action.get("domain", []))
        self.assertEqual(action["context"]["default_customer_id"], 
                         self.customer.id)
        self.assertEqual(action["view_mode"], 'list,form')
        self.assertEqual(action["target"], "current")
    
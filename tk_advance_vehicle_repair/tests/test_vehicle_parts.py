import datetime
import psycopg2
from dateutil.relativedelta import relativedelta
from odoo.tests.common import tagged
from .common import VehicleRepairData


@tagged('vehicle_parts')
class TestServiceTeam(VehicleRepairData):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vehicle_spare_part = cls._create_vehicle_spare_part({
            "product_id": cls.product.id, "qty": 3, "unit_price": 100, })
        cls.repair_job_card = cls._create_repair_job_card({
            "customer_id": cls.customer.id, "vehicle_brand_id":
            cls.vehicle_brand.id, "vehicle_model_id": cls.vehicle_model.id,
            "vehicle_fuel_type_id": cls.fuel_type.id,
            "registration_no": "613211621354", "email": "Email@gmail.com",
            "street": "Street One", "street2": "Street Two",
            "city": "City", "country_id": 104, "state_id": 12,
            "zip": "305013", "phone": "1234567890", })
        cls.team_one = cls._create_vehicle_service_team({
            "vehicle_service_id": cls.vehicle_service_one.id,
            "vehicle_service_team_members_ids": [
                (6, 0, [cls.user.id])], "start_date": datetime.datetime.today().
            date(), "end_date": datetime.datetime.today().
            date() + relativedelta(days=1), "service_charge": 10,
            "repair_job_card_id": cls.repair_job_card.id})
        cls.team_two = cls._create_vehicle_service_team({
            "vehicle_service_id": cls.vehicle_service_two.id,
            "vehicle_service_team_members_ids": [
                (6, 0, [cls.user.id])], "start_date": datetime.datetime.today().
            date(), "end_date": datetime.datetime.today().
            date() + relativedelta(days=1), "service_charge": 10,
            "repair_job_card_id": cls.repair_job_card.id})
        cls.vehicle_order_spare_part = cls._create_vehicle_order_spare_part({
            "product_id": cls.product.id, "qty": 5, "unit_price": 100,
            "repair_job_card_id": cls.repair_job_card.id})

    def test_create_vehicle_spare_part(self):
        with self.assertLogs("odoo.sql_db", level="ERROR"):
            with self.assertRaises(psycopg2.errors.NotNullViolation):
                self.env["vehicle.spare.part"].create({})

    def test_onchange_spare_part_price(self):
        self.vehicle_spare_part._onchange_spare_part_price()
        self.assertEqual(self.vehicle_spare_part.unit_price, 10)

    def test_compute_sub_total(self):
        self.vehicle_spare_part._onchange_spare_part_price()
        self.vehicle_spare_part._compute_sub_total()
        self.assertEqual(self.vehicle_spare_part.sub_total, 30)

    def test_spare_parts_create(self):
        with self.assertLogs("odoo.sql_db", level="ERROR"):
            with self.assertRaises(psycopg2.errors.NotNullViolation):
                self.env["vehicle.order.spare.part"].create({})

    def test_compute_valid_vehicle_services(self):
        self.vehicle_order_spare_part._compute_valid_vehicle_services()
        self.assertIn(self.team_one.vehicle_service_id.id, self.
                      vehicle_order_spare_part.valid_vehicle_service_ids.ids)
        self.assertIn(self.team_two.vehicle_service_id.id, self.
                      vehicle_order_spare_part.valid_vehicle_service_ids.ids)

    def test_onchange_spare_part_price(self):
        self.vehicle_order_spare_part._onchange_spare_part_price()
        self.assertEqual(self.vehicle_order_spare_part.unit_price, 10)

    def test_compute_sub_total(self):
        self.vehicle_order_spare_part._onchange_spare_part_price()
        self.vehicle_order_spare_part._compute_sub_total()
        self.assertEqual(self.vehicle_order_spare_part.sub_total, 50)

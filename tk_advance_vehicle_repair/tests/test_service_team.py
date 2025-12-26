import datetime
import psycopg2
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from .common import VehicleRepairData


@tagged('service_team')
class TestServiceTeam(VehicleRepairData):

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

    def test_vehicle_service_team(self):
        with self.assertLogs("odoo.sql_db", level="ERROR"):
            with self.assertRaises(psycopg2.errors.NotNullViolation):
                self.env["vehicle.service.team"].create({})
        vehicle_service_team = self._create_vehicle_service_team({
            "vehicle_service_id": self.vehicle_service_one.id, 
              "start_date": datetime.datetime.today().
                date(), "end_date": datetime.datetime.today().date()
                + relativedelta(days=2), "repair_job_card_id":
                self.repair_job_card.id},)
        with self.assertRaisesRegex(
                ValidationError, "Kindly verify that the vehicle "
                "services end date occurs after the start date"):
            self._create_vehicle_service_team({
                "vehicle_service_id": self.vehicle_service_one.id,
                  "start_date": datetime.datetime.
                today().date(), "end_date": datetime.datetime.today().
                date() - relativedelta(days=1), })

        vehicle_service_team._onchange_service_charge()
        self.assertEqual(vehicle_service_team.service_charge, 10)
        vehicle_service_team._onchange_service_team_id()
        self.assertFalse(vehicle_service_team.vehicle_service_team_members_ids)
        vehicle_service_team.create_service_task()
        self.assertTrue(vehicle_service_team.team_task_id)
        task = vehicle_service_team.team_task_id
        self.assertEqual(task.vehicle_service_id.id,
                         self.vehicle_service_one.id)
        self.assertEqual(task.partner_id.id, self.customer.id)
        self.assertEqual(task.user_ids.ids, vehicle_service_team.
                         vehicle_service_team_members_ids.ids)
        self.assertEqual(task.date_assign.date(),
                         datetime.datetime.today().date())
        self.assertEqual(task.date_deadline.date(), datetime.datetime.today().date()
                         + relativedelta(days=2))
        self.assertEqual(task.repair_job_card_id.id, self.repair_job_card.id)

        vehicle_service_team.work_is_done = False
        vehicle_service_team._onchange_team_work_status()
        self.assertFalse(vehicle_service_team.service_team_id)

        with self.assertRaisesRegex(ValidationError, "You cannot delete "
                                    "records with created team tasks."):
            vehicle_service_team._unlink_service_record()

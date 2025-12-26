import datetime
import psycopg2
from dateutil.relativedelta import relativedelta
from odoo.tests.common import tagged
from .common import VehicleRepairData


@tagged("vehicle_booking")
class TestVehicleBooking(VehicleRepairData):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.booking = cls._create_booking({
            "customer_id": cls.customer.id, "vehicle_brand_id":
            cls.vehicle_brand.id, "registration_no": "12345",
            "vehicle_model_id": cls.vehicle_model.id, "vehicle_fuel_type_id":
            cls.fuel_type.id, "street":"Street One", "street2":"Street Two",
            "city":"City", "country_id":104, "state_id":12,
            "zip":"305013", "phone":"1234567890", "email":"Email@gmail.com",})
        cls.empty_booking = cls._create_booking({
            "customer_id": cls.customer.id
        })

    def test_creating_booking(self):
        booking = self._create_booking({
            "customer_id": self.customer.id, "vehicle_brand_id":
            self.vehicle_brand.id, "registration_no": "12345",
            "vehicle_model_id": self.vehicle_model.id, "vehicle_fuel_type_id":
            self.fuel_type.id
        })
        self.assertTrue(booking)
        self.assertNotEqual(booking.booking_number, 'New')

    def test_write_method(self):
        self.booking.write({})
        self.assertEqual(self.customer.street, "Street One")
        self.assertEqual(self.customer.street2, "Street Two")
        self.assertEqual(self.customer.city, "City")
        self.assertEqual(self.customer.country_id.id, 104)
        self.assertEqual(self.customer.state_id.id, 12)
        self.assertEqual(self.customer.zip, "305013")
        self.assertEqual(self.customer.phone, "1234567890")
        self.assertEqual(self.customer.email, "Email@gmail.com")

    def test_expand_groups(self):
        data = self.booking._expand_groups(None, None)
        self.assertIsInstance(data, list)
        for val in ('draft', 'vehicle_inspection', 'vehicle_repair',
                    'vehicle_inspection_repair', 'cancel'):
            self.assertIn(val, data)

    def test_action_buttons(self):

        self.booking.street = "Street One"
        self.booking.street2 = "Street Two"
        self.booking.city = "City"
        self.booking.country_id = 104
        self.booking.state_id = 12
        self.booking.zip = "305013"
        self.booking.phone = "1234567890"
        self.booking.email = "Email@gamil.com"

        # draft_to_vehicle_inspection ------------------------------------------

        message = self.booking.draft_to_vehicle_inspection()
        self.assertIsInstance(message, dict)
        self.assertEqual(message["type"], "ir.actions.act_window")
        self.assertEqual(message["name"], "Inspection Job Card")
        self.assertEqual(message["res_model"], "inspection.job.card")
        self.assertTrue(message["res_id"])
        self.assertEqual(message["view_mode"], "form")
        self.assertEqual(message["target"], "current")

        inspection_card = self.env["inspection.job.card"].browse(
            message["res_id"])

        self.assertEqual(inspection_card.vehicle_brand_id.id,
                         self.booking.vehicle_brand_id.id)
        self.assertEqual(inspection_card.vehicle_model_id.id,
                         self.booking.vehicle_model_id.id)
        self.assertEqual(inspection_card.inspection_date,
                         self.booking.booking_date)
        self.assertEqual(inspection_card.vehicle_fuel_type_id.id,
                         self.booking.vehicle_fuel_type_id.id)
        self.assertEqual(inspection_card.registration_no,
                         self.booking.registration_no)
        self.assertEqual(inspection_card.fleet_vehicle_id.id,
                         self.booking.fleet_vehicle_id.id)
        self.assertEqual(inspection_card.register_vehicle_id.id,
                         self.booking.register_vehicle_id.id)
        self.assertEqual(inspection_card.vehicle_from,
                         self.booking.vehicle_from)
        self.assertEqual(inspection_card.is_registered_vehicle,
                         self.booking.is_registered_vehicle)
        self.assertEqual(inspection_card.vin_no, self.booking.vin_no)
        self.assertEqual(inspection_card.transmission_type,
                         self.booking.transmission_type)
        self.assertEqual(inspection_card.customer_id.id,
                         self.booking.customer_id.id)
        self.assertEqual(inspection_card.street, self.booking.street)
        self.assertEqual(inspection_card.street2, self.booking.street2)
        self.assertEqual(inspection_card.city, self.booking.city)
        self.assertEqual(inspection_card.state_id.id, self.booking.state_id.id)
        self.assertEqual(inspection_card.country_id.id,
                         self.booking.country_id.id)
        self.assertEqual(inspection_card.zip, self.booking.zip)
        self.assertEqual(inspection_card.phone, self.booking.phone)
        self.assertEqual(inspection_card.email, self.booking.email)
        self.assertEqual(inspection_card.inspect_type,
                         self.booking.booking_type)
        self.assertEqual(inspection_card.customer_observation,
                         self.booking.customer_observation)
        self.assertEqual(self.booking.booking_stages, "vehicle_inspection")

        # vehicle_inspection_to_vehicle_repair ---------------------------------

        message = self.booking.vehicle_inspection_to_vehicle_repair()
        self.assertIsInstance(message, dict)
        self.assertEqual(message["type"], "ir.actions.act_window")
        self.assertEqual(message["name"], "Repair Job Card")
        self.assertEqual(message["res_model"], "repair.job.card")
        self.assertTrue(message["res_id"])
        self.assertEqual(message["view_mode"], "form")
        self.assertEqual(message["target"], "current")

        repair_card = self.env["repair.job.card"].browse(
            message["res_id"])

        self.assertEqual(repair_card.vehicle_brand_id,
                         self.booking.vehicle_brand_id)
        self.assertEqual(repair_card.vehicle_model_id,
                         self.booking.vehicle_model_id)
        self.assertEqual(repair_card.inspect_repair_date,
                         self.booking.booking_date)
        self.assertEqual(repair_card.vehicle_fuel_type_id,
                         self.booking.vehicle_fuel_type_id)
        self.assertEqual(repair_card.registration_no,
                         self.booking.registration_no)
        self.assertEqual(repair_card.fleet_vehicle_id,
                         self.booking.fleet_vehicle_id)
        self.assertEqual(repair_card.register_vehicle_id,
                         self.booking.register_vehicle_id)
        self.assertEqual(repair_card.vehicle_from,
                         self.booking.vehicle_from)
        self.assertEqual(repair_card.is_registered_vehicle,
                         self.booking.is_registered_vehicle)
        self.assertEqual(repair_card.vin_no,
                         self.booking.vin_no)
        self.assertEqual(repair_card.transmission_type,
                         self.booking.transmission_type)
        self.assertEqual(repair_card.customer_id,
                         self.booking.customer_id)
        self.assertEqual(repair_card.street,
                         self.booking.street)
        self.assertEqual(repair_card.street2,
                         self.booking.street2)
        self.assertEqual(repair_card.city,
                         self.booking.city)
        self.assertEqual(repair_card.state_id,
                         self.booking.state_id)
        self.assertEqual(repair_card.country_id,
                         self.booking.country_id)
        self.assertEqual(repair_card.zip,
                         self.booking.zip)
        self.assertEqual(repair_card.phone,
                         self.booking.phone)
        self.assertEqual(repair_card.email,
                         self.booking.email)
        self.assertEqual(repair_card.customer_observation,
                         self.booking.customer_observation)
        self.assertEqual(self.booking.booking_stages, "vehicle_repair")

        # vehicle_repair_to_vehicle_inspection_repair --------------------------

        message = self.booking.vehicle_repair_to_vehicle_inspection_repair()
        self.assertIsInstance(message, dict)
        self.assertEqual(message["type"], "ir.actions.act_window")
        self.assertEqual(message["name"], "Inspection Job Card")
        self.assertEqual(message["res_model"], "inspection.job.card")
        self.assertTrue(message["res_id"])
        self.assertEqual(message["view_mode"], "form")
        self.assertEqual(message["target"], "current")


        inspection_card = self.env["inspection.job.card"].browse(
            message["res_id"])

        self.assertEqual(inspection_card.vehicle_brand_id.id,
                         self.booking.vehicle_brand_id.id)
        self.assertEqual(inspection_card.vehicle_model_id.id,
                         self.booking.vehicle_model_id.id)
        self.assertEqual(inspection_card.inspection_date,
                         self.booking.booking_date)
        self.assertEqual(inspection_card.vehicle_fuel_type_id.id,
                         self.booking.vehicle_fuel_type_id.id)
        self.assertEqual(inspection_card.registration_no,
                         self.booking.registration_no)
        self.assertEqual(inspection_card.fleet_vehicle_id.id,
                         self.booking.fleet_vehicle_id.id)
        self.assertEqual(inspection_card.register_vehicle_id.id,
                         self.booking.register_vehicle_id.id)
        self.assertEqual(inspection_card.vehicle_from,
                         self.booking.vehicle_from)
        self.assertEqual(inspection_card.is_registered_vehicle,
                         self.booking.is_registered_vehicle)
        self.assertEqual(inspection_card.vin_no, self.booking.vin_no)
        self.assertEqual(inspection_card.transmission_type,
                         self.booking.transmission_type)
        self.assertEqual(inspection_card.customer_id.id,
                         self.booking.customer_id.id)
        self.assertEqual(inspection_card.street, self.booking.street)
        self.assertEqual(inspection_card.street2, self.booking.street2)
        self.assertEqual(inspection_card.city, self.booking.city)
        self.assertEqual(inspection_card.state_id.id, self.booking.state_id.id)
        self.assertEqual(inspection_card.country_id.id,
                         self.booking.country_id.id)
        self.assertEqual(inspection_card.zip, self.booking.zip)
        self.assertEqual(inspection_card.phone, self.booking.phone)
        self.assertEqual(inspection_card.email, self.booking.email)
        self.assertEqual(inspection_card.inspect_type,
                         self.booking.booking_type)
        self.assertEqual(inspection_card.customer_observation,
                         self.booking.customer_observation)
        self.assertEqual(self.booking.booking_stages, "vehicle_inspection_repair")

    def test_vehicle_inspection_repair_to_cancel(self):
        self.booking.vehicle_inspection_repair_to_cancel()
        self.assertEqual(self.booking.booking_stages, "cancel")

    def test_onchange_method(self):
        self.booking.booking_date = "2025-04-11"
        self.booking._onchange_booking_days()
        self.assertEqual(self.booking.booking_appointment_id.id, 5)

    def test_onchange_fleet_vehicle(self):
        fleet_brand = self.env["fleet.vehicle.model.brand"].create({
            "name": "Fleet Brand", })
        fleet_model = self.env['fleet.vehicle.model'].create({
            "name": "Fleet Model", "brand_id": fleet_brand.id})
        fleet = self.env["fleet.vehicle"].create({
            "model_id":fleet_model.id, "license_plate": "License",
            "vehicle_brand_id": self.vehicle_brand.id, "vehicle_fuel_type_id":
            self.fuel_type.id, "vehicle_model_id": self.vehicle_model.id,
            "vin_no": "123", "transmission_type": "manual"})
        self.empty_booking.fleet_vehicle_id = fleet.id
        self.empty_booking.vehicle_from = "fleet_vehicle"
        self.empty_booking._onchange_fleet_vehicle()
        self.assertEqual(self.empty_booking.vehicle_brand_id.id, 
                         fleet.vehicle_brand_id.id)
        self.assertEqual(self.empty_booking.vehicle_model_id.id, 
                         fleet.vehicle_model_id.id)
        self.assertEqual(self.empty_booking.vehicle_fuel_type_id.id, 
                         fleet.vehicle_fuel_type_id.id)
        self.assertEqual(self.empty_booking.transmission_type, 
                         fleet.transmission_type)
        self.assertEqual(self.empty_booking.registration_no, 
                         fleet.license_plate)
        self.assertEqual(self.empty_booking.vin_no, 
                         fleet.vin_no)
        
        self.booking._onchange_fleet_vehicle()
        self.assertFalse(self.booking.vehicle_brand_id)
        self.assertFalse(self.booking.vehicle_model_id)
        self.assertFalse(self.booking.vehicle_fuel_type_id)
        self.assertFalse(self.booking.transmission_type)
        self.assertFalse(self.booking.registration_no)
        self.assertFalse(self.booking.vin_no)

    def test_onchange_vehicle_brand_id(self):
        self.empty_booking._onchange_vehicle_brand_id()
        self.assertFalse(self.empty_booking.vehicle_fuel_type_id)
        self.assertFalse(self.empty_booking.vehicle_model_id)

    def test_onchange_vehicle_model_id(self):
        self.empty_booking._onchange_vehicle_model_id()
        self.assertFalse(self.empty_booking.vehicle_fuel_type_id)

    def test_onchange_customer_details(self):
        self.booking._onchange_customer_details()
        self.assertEqual(self.booking.email, "Email@gmail.com")
        self.assertEqual(self.booking.street, "Street One")
        self.assertEqual(self.booking.street2, "Street Two")
        self.assertEqual(self.booking.city, "City")
        self.assertEqual(self.booking.state_id.id, 12)
        self.assertEqual(self.booking.country_id.id, 104)
        self.assertEqual(self.booking.zip, "305013")
        self.assertFalse(self.booking.register_vehicle_id)
        self.assertFalse(self.booking.fleet_vehicle_id)

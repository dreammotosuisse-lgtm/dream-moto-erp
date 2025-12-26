import datetime
import psycopg2
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from .common import VehicleRepairData


@tagged('configuration')
class TestConfiguration(VehicleRepairData):

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
            cls.fuel_type.id, "street": "Street One", "street2": "Street Two",
            "city": "City", "country_id": 104, "state_id": 12,
            "zip": "305013", "phone": "1234567890", "email": "Email@gmail.com", })

    def test_fuel_type(self):
        # Check required field
        with self.assertRaises(psycopg2.errors.NotNullViolation):
            with self.assertLogs("odoo.sql_db", level="ERROR"):
                self.env["vehicle.fuel.type"].create({})

    def test_vehicle_part_info(self):
        # Check required field
        with self.assertRaises(psycopg2.errors.NotNullViolation):
            with self.assertLogs("odoo.sql_db", level="ERROR"):
                self.env["vehicle.part.info"].create({})

        # Create without type
        with self.assertRaisesRegex(ValidationError, "Please select a any "
                                    "one type of part"):
            self.env["vehicle.part.info"].create({"name": "Name"}). \
                _constrain_check_part_type()

    def test_exterior_vehicle_part(self):
        exterior_vehicle_part = self.env["exterior.vehicle.part"].create({
            "vehicle_part_info_id": self.part_exterior.id,
            "inspection_job_card_id": self.inspection_job_card.id})

        exterior_vehicle_part.okay_for_now = True
        exterior_vehicle_part._onchange_okay_for_now()
        self.assertFalse(exterior_vehicle_part.further_attention)
        self.assertFalse(exterior_vehicle_part.required_attention)
        self.assertFalse(exterior_vehicle_part.not_inspected)

        exterior_vehicle_part.further_attention = True
        exterior_vehicle_part._onchange_further_attention()
        self.assertFalse(exterior_vehicle_part.okay_for_now)
        self.assertFalse(exterior_vehicle_part.required_attention)
        self.assertFalse(exterior_vehicle_part.not_inspected)

        exterior_vehicle_part.required_attention = True
        exterior_vehicle_part._onchange_required_attention()
        self.assertFalse(exterior_vehicle_part.further_attention)
        self.assertFalse(exterior_vehicle_part.okay_for_now)
        self.assertFalse(exterior_vehicle_part.not_inspected)

        exterior_vehicle_part.not_inspected = True
        exterior_vehicle_part._onchange_not_inspected()
        self.assertFalse(exterior_vehicle_part.required_attention)
        self.assertFalse(exterior_vehicle_part.further_attention)
        self.assertFalse(exterior_vehicle_part.okay_for_now)

        self.assertFalse(exterior_vehicle_part.action_inspection_button())

    def test_interior_vehicle_part(self):
        interior_vehicle_part = self.env["interior.vehicle.part"].create({
            "vehicle_part_info_id": self.part_interior.id,
            "inspection_job_card_id": self.inspection_job_card.id})

        interior_vehicle_part.okay_for_now = True
        interior_vehicle_part._onchange_okay_for_now()
        self.assertFalse(interior_vehicle_part.further_attention)
        self.assertFalse(interior_vehicle_part.required_attention)
        self.assertFalse(interior_vehicle_part.not_inspected)

        interior_vehicle_part.further_attention = True
        interior_vehicle_part._onchange_further_attention()
        self.assertFalse(interior_vehicle_part.okay_for_now)
        self.assertFalse(interior_vehicle_part.required_attention)
        self.assertFalse(interior_vehicle_part.not_inspected)

        interior_vehicle_part.required_attention = True
        interior_vehicle_part._onchange_required_attention()
        self.assertFalse(interior_vehicle_part.further_attention)
        self.assertFalse(interior_vehicle_part.okay_for_now)
        self.assertFalse(interior_vehicle_part.not_inspected)

        interior_vehicle_part.not_inspected = True
        interior_vehicle_part._onchange_not_inspected()
        self.assertFalse(interior_vehicle_part.required_attention)
        self.assertFalse(interior_vehicle_part.further_attention)
        self.assertFalse(interior_vehicle_part.okay_for_now)

        self.assertFalse(interior_vehicle_part.action_inspection_button())

    def test_under_hood_vehicle_part(self):
        under_hood_vehicle_part = self.env["under.hood.vehicle.part"].create({
            "vehicle_part_info_id": self.part_under_hood.id,
            "inspection_job_card_id": self.inspection_job_card.id})

        under_hood_vehicle_part.okay_for_now = True
        under_hood_vehicle_part._onchange_okay_for_now()
        self.assertFalse(under_hood_vehicle_part.further_attention)
        self.assertFalse(under_hood_vehicle_part.required_attention)
        self.assertFalse(under_hood_vehicle_part.not_inspected)

        under_hood_vehicle_part.further_attention = True
        under_hood_vehicle_part._onchange_further_attention()
        self.assertFalse(under_hood_vehicle_part.okay_for_now)
        self.assertFalse(under_hood_vehicle_part.required_attention)
        self.assertFalse(under_hood_vehicle_part.not_inspected)

        under_hood_vehicle_part.required_attention = True
        under_hood_vehicle_part._onchange_required_attention()
        self.assertFalse(under_hood_vehicle_part.further_attention)
        self.assertFalse(under_hood_vehicle_part.okay_for_now)
        self.assertFalse(under_hood_vehicle_part.not_inspected)

        under_hood_vehicle_part.not_inspected = True
        under_hood_vehicle_part._onchange_not_inspected()
        self.assertFalse(under_hood_vehicle_part.required_attention)
        self.assertFalse(under_hood_vehicle_part.further_attention)
        self.assertFalse(under_hood_vehicle_part.okay_for_now)

        self.assertFalse(under_hood_vehicle_part.action_inspection_button())

    def test_under_vehicle_part(self):
        under_vehicle_part = self.env["under.vehicle.part"].create({
            "vehicle_part_info_id": self.part_under_vehicle.id,
            "inspection_job_card_id": self.inspection_job_card.id})

        under_vehicle_part.okay_for_now = True
        under_vehicle_part._onchange_okay_for_now()
        self.assertFalse(under_vehicle_part.further_attention)
        self.assertFalse(under_vehicle_part.required_attention)
        self.assertFalse(under_vehicle_part.not_inspected)

        under_vehicle_part.further_attention = True
        under_vehicle_part._onchange_further_attention()
        self.assertFalse(under_vehicle_part.okay_for_now)
        self.assertFalse(under_vehicle_part.required_attention)
        self.assertFalse(under_vehicle_part.not_inspected)

        under_vehicle_part.required_attention = True
        under_vehicle_part._onchange_required_attention()
        self.assertFalse(under_vehicle_part.further_attention)
        self.assertFalse(under_vehicle_part.okay_for_now)
        self.assertFalse(under_vehicle_part.not_inspected)

        under_vehicle_part.not_inspected = True
        under_vehicle_part._onchange_not_inspected()
        self.assertFalse(under_vehicle_part.required_attention)
        self.assertFalse(under_vehicle_part.further_attention)
        self.assertFalse(under_vehicle_part.okay_for_now)

        self.assertFalse(under_vehicle_part.action_inspection_button())

    def test_fluids_vehicle_part(self):
        fluids_vehicle_part = self.env["fluids.vehicle.part"].create({
            "vehicle_part_info_id": self.part_fluids.id,
            "inspection_job_card_id": self.inspection_job_card.id})

        fluids_vehicle_part.okay_for_now = True
        fluids_vehicle_part._onchange_okay_for_now()
        self.assertFalse(fluids_vehicle_part.further_attention)
        self.assertFalse(fluids_vehicle_part.required_attention)
        self.assertFalse(fluids_vehicle_part.not_inspected)

        fluids_vehicle_part.further_attention = True
        fluids_vehicle_part._onchange_further_attention()
        self.assertFalse(fluids_vehicle_part.okay_for_now)
        self.assertFalse(fluids_vehicle_part.required_attention)
        self.assertFalse(fluids_vehicle_part.not_inspected)

        fluids_vehicle_part.required_attention = True
        fluids_vehicle_part._onchange_required_attention()
        self.assertFalse(fluids_vehicle_part.further_attention)
        self.assertFalse(fluids_vehicle_part.okay_for_now)
        self.assertFalse(fluids_vehicle_part.not_inspected)

        fluids_vehicle_part.not_inspected = True
        fluids_vehicle_part._onchange_not_inspected()
        self.assertFalse(fluids_vehicle_part.required_attention)
        self.assertFalse(fluids_vehicle_part.further_attention)
        self.assertFalse(fluids_vehicle_part.okay_for_now)

        self.assertFalse(fluids_vehicle_part.action_inspection_button())

    def test_vehicle_part_tires(self):
        vehicle_part_tires = self.env["vehicle.part.tires"].create({
            "vehicle_part_info_id": self.part_tires.id,
            "inspection_job_card_id": self.inspection_job_card.id})

        vehicle_part_tires.okay_for_now = True
        vehicle_part_tires._onchange_okay_for_now()
        self.assertFalse(vehicle_part_tires.further_attention)
        self.assertFalse(vehicle_part_tires.required_attention)
        self.assertFalse(vehicle_part_tires.not_inspected)

        vehicle_part_tires.further_attention = True
        vehicle_part_tires._onchange_further_attention()
        self.assertFalse(vehicle_part_tires.okay_for_now)
        self.assertFalse(vehicle_part_tires.required_attention)
        self.assertFalse(vehicle_part_tires.not_inspected)

        vehicle_part_tires.required_attention = True
        vehicle_part_tires._onchange_required_attention()
        self.assertFalse(vehicle_part_tires.further_attention)
        self.assertFalse(vehicle_part_tires.okay_for_now)
        self.assertFalse(vehicle_part_tires.not_inspected)

        vehicle_part_tires.not_inspected = True
        vehicle_part_tires._onchange_not_inspected()
        self.assertFalse(vehicle_part_tires.required_attention)
        self.assertFalse(vehicle_part_tires.further_attention)
        self.assertFalse(vehicle_part_tires.okay_for_now)

        self.assertFalse(vehicle_part_tires.action_inspection_button())

    def test_vehicle_brake_condition(self):
        vehicle_brake_condition = self.env["vehicle.brake.condition"].create({
            "vehicle_part_info_id": self.part_brake_condition.id,
            "inspection_job_card_id": self.inspection_job_card.id})

        vehicle_brake_condition.okay_for_now = True
        vehicle_brake_condition._onchange_okay_for_now()
        self.assertFalse(vehicle_brake_condition.further_attention)
        self.assertFalse(vehicle_brake_condition.required_attention)
        self.assertFalse(vehicle_brake_condition.not_inspected)

        vehicle_brake_condition.further_attention = True
        vehicle_brake_condition._onchange_further_attention()
        self.assertFalse(vehicle_brake_condition.okay_for_now)
        self.assertFalse(vehicle_brake_condition.required_attention)
        self.assertFalse(vehicle_brake_condition.not_inspected)

        vehicle_brake_condition.required_attention = True
        vehicle_brake_condition._onchange_required_attention()
        self.assertFalse(vehicle_brake_condition.further_attention)
        self.assertFalse(vehicle_brake_condition.okay_for_now)
        self.assertFalse(vehicle_brake_condition.not_inspected)

        vehicle_brake_condition.not_inspected = True
        vehicle_brake_condition._onchange_not_inspected()
        self.assertFalse(vehicle_brake_condition.required_attention)
        self.assertFalse(vehicle_brake_condition.further_attention)
        self.assertFalse(vehicle_brake_condition.okay_for_now)

        self.assertFalse(vehicle_brake_condition.action_inspection_button())

    def test_vehicle_condition(self):
        # Check Required field
        with self.assertLogs("odoo.sql_db", level="ERROR"):
            with self.assertRaises(psycopg2.errors.NotNullViolation):
                self.env["vehicle.condition"].create({})
        vehicle_condition = self.env["vehicle.condition"].create({
            "condition": "Condition", "condition_code": "P1"})
        vehicle_condition_two = self.env["vehicle.condition"].create({
            "condition": "Condition", "condition_code": "P2"})
        # Check validation of the create method
        with self.assertRaisesRegex(ValidationError, "Condition Code P1 is al"
                                    "ready in use. Please try a different one."):
            self.env["vehicle.condition"].create({
                "condition": "Condition", "condition_code": "P1"})
        # Check validation of the write method
        with self.assertRaisesRegex(ValidationError, "Condition Code P1 is al"
                                    "ready in use. Please try a different one."):
            vehicle_condition_two.write({"condition_code": "P1"})

    def test_vehicle_item(self):
        vehicle_item = self.env["vehicle.item"].create({
            "name": "Name", })
        with self.assertRaisesRegex(ValidationError, "Please select a category "
                                    "type: Mechanical Item or Interior Item"):
            vehicle_item._check_item_category()

    def test_vehicle_component(self):
        vehicle_component = self.env["vehicle.component"].create({
            "name": "Name"})
        with self.assertRaisesRegex(ValidationError, 'Please select a vehicle '
                                    'side: Top Side or Bottom Side'):
            vehicle_component._check_compo_vehicle_side()

    def test_vehicle_fluid(self):
        vehicle_fluid = self.env["vehicle.fluid"].create({"name": "Name"})
        with self.assertRaisesRegex(ValidationError, "Please select a vehicle "
                                    "side: Top Side or Bottom Side"):
            vehicle_fluid._check_fluid_vehicle_side()

    def test_checklist_template(self):
        with self.assertLogs("odoo.sql_db", level="ERROR"):
            with self.assertRaises(psycopg2.errors.NotNullViolation):
                self.env["checklist.template"].create({})

    def test_booking_appointment_slot(self):

        with self.assertRaisesRegex(ValidationError, "Closing Time cannot be "
                                    "less than Starting Time."):
            self.env["booking.appointment.slot"].create({
                "title": "Title", "from_time": 11.0, "to_time": 10.0, })

        with self.assertRaisesRegex(ValidationError, "Closing Time must be "
                                    "between 0 and 24."):
            self.env["booking.appointment.slot"].create({
                "title": "Title", "from_time": 11.0, "to_time": 25.0, })

        with self.assertRaisesRegex(ValidationError, "Starting Time must be "
                                    "between 0 and 24."):
            self.env["booking.appointment.slot"].create({
                "title": "Title", "from_time": 25.0, "to_time": 10.0, })

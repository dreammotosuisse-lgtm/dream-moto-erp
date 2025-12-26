from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from .common import VehicleRepairData


@tagged("vehicle_register")
class TestVehicleRegister(VehicleRepairData):

    def test_register_vehicle(self):
        # create method
        register_vehicle = self.env["register.vehicle"].create({
            "customer_id": self.customer.id, "vehicle_brand_id":
            self.vehicle_brand.id, "vehicle_model_id": self.vehicle_model.id,
            "registration_no": "5647382910", "vehicle_fuel_type_id": self.
            fuel_type.id, "transmission_type": "automatic", "vin_no": "132"})

        register_vehicle._compute_display_name()
        self.assertEqual(register_vehicle.display_name, "VB/VM/5647382910")
        with self.assertRaisesRegex(ValidationError,
                                    "Registration 5647382910 is already in " \
                                    "use. Please try a different one."):
            self.env["register.vehicle"].create({
            "customer_id": self.customer.id, "vehicle_brand_id":
            self.vehicle_brand.id, "vehicle_model_id": self.vehicle_brand.id,
            "registration_no": "5647382910", "vehicle_fuel_type_id": self.
            fuel_type.id, "transmission_type": "automatic", "vin_no": "132"})
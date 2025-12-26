from odoo.tests.common import tagged
from .common import VehicleRepairData


@tagged("vehicle_dashboard")
class TestVehicleDashboard(VehicleRepairData):

    def test_dashboard(self):
        bookings = []
        inspection_job_cards = []
        repair_job_cards = []
        for _ in range(5):
            bookings.append(self._create_booking({
                "customer_id": self.customer.id, "vehicle_brand_id":
                    self.vehicle_brand.id, "registration_no": "12345",
                "vehicle_model_id": self.vehicle_model.id,
                "vehicle_fuel_type_id": self.fuel_type.id,
                "street": "Street One", "street2": "Street Two",
                "city": "City", "country_id": 104, "state_id": 12, "zip":
                    "305013", "phone": "1234567890", "email": "Email@gmail.com", }))

        for _ in range(5):
            inspection_job_cards.append(self._create_inspection_job_card({
                "vehicle_brand_id": self.vehicle_brand.id, "vehicle_model_id":
                    self.vehicle_model.id, "vehicle_fuel_type_id": self.fuel_type.id,
                "customer_id": self.customer.id, "email": "Email@gmail.com",
                "street": "Street One", "street2": "Street Two",
                "city": "City", "country_id": 104, "state_id": 12,
                "zip": "305013", "phone": "1234567890", "inspect_type":
                    "only_inspection", "vin_no":
                    "1234", "transmission_type": "automatic"}))

        for _ in range(6):
            repair_job_cards.append(self._create_repair_job_card({
                "customer_id": self.customer.id, "vehicle_brand_id":
                    self.vehicle_brand.id, "vehicle_model_id": self.vehicle_model.id,
                "vehicle_fuel_type_id": self.fuel_type.id,
                "registration_no": "613211621354", "email": "Email@gmail.com",
                "street": "Street One", "street2": "Street Two",
                "city": "City", "country_id": 104, "state_id": 12,
                "zip": "305013", "phone": "1234567890", }))

        bookings[0].write({
            "booking_stages": "vehicle_inspection", "booking_source": "direct"})
        bookings[1].write({
            "booking_stages": "vehicle_repair", "booking_source": "direct"})
        bookings[2].write({
            "booking_stages": "vehicle_inspection_repair", "booking_source":
                "website"})
        bookings[3].write({
            "booking_stages": "vehicle_inspection_repair", "booking_source":
                "website"})
        bookings[4].write({
            "booking_stages": "cancel", "booking_source": "website"})

        inspection_job_cards[0].write({
            "stages": "a_draft", "inspection_type": "full_inspection"})
        inspection_job_cards[1].write({
            "stages": "b_in_progress", "inspection_type": "specific_inspection"})
        inspection_job_cards[2].write({
            "stages": "c_complete", "inspection_type": "full_inspection"})
        inspection_job_cards[3].write({
            "stages": "c_complete", "inspection_type": "specific_inspection"})
        inspection_job_cards[4].write({
            "stages": "d_cancel", "inspection_type": "full_inspection"})

        repair_job_cards[0].write({"stages": "assign_to_technician"})
        repair_job_cards[1].write({"stages": "in_diagnosis"})
        repair_job_cards[2].write({"stages": "supervisor_inspection"})
        repair_job_cards[3].write({"stages": "hold"})
        repair_job_cards[4].write({"stages": "complete"})
        repair_job_cards[5].write({"stages": "cancel"})

        dashboard = self.env["advance.vehicle.repair.dashboard"].create({})
        data = dashboard.get_advance_vehicle_repair_dashboard()
        self.assertEqual(data["total_vehicle_booking"], 16)
        self.assertEqual(data["vehicle_inspection"], 2)
        self.assertEqual(data["vehicle_repair"], 3)
        self.assertEqual(data["vehicle_inspection_repair"], 3)
        self.assertEqual(data["booking_cancel"], 1)
        self.assertEqual(data["total_inspection_job_card"], 12)
        self.assertEqual(data["inspection_in_progress"], 1)
        self.assertEqual(data["inspection_complete"], 2)
        self.assertEqual(data["inspection_cancel"], 1)
        self.assertEqual(data["repair_job_card_details"], [
            ['Assign', 'In Diagnosis', 'In Inspection', 'Hold', 'Completed', 'Cancelled'],
            [2, 2, 2, 2, 2, 2]])
        self.assertEqual(data["booking_details"], [
            ['Vehicle Inspection', 'Vehicle Repair', 'Vehicle Inspection and Repair'], [2, 3, 3]])
        self.assertEqual(data["booking_source"], [['Direct', 'Website'], [10, 6]])
        self.assertEqual(data["inspection_draft"], 5)
        self.assertEqual(data["repair_job_card"], 14)
        self.assertEqual(data["service_teams"], 2)
        self.assertEqual(data["vehicle_customers"], 62)
        self.assertEqual(data["booking_source_direct"], 10)
        self.assertEqual(data["booking_source_website"], 6)
        self.assertEqual(data["inspection_job_card_details"], [
            ['Full Inspection', 'Specific Inspection'], [3, 9]])
        self.assertEqual(data["type_full_inspection"], 3)
        self.assertEqual(data["type_specific_inspection"], 9)
        self.assertIn("Fuel", data["common_fuel_used_in_vehicle"][0])
        self.assertIn(5, data["common_fuel_used_in_vehicle"][1])

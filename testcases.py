import os
import pickle
import unittest
from objects import (
    User, Customer, Admin,
    Event, Ticket, SingleRacePass, WeekendPackage,
    SeasonMembership, GroupDiscount, Payment,
    Reservation, SystemManager
)

class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User("ahmed", "secret", "ahmed ebrahim")

    def test_username_name_getters_setters(self):
        self.assertEqual(self.user.get_username(), "ahmed")
        self.user.set_username("ahmed2")
        self.assertEqual(self.user.get_username(), "ahmed2")

        self.assertEqual(self.user.get_name(), "ahmed ebrahim")
        self.user.set_name("A. ebrahim")
        self.assertEqual(self.user.get_name(), "A. ebrahim")

    def test_password_check(self):
        self.assertTrue(self.user.check_password("secret"))
        self.assertFalse(self.user.check_password("wrong"))


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("Sultan", "pw", "Sultan")

    def test_reservation_management(self):
        # create dummy reservation
        event = Event("E1", "Race 1", "2025-06-10", 100)
        payment = Payment(0, "card")
        res = Reservation("R1", event, payment)

        self.customer.add_reservation(res)
        self.assertEqual(len(self.customer.get_reservations()), 1)

        self.customer.delete_reservation("R1")
        self.assertEqual(len(self.customer.get_reservations()), 0)


class TestAdmin(unittest.TestCase):
    def setUp(self):
        self.admin = Admin("admin", "pw", "Administrator")
        self.mgr = SystemManager()
        self.mgr._sales_log = {"E1": 5}

    def test_view_sales_report_and_update_discounts(self):
        report = self.admin.view_sales_report(self.mgr)
        self.assertEqual(report, {"E1": 5})

        new_rules = {"SingleRacePass": 10.0}
        self.admin.update_discounts(self.mgr, new_rules)
        self.assertEqual(self.mgr._discount_rules, new_rules)


class TestEvent(unittest.TestCase):
    def setUp(self):
        self.event = Event("E2", "Race 2", "2025-07-15", 50)

    def test_capacity_and_sales(self):
        self.assertEqual(self.event.get_remaining_capacity(), 50)
        self.event.increment_tickets_sold(3)
        self.assertEqual(self.event.get_tickets_sold(), 3)
        self.assertEqual(self.event.get_remaining_capacity(), 47)

        self.event.set_capacity(100)
        self.assertEqual(self.event.get_capacity(), 100)


class TestTickets(unittest.TestCase):
    def test_general_ticket(self):
        t = Ticket("T1", 150.0, "General")
        self.assertEqual(t.get_price(), 150.0)
        t.set_price(200.0)
        self.assertEqual(t.get_price(), 200.0)
        self.assertEqual(t.get_type(), "General")
        t.set_type("VIP")
        self.assertEqual(t.get_type(), "VIP")

    def test_specialized_tickets(self):
        s = SingleRacePass("S1", 100.0)
        w = WeekendPackage("W1", 180.0)
        m = SeasonMembership("M1", 800.0)
        g = GroupDiscount("G1", 400.0, group_size=4)

        for ticket, expected_type in [
            (s, "SingleRacePass"),
            (w, "WeekendPackage"),
            (m, "SeasonMembership"),
            (g, "GroupDiscount")
        ]:
            self.assertEqual(ticket.get_type(), expected_type)
        
        self.assertEqual(g.get_group_size(), 4)
        g.set_group_size(5)
        self.assertEqual(g.get_group_size(), 5)


class TestPayment(unittest.TestCase):
    def setUp(self):
        self.pay = Payment(250.0, "digital_wallet")

    def test_amount_and_method(self):
        self.assertEqual(self.pay.get_amount(), 250.0)
        self.pay.set_amount(300.0)
        self.assertEqual(self.pay.get_amount(), 300.0)

        self.assertEqual(self.pay.get_method(), "digital_wallet")
        self.pay.set_method("credit_card")
        self.assertEqual(self.pay.get_method(), "credit_card")


class TestReservation(unittest.TestCase):
    def setUp(self):
        self.event = Event("E3", "Race 3", "2025-08-20", 2)
        self.payment = Payment(0, "card")
        self.res = Reservation("R2", self.event, self.payment)

    def test_add_ticket_and_total_price(self):
        t1 = SingleRacePass("S2", 120.0)
        t2 = SingleRacePass("S3", 130.0)

        self.res.add_ticket(t1)
        self.res.add_ticket(t2)
        self.assertEqual(self.res.get_total_price(), 250.0)
        self.assertEqual(self.event.get_tickets_sold(), 2)
        self.assertEqual(self.event.get_remaining_capacity(), 0)

        # adding beyond capacity should raise
        with self.assertRaises(ValueError):
            self.res.add_ticket(SingleRacePass("S4", 140.0))


class TestSystemManager(unittest.TestCase):
    def setUp(self):
        self.data_file = "test_system_data.pkl"
        # ensure clean state
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        self.mgr = SystemManager(self.data_file)

    def tearDown(self):
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_save_and_load_data(self):
        self.mgr.set_discount_rules({"WeekendPackage": 20.0})
        self.mgr._sales_log = {"E4": 7}
        self.mgr.save_data()

        # create new manager to load from file
        mgr2 = SystemManager(self.data_file)
        mgr2.load_data()
        self.assertEqual(mgr2._discount_rules, {"WeekendPackage": 20.0})
        self.assertEqual(mgr2._sales_log, {"E4": 7})

    def test_log_sale(self):
        event = Event("E5", "Race 5", "2025-09-10", 10)
        self.mgr.log_sale(event, 3)
        self.assertEqual(self.mgr._sales_log["E5"], 3)
        # log additional
        self.mgr.log_sale(event, 2)
        self.assertEqual(self.mgr._sales_log["E5"], 5)


if __name__ == "__main__":
    unittest.main()

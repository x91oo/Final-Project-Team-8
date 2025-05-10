import pickle
from typing import List, Dict

# Base user class
class User:
    def __init__(self, username: str, password: str, name: str):
        self._username = username
        self._password = password
        self._name = name

    # Username
    def get_username(self) -> str:
        return self._username

    def set_username(self, username: str):
        self._username = username

    # Name
    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    # Password check (no setter for security)
    def check_password(self, password: str) -> bool:
        return self._password == password


# Customer inherits from User
class Customer(User):
    def __init__(self, username: str, password: str, name: str):
        super().__init__(username, password, name)
        self._reservations: List['Reservation'] = []

    def get_reservations(self) -> List['Reservation']:
        return self._reservations

    def add_reservation(self, reservation: 'Reservation'):
        self._reservations.append(reservation)

    def delete_reservation(self, reservation_id: str):
        self._reservations = [
            r for r in self._reservations if r.get_reservation_id() != reservation_id
        ]


# Admin inherits from User
class Admin(User):
    def __init__(self, username: str, password: str, name: str):
        super().__init__(username, password, name)

    def view_sales_report(self, system_manager: 'SystemManager') -> Dict:
        return system_manager.track_sales()

    def update_discounts(self, system_manager: 'SystemManager', new_rules):
        system_manager.set_discount_rules(new_rules)


# Represents a racing event
class Event:
    def __init__(self, event_id: str, name: str, date: str, capacity: int):
        self._event_id = event_id
        self._name = name
        self._date = date
        self._capacity = capacity
        self._tickets_sold = 0

    # Event ID
    def get_event_id(self) -> str:
        return self._event_id

    # Name
    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    # Date
    def get_date(self) -> str:
        return self._date

    def set_date(self, date: str):
        self._date = date

    # Capacity and sales
    def get_capacity(self) -> int:
        return self._capacity

    def set_capacity(self, capacity: int):
        self._capacity = capacity

    def get_tickets_sold(self) -> int:
        return self._tickets_sold

    def increment_tickets_sold(self, count: int = 1):
        self._tickets_sold += count

    def get_remaining_capacity(self) -> int:
        return self._capacity - self._tickets_sold


# General Ticket
class Ticket:
    def __init__(self, ticket_id: str, price: float, ticket_type: str):
        self._ticket_id = ticket_id
        self._price = price
        self._type = ticket_type

    # ID
    def get_ticket_id(self) -> str:
        return self._ticket_id

    # Price
    def get_price(self) -> float:
        return self._price

    def set_price(self, price: float):
        self._price = price

    # Type
    def get_type(self) -> str:
        return self._type

    def set_type(self, ticket_type: str):
        self._type = ticket_type


# Specific ticket types (can add extra attributes/methods if needed)
class SingleRacePass(Ticket):
    def __init__(self, ticket_id: str, price: float):
        super().__init__(ticket_id, price, "SingleRacePass")


class WeekendPackage(Ticket):
    def __init__(self, ticket_id: str, price: float):
        super().__init__(ticket_id, price, "WeekendPackage")


class SeasonMembership(Ticket):
    def __init__(self, ticket_id: str, price: float):
        super().__init__(ticket_id, price, "SeasonMembership")


class GroupDiscount(Ticket):
    def __init__(self, ticket_id: str, price: float, group_size: int):
        super().__init__(ticket_id, price, "GroupDiscount")
        self._group_size = group_size

    def get_group_size(self) -> int:
        return self._group_size

    def set_group_size(self, size: int):
        self._group_size = size


# Payment details
class Payment:
    def __init__(self, amount: float, method: str):
        self._amount = amount
        self._method = method

    # Amount
    def get_amount(self) -> float:
        return self._amount

    def set_amount(self, amount: float):
        self._amount = amount

    # Method
    def get_method(self) -> str:
        return self._method

    def set_method(self, method: str):
        self._method = method


# Reservation / Purchase Order
class Reservation:
    def __init__(self, reservation_id: str, event: Event, payment: Payment):
        self._reservation_id = reservation_id
        self._event = event
        self._tickets: List[Ticket] = []
        self._payment = payment

    def get_reservation_id(self) -> str:
        return self._reservation_id

    def get_event(self) -> Event:
        return self._event

    def get_tickets(self) -> List[Ticket]:
        return self._tickets

    def add_ticket(self, ticket: Ticket):
        if self._event.get_remaining_capacity() > 0:
            self._tickets.append(ticket)
            self._event.increment_tickets_sold(1)
        else:
            raise ValueError("Event sold out")

    def get_total_price(self) -> float:
        return sum(t.get_price() for t in self._tickets)


# Manages persistence and administrative logic
class SystemManager:
    def __init__(self, data_file: str = "system_data.pkl"):
        self._data_file = data_file
        self._discount_rules = {}
        self._sales_log: Dict[str, int] = {}  # event_id -> tickets sold

    def load_data(self):
        try:
            with open(self._data_file, "rb") as f:
                data = pickle.load(f)
                self._discount_rules = data.get("discounts", {})
                self._sales_log = data.get("sales", {})
        except FileNotFoundError:
            # No existing data; start fresh
            pass

    def save_data(self):
        data = {
            "discounts": self._discount_rules,
            "sales": self._sales_log
        }
        with open(self._data_file, "wb") as f:
            pickle.dump(data, f)

    def set_discount_rules(self, rules):
        self._discount_rules = rules

    def calculate_discounts(self, ticket: Ticket) -> float:
        # Example: apply a flat discount if rule exists for type
        return self._discount_rules.get(ticket.get_type(), 0.0)

    def track_sales(self) -> Dict[str, int]:
        return dict(self._sales_log)

    def log_sale(self, event: Event, count: int = 1):
        eid = event.get_event_id()
        self._sales_log[eid] = self._sales_log.get(eid, 0) + count

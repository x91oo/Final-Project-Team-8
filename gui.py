import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import os
from objects import (
    Customer, Admin, Event,
    SingleRacePass, WeekendPackage,
    SeasonMembership, GroupDiscount,
    Reservation, Payment, SystemManager
)

# File constants
CUSTOMERS_FILE = "customers.pkl"
EVENTS_FILE = "events.pkl"

# Helper functions for persistence

def load_customers():
    try:
        with open(CUSTOMERS_FILE, "rb") as f:
            return pickle.load(f)
    except Exception:
        return []


def save_customers(customers):
    with open(CUSTOMERS_FILE, "wb") as f:
        pickle.dump(customers, f)


def load_events():
    # Initialize sample events if none exist
    if not os.path.exists(EVENTS_FILE):
        sample = [
            Event("E1", "Friday Practice", "2025-11-21", 200),
            Event("E2", "Qualifying", "2025-11-22", 200),
            Event("E3", "Grand Prix Race", "2025-11-23", 200),
        ]
        save_events(sample)
        return sample
    try:
        with open(EVENTS_FILE, "rb") as f:
            return pickle.load(f)
    except Exception:
        return []


def save_events(events):
    with open(EVENTS_FILE, "wb") as f:
        pickle.dump(events, f)


class TicketBookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grand Prix Ticket Booking System")
        self.geometry("700x500")

        # Load data
        self.customers = load_customers()
        self.events = load_events()
        self.system_manager = SystemManager()
        self.system_manager.load_data()

        # Current user
        self.current_user = None

        # Container for frames
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialize frames
        self.frames = {}
        for F in (LoginFrame, CustomerFrame, ViewReservationsFrame,
                  NewReservationFrame, EditProfileFrame,
                  AdminFrame, ViewSalesFrame, UpdateDiscountFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        # Call loaders explicitly after frame is raised
        if hasattr(frame, 'load_reservations'):
            frame.load_reservations()
        if hasattr(frame, 'update_report'):
            frame.update_report()
        if hasattr(frame, 'load_profile'):
            frame.load_profile()

    def on_closing(self):
        # Save all data
        save_customers(self.customers)
        save_events(self.events)
        self.system_manager.save_data()
        self.destroy()


class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Login", font=(None, 16)).pack(pady=10)

        frm = ttk.Frame(self)
        frm.pack(pady=20)
        ttk.Label(frm, text="Username:").grid(row=0, column=0, sticky="e")
        self.username_entry = ttk.Entry(frm)
        self.username_entry.grid(row=0, column=1)

        ttk.Label(frm, text="Password:").grid(row=1, column=0, sticky="e")
        self.password_entry = ttk.Entry(frm, show="*")
        self.password_entry.grid(row=1, column=1)

        # Role selection
        self.role_var = tk.StringVar(value="Customer")
        ttk.Radiobutton(frm, text="Customer", variable=self.role_var, value="Customer").grid(row=2, column=0)
        ttk.Radiobutton(frm, text="Admin", variable=self.role_var, value="Admin").grid(row=2, column=1)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Login", command=self.login).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Create Account", command=self.create_account).pack(side="left", padx=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if role == "Customer":
            for cust in self.app.customers:
                if cust.get_username() == username and cust.check_password(password):
                    self.app.current_user = cust
                    messagebox.showinfo("Success", f"Welcome, {cust.get_name()}!")
                    self.app.show_frame("CustomerFrame")
                    return
            messagebox.showerror("Error", "Invalid customer credentials.")

        else:  # Admin
            if username == "admin" and password == "admin":
                self.app.current_user = Admin(username, password, "Administrator")
                messagebox.showinfo("Success", "Logged in as Admin.")
                self.app.show_frame("AdminFrame")
            else:
                messagebox.showerror("Error", "Invalid admin credentials.")

    def create_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        name = username
        if not username or not password:
            messagebox.showerror("Error", "Enter username and password to create account.")
            return
        for cust in self.app.customers:
            if cust.get_username() == username:
                messagebox.showerror("Error", "Username already exists.")
                return
        new_cust = Customer(username, password, name)
        self.app.customers.append(new_cust)
        save_customers(self.app.customers)
        messagebox.showinfo("Success", "Account created. You can now log in.")


class CustomerFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Customer Dashboard", font=(None, 16)).pack(pady=10)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="View Reservations", width=20,
                   command=lambda: app.show_frame("ViewReservationsFrame")).pack(pady=5)
        ttk.Button(btn_frame, text="New Reservation", width=20,
                   command=lambda: app.show_frame("NewReservationFrame")).pack(pady=5)
        ttk.Button(btn_frame, text="Edit Profile", width=20,
                   command=lambda: app.show_frame("EditProfileFrame")).pack(pady=5)
        ttk.Button(btn_frame, text="Logout", width=20,
                   command=lambda: app.show_frame("LoginFrame")).pack(pady=5)


class EditProfileFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Edit Profile", font=(None, 16)).pack(pady=10)

        frm = ttk.Frame(self)
        frm.pack(pady=20)
        ttk.Label(frm, text="Display Name:").grid(row=0, column=0, sticky="e")
        self.name_entry = ttk.Entry(frm)
        self.name_entry.grid(row=0, column=1)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save_name).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=lambda: app.show_frame("CustomerFrame")).pack(side="left", padx=5)

    def load_profile(self):
        """Populate the entry with the current user's name."""
        if self.app.current_user:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.app.current_user.get_name())

    def save_name(self):
        """Save the new name and persist to file."""
        new_name = self.name_entry.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return
        # Update the user object
        self.app.current_user.set_name(new_name)
        # Persist customers
        save_customers(self.app.customers)
        messagebox.showinfo("Success", "Your display name has been updated.")
        # Return to dashboard
        self.app.show_frame("CustomerFrame")


class ViewReservationsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Your Reservations", font=(None, 16)).pack(pady=10)

        self.listbox = tk.Listbox(self, width=80)
        self.listbox.pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Delete Reservation", command=self.delete_res).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=lambda: app.show_frame("CustomerFrame")).pack(side="left", padx=5)

    def load_reservations(self):
        if not self.app.current_user:
            return
        self.listbox.delete(0, tk.END)
        for res in self.app.current_user.get_reservations():
            self.listbox.insert(tk.END,
                                f"ID: {res.get_reservation_id()} | Event: {res.get_event().get_name()} | Total: ${res.get_total_price():.2f}")

    def delete_res(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showerror("Error", "Select a reservation to delete.")
            return
        idx = sel[0]
        res = self.app.current_user.get_reservations()[idx]
        self.app.current_user.delete_reservation(res.get_reservation_id())
        save_customers(self.app.customers)
        messagebox.showinfo("Success", "Reservation deleted.")
        self.load_reservations()


class NewReservationFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="New Reservation", font=(None, 16)).pack(pady=10)

        frm = ttk.Frame(self)
        frm.pack(pady=10)
        ttk.Label(frm, text="Event:").grid(row=0, column=0)
        self.event_cb = ttk.Combobox(frm, values=[e.get_name() for e in app.events])
        self.event_cb.grid(row=0, column=1)

        ttk.Label(frm, text="Ticket Type:").grid(row=1, column=0)
        self.type_cb = ttk.Combobox(frm, values=["SingleRacePass","WeekendPackage","SeasonMembership","GroupDiscount"]) 
        self.type_cb.grid(row=1, column=1)

        ttk.Label(frm, text="Quantity:").grid(row=2, column=0)
        self.qty_entry = ttk.Entry(frm)
        self.qty_entry.grid(row=2, column=1)

        ttk.Label(frm, text="Payment Method:").grid(row=3, column=0)
        self.pay_cb = ttk.Combobox(frm, values=["Credit Card","Digital Wallet"])   
        self.pay_cb.grid(row=3, column=1)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Purchase", command=self.purchase).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=lambda: app.show_frame("CustomerFrame")).pack(side="left", padx=5)

    def purchase(self):
        ev_name = self.event_cb.get()
        ttype = self.type_cb.get()
        qty = self.qty_entry.get().strip()
        method = self.pay_cb.get()
        if not ev_name or not ttype or not qty.isdigit() or not method:
            messagebox.showerror("Error", "Fill all fields correctly.")
            return
        qty = int(qty)
        event = next((e for e in self.app.events if e.get_name()==ev_name), None)
        if not event:
            messagebox.showerror("Error", "Invalid event selected.")
            return
        rid = f"{self.app.current_user.get_username()}_{len(self.app.current_user.get_reservations())+1}"
        payment = Payment(0.0, method)
        res = Reservation(rid, event, payment)
        total = 0.0
        for i in range(qty):
            if ttype == "SingleRacePass":
                ticket = SingleRacePass(f"{rid}_{i+1}", 100.0)
            elif ttype == "WeekendPackage":
                ticket = WeekendPackage(f"{rid}_{i+1}", 180.0)
            elif ttype == "SeasonMembership":
                ticket = SeasonMembership(f"{rid}_{i+1}", 800.0)
            else:
                ticket = GroupDiscount(f"{rid}_{i+1}", 400.0, group_size=qty)
            disc = self.app.system_manager.calculate_discounts(ticket)
            price = ticket.get_price() - disc
            total += price
            res.add_ticket(ticket)
            self.app.system_manager.log_sale(event, 1)
        payment.set_amount(total)
        self.app.current_user.add_reservation(res)
        save_customers(self.app.customers)
        self.app.system_manager.save_data()
        messagebox.showinfo("Success", f"Purchased {qty} ticket(s). Total: ${total:.2f}")
        self.app.show_frame("CustomerFrame")


class AdminFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Admin Dashboard", font=(None, 16)).pack(pady=10)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="View Sales", width=20,
                   command=lambda: app.show_frame("ViewSalesFrame")).pack(pady=5)
        ttk.Button(btn_frame, text="Update Discounts", width=20,
                   command=lambda: app.show_frame("UpdateDiscountFrame")).pack(pady=5)
        ttk.Button(btn_frame, text="Logout", width=20,
                   command=lambda: app.show_frame("LoginFrame")).pack(pady=5)


class ViewSalesFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Sales Report", font=(None, 16)).pack(pady=10)
        self.txt = tk.Text(self, width=80, height=20)
        self.txt.pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: app.show_frame("AdminFrame")).pack()

    def update_report(self):
        self.txt.delete("1.0", tk.END)
        sales = self.app.system_manager.track_sales()
        for eid, count in sales.items():
            event = next((e for e in self.app.events if e.get_event_id()==eid), None)
            name = event.get_name() if event else eid
            self.txt.insert(tk.END, f"{name}: {count} tickets sold\n")


class UpdateDiscountFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Update Discount Rules", font=(None, 16)).pack(pady=10)
        frm = ttk.Frame(self)
        frm.pack(pady=10)
        ttk.Label(frm, text="Ticket Type:").grid(row=0, column=0)
        self.type_cb = ttk.Combobox(frm, values=["SingleRacePass","WeekendPackage","SeasonMembership","GroupDiscount"])
        self.type_cb.grid(row=0, column=1)
        ttk.Label(frm, text="Discount Amount:").grid(row=1, column=0)
        self.amount_entry = ttk.Entry(frm)
        self.amount_entry.grid(row=1, column=1)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Apply", command=self.apply).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=lambda: app.show_frame("AdminFrame")).pack(side="left", padx=5)

    def apply(self):
        ttype = self.type_cb.get()
        amt = self.amount_entry.get().strip()
        if not ttype or not amt.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Select type and valid amount.")
            return
        amt_f = float(amt)
        admin = self.app.current_user  # type: Admin
        admin.update_discounts(self.app.system_manager, {ttype: amt_f})
        self.app.system_manager.save_data()
        messagebox.showinfo("Success", f"Discount for {ttype} set to ${amt_f:.2f}")


if __name__ == "__main__":
    app = TicketBookingApp()
    app.mainloop()

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import requests

API_BASE_URL = "https://setasynctutor.admin.trafft.com/api/v1/appointments"
AUTH_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NldGFzeW5jdHV0b3J0cmFmZnQuY29tIiwiaWF0IjoxNzQ3NTk4NzE4LCJlbWFpbCI6ImNvbnRhY3RAc2V0YXN5bmMubWUifQ.m3hpFcofevPvYEw6DnaVLYZbSzNEuu3upZQHEhenLqc"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "authorization": AUTH_TOKEN
}

@dataclass
class Customer:
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    description_html: str

    @property
    def fullname(self):
        return self.first_name + " " + self.last_name

@dataclass
class Booking:
    id: int
    status: str
    invoice_amount: float
    invoice_paid: float
    customer: Customer
    custom_fields: List[dict]

@dataclass
class Employee:
    first_name: str
    last_name: str
    avatar_url: Optional[str]

    @property
    def fullname(self):
        return self.first_name + " " + self.last_name

@dataclass
class Appointment:
    id: int
    note: str
    status: int
    service_name: str
    service_color: str
    start: datetime
    location: Optional[str]
    hangouts_link: Optional[str]
    employee: Employee
    bookings: List[Booking]

    @staticmethod
    def from_json(data: dict) -> "Appointment":
        start_dt = datetime.strptime(data["startDateTime"], "%Y-%m-%d %H:%M")

        bookings = []
        for b in data.get("bookings", []):
            cust = b.get("customer", {})
            customer = Customer(
                first_name=cust.get("firstName", ""),
                last_name=cust.get("lastName", ""),
                email=cust.get("email", ""),
                phone=cust.get("phoneNumber"),
                description_html=cust.get("description", "")
            )
            bookings.append(Booking(
                id=b["id"],
                status=b["status"],
                invoice_amount=b.get("invoiceAmount", 0),
                invoice_paid=b.get("invoiceAmountPaid", 0),
                customer=customer,
                custom_fields=b.get("customFields", [])
            ))

        emp = data.get("employee", {})
        employee = Employee(
            first_name=emp.get("firstName", ""),
            last_name=emp.get("lastName", ""),
            avatar_url=emp.get("mediaUrl")
        )

        return Appointment(
            id=data["id"],
            note=data.get("note", ""),
            status=data.get("status", 0),
            service_name=data.get("serviceName", ""),
            service_color=data.get("serviceColor", "#000000"),
            start=start_dt,
            location=data.get("locationName"),
            hangouts_link=data.get("hangoutsLink"),
            employee=employee,
            bookings=bookings
        )


class Client:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.firstName = data.get("firstName")
        self.lastName = data.get("lastName")
        self.email = data.get("email")
        self.status = data.get("status")
        self.activated = data.get("activated")
        self.mediaUrl = data.get("mediaUrl")  # note: fix typo from medialUrl to mediaUrl if needed
        self.permittedActions = data.get("permittedActions", {})
        self.createdAt = data.get("createdAt")
        self.stats = data.get("stats", {})

    def __repr__(self):
        return (f"<Customer id={self.id} name={self.firstName} {self.lastName} "
                f"email={self.email} status={self.status}>")

def getClient(searchQuery):
    url = "https://setasynctutor.admin.trafft.com/api/v1/users/customers"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NldGFzeW5jdHV0b3J0cmFmZnQuY29tIiwiaWF0IjoxNzQ3NTk4NzE4LCJlbWFpbCI6ImNvbnRhY3RAc2V0YXN5bmMubWUifQ.m3hpFcofevPvYEw6DnaVLYZbSzNEuu3upZQHEhenLqc",
        "referer": "https://setasynctutor.admin.trafft.com/customers",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }
    params = {
        "page": 1,
        "search": searchQuery
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    customers = data.get("customers", [])

    if len(customers) == 1:
        return Client(customers[0])
    elif len(customers) > 1:
        return False  # multiple matches found
    else:
        return None

def getAppointment(appointment_id: int) -> Optional[Appointment]:
    if not isinstance(appointment_id, int) or appointment_id < 0 or appointment_id > 9999:
        return None

    try:
        response = requests.get(f"{API_BASE_URL}/{appointment_id}/details", headers=HEADERS)
        response.raise_for_status()
        return Appointment.from_json(response.json())
    except requests.RequestException as e:
        print(f"Error fetching appointment: {e}")
        return None

def addNote(appointmentId: int, noteStr: str) -> bool:
    url = f"https://setasynctutor.admin.trafft.com/api/v1/appointments/note/{appointmentId}"

    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": AUTH_TOKEN,
        "content-type": "application/json",
        "origin": "https://setasynctutor.admin.trafft.com",
        "referer": "https://setasynctutor.admin.trafft.com/appointments",
    }

    payload = {
        "note": noteStr
    }

    try:
        response = requests.post(url, json=payload, headers=headers)#, cookies=COOKIES)
        return response.ok  # True if status_code is 2xx
    except requests.RequestException:
        return False
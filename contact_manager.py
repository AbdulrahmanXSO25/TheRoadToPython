#!/usr/bin/env python3
"""
Simple Contact Manager (v1)

This is a lightweight CLI-based contact manager written in Python.
It allows users to add, view, update, delete, and search contacts.
Each contact includes a name, phone number, and email address.

Contacts are stored in memory using a collection class and
persisted to disk using binary serialization via the `pickle` module.

Features:
- Data validation (email format, non-empty fields)
- Search and sort by contact name
- Persistent storage across sessions
- More and more...
"""


from functools import total_ordering
import re
import os
import pickle
from typing import Union, Iterable, Optional


class StorageManager:
    """
    Handles saving and loading of serialized data to/from a file.
    Uses binary mode for file operations.
    """

    def __init__(self, filename: str):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as file:
                pass
        print(f"[✔️] Storage initialized at {self.filename}")

    def save(self, data: bytes) -> None:
        with open(self.filename, 'wb') as file:
            file.write(data)

    def load(self) -> Optional[bytes]:
        try:
            with open(self.filename, 'rb') as file:
                return file.read()
        except FileNotFoundError:
            print(f"[⚠️] File not found: {self.filename}")
            return None


@total_ordering
class Contact:
    """
    Represents a single contact with name, phone, and email.
    Provides comparison, string representation, and hashing.
    """

    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    def __init__(self, name: str, phone: str, email: str):
        self.name = self._validate_non_empty(name, "name")
        self.phone = self._validate_non_empty(phone, "phone")
        self.email = self._validate_email(email)

    def __str__(self) -> str:
        return f"{self.name} | 📞 {self.phone} | 📧 {self.email}"

    def __repr__(self) -> str:
        return f"Contact(name={self.name!r}, phone={self.phone!r}, email={self.email!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Contact):
            return NotImplemented
        return self.name.lower() == other.name.lower()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Contact):
            return NotImplemented
        return self.name.lower() < other.name.lower()

    def __hash__(self) -> int:
        return hash((self.name.lower(), self.phone, self.email.lower()))

    def to_dict(self) -> dict:
        return {"name": self.name, "phone": self.phone, "email": self.email}

    @staticmethod
    def _validate_non_empty(value: str, field: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError(f"{field.capitalize()} cannot be empty.")
        return value

    @classmethod
    def _validate_email(cls, email: str) -> str:
        email = email.strip()
        if not cls.EMAIL_REGEX.fullmatch(email):
            raise ValueError(f"Invalid email format: {email}")
        return email


class ContactsCollection:
    """
    A collection of Contact objects with support for adding, removing, indexing,
    iteration, searching, and merging.
    """

    def __init__(self, data: Iterable[Contact] = None):
        self._contacts = []
        if data:
            self += data

    def __iadd__(self, other: Union[Contact, Iterable, dict]):
        self._extend(other)
        return self

    def __add__(self, other: Union[Contact, Iterable, dict]):
        new = ContactsCollection(self._contacts)
        new += other
        return new

    def __isub__(self, other: Union[Contact, Iterable, dict]):
        self._remove(other)
        return self

    def __sub__(self, other: Union[Contact, Iterable, dict]):
        new = ContactsCollection(self._contacts)
        new -= other
        return new

    def __len__(self) -> int:
        return len(self._contacts)

    def __getitem__(self, index: int) -> Contact:
        return self._contacts[index]

    def __setitem__(self, index: int, contact: Contact) -> None:
        if not isinstance(contact, Contact):
            raise TypeError("Only Contact instances can be assigned.")
        self._contacts[index] = contact

    def __iter__(self):
        return iter(self._contacts)

    def __contains__(self, contact: Contact) -> bool:
        return contact in self._contacts

    def __str__(self) -> str:
        return "\n".join(str(c) for c in self._contacts)

    def __repr__(self) -> str:
        return f"ContactsCollection({self._contacts!r})"

    def sort(self) -> None:
        self._contacts.sort()

    def find_by_name(self, name: str) -> list:
        return [c for c in self._contacts if c.name.lower() == name.lower()]

    def to_list(self) -> list:
        return [c.to_dict() for c in self._contacts]

    def _add_contact(self, contact: Contact) -> None:
        if not isinstance(contact, Contact):
            raise TypeError("Only Contact instances are allowed.")
        if contact not in self._contacts:
            self._contacts.append(contact)

    def _extend(self, other) -> None:
        if isinstance(other, Contact):
            self._add_contact(other)
        elif isinstance(other, (list, tuple, ContactsCollection)):
            for item in other:
                self._add_contact(item)
        elif isinstance(other, dict):
            for val in other.values():
                self._add_contact(val)
        else:
            raise TypeError("Unsupported type for addition.")

    def _remove(self, other) -> None:
        if isinstance(other, Contact):
            self._contacts.remove(other)
        elif isinstance(other, (list, tuple, ContactsCollection)):
            for item in other:
                self._contacts.remove(item)
        elif isinstance(other, dict):
            for val in other.values():
                self._contacts.remove(val)
        else:
            raise TypeError("Unsupported type for removal.")


class ContactManager:
    """
    CLI-based contact manager with persistence.
    """

    STORAGE_FILE = 'contacts.dat'

    def __init__(self):
        self.contacts = ContactsCollection()
        self.storage = StorageManager(self.STORAGE_FILE)
        self._load_contacts()

    def _load_contacts(self) -> None:
        raw = self.storage.load()
        if raw:
            try:
                loaded = pickle.loads(raw)
                if isinstance(loaded, list):
                    for c in loaded:
                        self.contacts += c
                    print(f"Loaded {len(self.contacts)} contacts.")
            except Exception:
                print("[⚠️] Failed to parse saved contacts.")

    def _save_contacts(self) -> None:
        data = pickle.dumps(list(self.contacts))
        self.storage.save(data)

    def add_contact(self, name: str, phone: str, email: str) -> None:
        try:
            contact = Contact(name, phone, email)
            self.contacts += contact
            self.contacts.sort()
            self._save_contacts()
            print(f"✅ Added: {contact}")
        except Exception as e:
            print(f"[Error] {e}")

    def update_contact(self, name: str, phone: Optional[str] = None, email: Optional[str] = None) -> None:
        matches = self.contacts.find_by_name(name)
        if not matches:
            print(f"[Info] No contact found named '{name}'.")
            return
        contact = matches[0]
        new_phone = phone.strip() if phone else contact.phone
        new_email = email.strip() if email else contact.email
        try:
            updated = Contact(contact.name, new_phone, new_email)
            self.contacts -= contact
            self.contacts += updated
            self.contacts.sort()
            self._save_contacts()
            print(f"✏️ Updated: {updated}")
        except Exception as e:
            print(f"[Error] {e}")

    def delete_contact(self, name: str) -> None:
        matches = self.contacts.find_by_name(name)
        if not matches:
            print(f"[Info] No contact found named '{name}'.")
            return
        for c in matches:
            self.contacts -= c
        self.contacts.sort()
        self._save_contacts()
        print(f"🗑️ Deleted {len(matches)} contact(s) named '{name}'.")

    def view_contacts(self) -> None:
        if not len(self.contacts):
            print("[Info] No contacts to display.")
        else:
            print("\n📒 All Contacts 📒")
            for c in self.contacts:
                print(f" - {c}")

    def search_contact(self, name: str) -> None:
        matches = self.contacts.find_by_name(name)
        if not matches:
            print(f"[Info] No contact found named '{name}'.")
        else:
            print(f"🔎 Found {len(matches)} contact(s) named '{name}':")
            for c in matches:
                print(f" * {c}")


def main():
    manager = ContactManager()
    while True:
        print("\n=== Contact Manager ===")
        print("1) Add Contact")
        print("2) Update Contact")
        print("3) Delete Contact")
        print("4) View Contacts")
        print("5) Search Contact")
        print("6) Exit")
        choice = input("Choose an option [1-6]: ")
        if choice == '1':
            name = input("Name: ")
            phone = input("Phone: ")
            email = input("Email: ")
            manager.add_contact(name, phone, email)
        elif choice == '2':
            name = input("Name to update: ")
            phone = input("New phone (leave blank to keep): ")
            email = input("New email (leave blank to keep): ")
            manager.update_contact(name, phone if phone else None, email if email else None)
        elif choice == '3':
            name = input("Name to delete: ")
            manager.delete_contact(name)
        elif choice == '4':
            manager.view_contacts()
        elif choice == '5':
            name = input("Name to search: ")
            manager.search_contact(name)
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("[Warning] Invalid choice.")


if __name__ == "__main__":
    main()

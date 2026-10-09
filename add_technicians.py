
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "it_service_desk.settings"
)

django.setup()

from django.contrib.auth.models import User, Group

names = [
    ("Ramesh", "Kumar"),
    ("Suresh", "Reddy"),
    ("Priya", "Sharma"),
    ("Rahul", "Verma"),
    ("Anjali", "Rao"),
    ("Arjun", "Kumar"),
    ("Sneha", "Patel"),
    ("Vikram", "Singh"),
    ("Kiran", "Reddy"),
    ("Divya", "Nair"),
]

group, _ = Group.objects.get_or_create(name="Technician")

for first, last in names:
    username = (first + last).lower()

    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password="TechDemo@123",
            first_name=first,
            last_name=last,
        )
        user.groups.add(group)

print("Technicians in database:")

for user in group.user_set.all():
    print(user.get_full_name(), "-", user.username)
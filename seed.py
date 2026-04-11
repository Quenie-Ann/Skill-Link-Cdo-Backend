"""
Skill-Link CDO — Development Seed Script
Creates: 3 test accounts + skill categories + sample data
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skilllink.settings')
django.setup()

from users.models import User
from workers.models import SkillCategory, WorkerProfile
from residents.models import ResidentProfile
from requests_api.models import JobRequest, JobOffer
from notifications_app.models import Notification

print("Seeding Skill-Link CDO database...")

#1. Skill Categories 
CATEGORIES = [
    ('Plumber',        'Water system installation, repair, and maintenance.'),
    ('Electrician',    'Electrical wiring, panel work, and appliance repair.'),
    ('Carpenter',      'Furniture, framing, roofing, and woodwork.'),
    ('Welder',         'Metal fabrication, gate work, and structural welding.'),
    ('Mason',          'Concrete, tile, brick, and stonework.'),
]
categories = {}
for name, desc in CATEGORIES:
    cat, _ = SkillCategory.objects.get_or_create(category_name=name, defaults={'description': desc})
    categories[name] = cat
    print(f" Category: {name}")

#2. Admin User
admin_user, created = User.objects.get_or_create(
    email='admin@skilllink.com',
    defaults={'role': 'admin', 'status': 'active', 'is_staff': True, 'is_superuser': True}
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(" Admin: admin@skilllink.com / admin123")
else:
    print("  · Admin already exists")

#3. Worker Users
WORKERS = [
    ('worker@skilllink.com',  'worker123',  'Juan dela Cruz',   'Zone 3, Bulua, CDO',   categories['Plumber'],     650.00, 5),
    ('worker2@skilllink.com', 'worker123',  'Maria Santos',     'Zone 7, Bulua, CDO',    categories['Electrician'], 750.00, 8),
    ('worker3@skilllink.com', 'worker123',  'Pedro Reyes',      'Zone 1, Bulua, CDO', categories['Carpenter'],   600.00, 3),
]
for email, pw, name, addr, cat, rate, yrs in WORKERS:
    u, created = User.objects.get_or_create(email=email, defaults={'role': 'worker', 'status': 'active'})
    if created:
        u.set_password(pw)
        u.save()
    wp, _ = WorkerProfile.objects.get_or_create(user=u, defaults={
        'full_name': name, 'address': addr, 'skill_category': cat,
        'declared_rate': rate, 'years_experience': yrs,
        'contact_number': '09170000000', 'bio': f'Experienced {cat.category_name} in CDO.',
        'verification_status': 'verified', 'avg_rating': 4.50,
        'availability_schedule': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    })
    print(f" Worker: {email} / {pw}  ({cat.category_name})")

#4. Resident Users
RESIDENTS = [
    ('resident@skilllink.com',  'resident123', 'Ana Gomez',  'Zone 5, Bulua, CDO',   '09180000001'),
    ('resident2@skilllink.com', 'resident123', 'Carlo Tan',  'Zone 2, Bulua, CDO',    '09180000002'),
]
resident_profiles = []
for email, pw, name, addr, phone in RESIDENTS:
    u, created = User.objects.get_or_create(email=email, defaults={'role': 'resident', 'status': 'active'})
    if created:
        u.set_password(pw)
        u.save()
    rp, _ = ResidentProfile.objects.get_or_create(user=u, defaults={
        'full_name': name, 'address': addr, 'contact_number': phone,
        'verification_status': 'verified',
    })
    resident_profiles.append(rp)
    print(f" Resident: {email} / {pw}")

#5. Sample Job Requests
if JobRequest.objects.count() == 0:
    jr1 = JobRequest.objects.create(
        resident=resident_profiles[0],
        category=categories['Plumber'],
        title='Leaking Pipe Repair',
        description='Kitchen sink pipe is leaking badly. Need urgent repair.',
        location_address='Zone 5, Bulua, CDO',
        budget_min=300, budget_max=800,
        status='pending_match',
    )
    jr2 = JobRequest.objects.create(
        resident=resident_profiles[1],
        category=categories['Electrician'],
        title='Panel Box Rewiring',
        description='Old electrical panel needs complete rewiring for safety.',
        location_address='Zone 2, Bulua, CDO',
        budget_min=1000, budget_max=2500,
        status='offer_accepted',
    )
    print(f" Job Requests: {JobRequest.objects.count()} created")

    # Create a job offer for jr2
    worker2 = WorkerProfile.objects.get(user__email='worker2@skilllink.com')
    jo = JobOffer.objects.create(request=jr2, worker=worker2, status='accepted', match_score=92.5)
    print(f" Job Offer created (accepted) for Panel Box Rewiring")

#6. Sample Notifications
if Notification.objects.count() == 0:
    worker_user = User.objects.get(email='worker@skilllink.com')
    resident_user = User.objects.get(email='resident@skilllink.com')
    Notification.objects.bulk_create([
        Notification(user=worker_user, type='match', title='New Job Match!',
                     message='You have been matched for: Leaking Pipe Repair'),
        Notification(user=resident_user, type='offer', title='Request Submitted',
                     message='Your job request has been submitted and is being matched.'),
    ])
    print(f" Notifications seeded")

print("\nSeed complete! Test credentials:")
print("   Admin    → admin@skilllink.com    / admin123")
print("   Worker   → worker@skilllink.com   / worker123")
print("   Worker   → worker2@skilllink.com  / worker123")
print("   Resident → resident@skilllink.com / resident123")

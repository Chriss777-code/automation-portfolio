# STR Guest Messaging Automation 🏠

**Automate guest communication for short-term rentals (Airbnb, VRBO)**

Send personalized messages at key moments during the guest journey.

## Features

- 📝 Template-based messaging with variables
- 🗓️ Scheduled sends based on booking timeline
- 🏡 Multi-property support
- 📱 Platform-agnostic (Airbnb, VRBO, direct booking)
- 🔄 Full guest journey automation

## Guest Journey Stages

| Stage | When | Default Message |
|-------|------|-----------------|
| `BOOKING_CONFIRMED` | Immediately | Thank you + dates |
| `PRE_ARRIVAL` | 2 days before | Check-in instructions |
| `CHECK_IN_DAY` | Check-in day noon | Reminder + encouragement |
| `DURING_STAY` | First full day evening | Mid-stay check-in |
| `CHECK_OUT_DAY` | Check-out morning | Reminder + instructions |
| `POST_STAY` | 1 day after | Review request |

## Quick Start

```python
from guest_messenger import GuestMessenger, Guest, Property, create_default_messenger

# Create messenger with default templates
messenger = create_default_messenger()

# Add your property
messenger.add_property(Property(
    name="Beach House",
    address="123 Ocean Dr, Malibu, CA",
    wifi_name="BeachHouse_5G",
    wifi_password="SunAndSand!",
    door_code="1234",
    check_in_time="4:00 PM",
    check_out_time="11:00 AM",
    parking_info="Driveway parking available",
    house_rules="No smoking, no parties",
    emergency_contact="Host: (555) 123-4567"
))

# Create a guest
guest = Guest(
    name="John Smith",
    check_in="2026-02-15",
    check_out="2026-02-18",
    num_guests=4
)

# Get all scheduled messages
messages = messenger.get_scheduled_messages(guest, "Beach House")
for msg in messages:
    print(f"{msg['send_at']}: {msg['template_name']}")
```

## Template Variables

| Variable | Description |
|----------|-------------|
| `{guest_name}` | Full name |
| `{guest_first_name}` | First name only |
| `{num_guests}` | Number of guests |
| `{check_in_date}` | "February 15, 2026" |
| `{check_out_date}` | "February 18, 2026" |
| `{check_in_day}` | "Saturday" |
| `{property_name}` | Property name |
| `{address}` | Full address |
| `{wifi_name}` | WiFi network |
| `{wifi_password}` | WiFi password |
| `{door_code}` | Entry code |
| `{check_in_time}` | "4:00 PM" |
| `{check_out_time}` | "11:00 AM" |
| `{parking_info}` | Parking details |
| `{house_rules}` | Rules text |
| `{local_tips}` | Local recommendations |
| `{emergency_contact}` | Contact info |

## Custom Templates

```python
from guest_messenger import MessageTemplate, BookingStage

# Add a custom template
messenger.add_template(MessageTemplate(
    name="Weather Alert",
    stage=BookingStage.PRE_ARRIVAL,
    subject="Weather update for your stay",
    body="Hi {guest_first_name}! Expect snow this weekend...",
    send_offset_hours=-24  # 1 day before check-in
))
```

## Export/Import Templates

```python
# Export to JSON
messenger.export_templates("my_templates.json")

# Load from JSON
messenger.add_templates_from_file("my_templates.json")
```

## Integration Ideas

- **Cron job**: Schedule message sends
- **Airbnb API**: Auto-fetch bookings
- **Twilio**: Send as SMS
- **Email service**: Send as email
- **OpenClaw**: Automated message delivery

## Default Templates Included

1. **Booking Confirmation** - Thanks + dates
2. **Pre-Arrival Instructions** - Full check-in details
3. **Check-in Day Reminder** - Door code + arrival
4. **Mid-Stay Check** - Everything okay?
5. **Check-out Reminder** - Departure instructions
6. **Review Request** - Ask for feedback

## Requirements

```
# No external dependencies - pure Python
```

## Author

Built by Neo for Crystal's STR business (Mammoth Lakes + Maui).

## License

MIT

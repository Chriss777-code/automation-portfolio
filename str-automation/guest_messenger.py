#!/usr/bin/env python3
"""
STR Guest Messaging Automation

Automate guest communication for short-term rentals (Airbnb, VRBO).
Sends personalized messages at key moments during the guest journey.

Features:
- Template-based messaging
- Variable substitution
- Scheduled sends
- Multi-platform support (Airbnb, VRBO)
- Booking stage detection

Author: Neo (AI Assistant)
Date: 2026-02-11
For: Crystal's STR business
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class BookingStage(Enum):
    """Stages of a guest's booking journey."""
    INQUIRY = "inquiry"
    BOOKING_CONFIRMED = "booking_confirmed"
    PRE_ARRIVAL = "pre_arrival"
    CHECK_IN_DAY = "check_in_day"
    DURING_STAY = "during_stay"
    CHECK_OUT_DAY = "check_out_day"
    POST_STAY = "post_stay"


@dataclass
class Guest:
    """Guest information."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    num_guests: int = 1
    check_in: Optional[str] = None  # ISO date
    check_out: Optional[str] = None
    platform: str = "airbnb"  # airbnb, vrbo
    booking_id: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Property:
    """Property information."""
    name: str
    address: str
    wifi_name: Optional[str] = None
    wifi_password: Optional[str] = None
    door_code: Optional[str] = None
    check_in_time: str = "4:00 PM"
    check_out_time: str = "11:00 AM"
    parking_info: Optional[str] = None
    house_rules: Optional[str] = None
    local_tips: Optional[str] = None
    emergency_contact: Optional[str] = None


@dataclass
class MessageTemplate:
    """A message template with variables."""
    name: str
    stage: BookingStage
    subject: Optional[str]  # For email
    body: str
    send_offset_hours: int = 0  # Hours before/after stage trigger


class GuestMessenger:
    """
    Automate guest communication for STR properties.
    
    Usage:
        messenger = GuestMessenger()
        messenger.add_property(Property(name="Mammoth Condo", ...))
        messenger.add_templates_from_file("templates.json")
        
        message = messenger.generate_message(
            guest=Guest(name="John", check_in="2026-02-15"),
            property_name="Mammoth Condo",
            stage=BookingStage.PRE_ARRIVAL
        )
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        self.properties: Dict[str, Property] = {}
        self.templates: Dict[str, List[MessageTemplate]] = {}
        self.templates_dir = Path(templates_dir) if templates_dir else None
        
    def add_property(self, property: Property):
        """Add a property to manage."""
        self.properties[property.name] = property
        
    def add_template(self, template: MessageTemplate):
        """Add a message template."""
        stage_key = template.stage.value
        if stage_key not in self.templates:
            self.templates[stage_key] = []
        self.templates[stage_key].append(template)
        
    def add_templates_from_file(self, filepath: str):
        """Load templates from JSON file."""
        with open(filepath) as f:
            data = json.load(f)
            for t in data.get("templates", []):
                self.add_template(MessageTemplate(
                    name=t["name"],
                    stage=BookingStage(t["stage"]),
                    subject=t.get("subject"),
                    body=t["body"],
                    send_offset_hours=t.get("send_offset_hours", 0)
                ))
                
    def generate_message(
        self,
        guest: Guest,
        property_name: str,
        stage: BookingStage,
        template_name: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a personalized message for a guest.
        
        Returns:
            Dict with 'subject' and 'body' keys
        """
        if property_name not in self.properties:
            raise ValueError(f"Property not found: {property_name}")
            
        property = self.properties[property_name]
        stage_templates = self.templates.get(stage.value, [])
        
        if not stage_templates:
            raise ValueError(f"No templates for stage: {stage.value}")
            
        # Select template
        if template_name:
            template = next((t for t in stage_templates if t.name == template_name), None)
            if not template:
                raise ValueError(f"Template not found: {template_name}")
        else:
            template = stage_templates[0]
            
        # Build variables
        variables = self._build_variables(guest, property)
        
        # Substitute variables
        subject = self._substitute(template.subject, variables) if template.subject else None
        body = self._substitute(template.body, variables)
        
        return {
            "subject": subject,
            "body": body,
            "template_name": template.name,
            "stage": stage.value,
            "generated_at": datetime.now().isoformat()
        }
        
    def _build_variables(self, guest: Guest, property: Property) -> Dict[str, str]:
        """Build variable substitution map."""
        # Parse dates
        check_in_date = None
        check_out_date = None
        if guest.check_in:
            check_in_date = datetime.fromisoformat(guest.check_in)
        if guest.check_out:
            check_out_date = datetime.fromisoformat(guest.check_out)
            
        variables = {
            # Guest info
            "{guest_name}": guest.name,
            "{guest_first_name}": guest.name.split()[0] if guest.name else "",
            "{num_guests}": str(guest.num_guests),
            "{check_in_date}": check_in_date.strftime("%B %d, %Y") if check_in_date else "",
            "{check_out_date}": check_out_date.strftime("%B %d, %Y") if check_out_date else "",
            "{check_in_day}": check_in_date.strftime("%A") if check_in_date else "",
            
            # Property info
            "{property_name}": property.name,
            "{address}": property.address,
            "{wifi_name}": property.wifi_name or "",
            "{wifi_password}": property.wifi_password or "",
            "{door_code}": property.door_code or "",
            "{check_in_time}": property.check_in_time,
            "{check_out_time}": property.check_out_time,
            "{parking_info}": property.parking_info or "",
            "{house_rules}": property.house_rules or "",
            "{local_tips}": property.local_tips or "",
            "{emergency_contact}": property.emergency_contact or "",
        }
        
        return variables
        
    def _substitute(self, text: str, variables: Dict[str, str]) -> str:
        """Replace variables in text."""
        result = text
        for var, value in variables.items():
            result = result.replace(var, value)
        return result
        
    def get_scheduled_messages(
        self,
        guest: Guest,
        property_name: str
    ) -> List[Dict]:
        """
        Get all scheduled messages for a guest's stay.
        
        Returns list of messages with scheduled send times.
        """
        if not guest.check_in:
            raise ValueError("Guest check_in date required")
            
        messages = []
        check_in = datetime.fromisoformat(guest.check_in)
        check_out = datetime.fromisoformat(guest.check_out) if guest.check_out else None
        
        stage_times = {
            BookingStage.BOOKING_CONFIRMED: datetime.now(),
            BookingStage.PRE_ARRIVAL: check_in - timedelta(days=2),
            BookingStage.CHECK_IN_DAY: check_in,
            BookingStage.DURING_STAY: check_in + timedelta(days=1),
            BookingStage.CHECK_OUT_DAY: check_out if check_out else check_in + timedelta(days=3),
            BookingStage.POST_STAY: (check_out if check_out else check_in + timedelta(days=3)) + timedelta(days=1),
        }
        
        for stage, base_time in stage_times.items():
            stage_templates = self.templates.get(stage.value, [])
            for template in stage_templates:
                send_time = base_time + timedelta(hours=template.send_offset_hours)
                
                try:
                    message = self.generate_message(guest, property_name, stage, template.name)
                    message["send_at"] = send_time.isoformat()
                    message["stage"] = stage.value
                    messages.append(message)
                except:
                    pass
                    
        # Sort by send time
        messages.sort(key=lambda m: m.get("send_at", ""))
        return messages
        
    def export_templates(self, filepath: str):
        """Export all templates to JSON."""
        templates = []
        for stage_templates in self.templates.values():
            for t in stage_templates:
                templates.append({
                    "name": t.name,
                    "stage": t.stage.value,
                    "subject": t.subject,
                    "body": t.body,
                    "send_offset_hours": t.send_offset_hours
                })
                
        with open(filepath, 'w') as f:
            json.dump({"templates": templates}, f, indent=2)


# Default templates
DEFAULT_TEMPLATES = [
    MessageTemplate(
        name="Booking Confirmation",
        stage=BookingStage.BOOKING_CONFIRMED,
        subject="Your reservation at {property_name} is confirmed!",
        body="""Hi {guest_first_name}! 👋

Thank you for booking {property_name}! We're excited to host you.

📅 Check-in: {check_in_date} at {check_in_time}
📅 Check-out: {check_out_date} at {check_out_time}

I'll send you detailed check-in instructions a couple days before your arrival.

If you have any questions before then, don't hesitate to reach out!

Best,
Crystal"""
    ),
    MessageTemplate(
        name="Pre-Arrival Instructions",
        stage=BookingStage.PRE_ARRIVAL,
        subject="Check-in details for {property_name}",
        send_offset_hours=-48,  # 2 days before
        body="""Hi {guest_first_name}! 🏔️

Your stay at {property_name} is coming up! Here are your check-in details:

📍 **Address:** {address}

🔑 **Door Code:** {door_code}

📶 **WiFi:**
- Network: {wifi_name}
- Password: {wifi_password}

🚗 **Parking:** {parking_info}

⏰ **Check-in:** {check_in_time}
⏰ **Check-out:** {check_out_time}

📋 **House Rules:**
{house_rules}

Let me know when you arrive safely!

Crystal"""
    ),
    MessageTemplate(
        name="Check-in Day",
        stage=BookingStage.CHECK_IN_DAY,
        subject=None,
        send_offset_hours=12,  # Noon on check-in day
        body="""Hi {guest_first_name}! 

Happy check-in day! 🎉 The property is all ready for you.

As a reminder, check-in starts at {check_in_time}. The door code is {door_code}.

Safe travels, and let me know when you've settled in!

Crystal"""
    ),
    MessageTemplate(
        name="Mid-Stay Check",
        stage=BookingStage.DURING_STAY,
        subject=None,
        send_offset_hours=18,  # Evening of first full day
        body="""Hi {guest_first_name}!

Just checking in to make sure everything is going well with your stay! 

Is there anything you need? I'm happy to help with local recommendations too.

Enjoy! 🏔️
Crystal"""
    ),
    MessageTemplate(
        name="Check-out Reminder",
        stage=BookingStage.CHECK_OUT_DAY,
        subject="Check-out reminder for {property_name}",
        send_offset_hours=8,  # Morning of check-out
        body="""Good morning {guest_first_name}! ☀️

Just a friendly reminder that check-out is at {check_out_time} today.

Before you go:
- Please leave all used towels in the bathtub
- Run the dishwasher if you used dishes
- Make sure all windows and doors are locked
- Leave the key/fob on the kitchen counter

Thank you so much for staying with us! We hope you had an amazing time.

Safe travels home! 🚗

Crystal"""
    ),
    MessageTemplate(
        name="Review Request",
        stage=BookingStage.POST_STAY,
        subject="Thank you for staying at {property_name}!",
        send_offset_hours=24,  # Day after checkout
        body="""Hi {guest_first_name}!

Thank you so much for being such great guests! We hope you had a wonderful time at {property_name}.

If you have a moment, we'd really appreciate it if you could leave us a review. Your feedback helps future guests and helps us improve! ⭐

We'd love to host you again anytime!

Warmly,
Crystal"""
    ),
]


def create_default_messenger() -> GuestMessenger:
    """Create a messenger with default templates."""
    messenger = GuestMessenger()
    for template in DEFAULT_TEMPLATES:
        messenger.add_template(template)
    return messenger


def demo():
    """Demo the guest messenger."""
    print("=== STR Guest Messenger Demo ===\n")
    
    # Create messenger with defaults
    messenger = create_default_messenger()
    
    # Add a property
    messenger.add_property(Property(
        name="Mammoth Lakes Condo",
        address="123 Mountain View Dr, Mammoth Lakes, CA 93546",
        wifi_name="MammothCondo_5G",
        wifi_password="SkiSnow2026!",
        door_code="1234",
        check_in_time="4:00 PM",
        check_out_time="11:00 AM",
        parking_info="1 assigned spot in underground garage, space #42",
        house_rules="No smoking, no parties, quiet hours 10pm-8am",
        local_tips="Best coffee: Black Velvet. Best tacos: Gomez's.",
        emergency_contact="Crystal: (555) 123-4567"
    ))
    
    # Create a guest
    guest = Guest(
        name="John Smith",
        num_guests=4,
        check_in="2026-02-15",
        check_out="2026-02-18",
        platform="airbnb"
    )
    
    # Generate messages
    print("Scheduled messages for John Smith's stay:\n")
    
    messages = messenger.get_scheduled_messages(guest, "Mammoth Lakes Condo")
    for msg in messages:
        print(f"📅 {msg['send_at'][:10]} | {msg['stage']}")
        print(f"   Template: {msg['template_name']}")
        if msg['subject']:
            print(f"   Subject: {msg['subject']}")
        print(f"   Preview: {msg['body'][:100]}...")
        print()


if __name__ == "__main__":
    demo()

import re
from django.core.exceptions import ValidationError

def validate_vehicle_number(value):
    """
    Validate vehicle registration number format: XX88 XY8888
    """
    pattern = r'^[A-Z]{2}\d{2} [A-Z]{2}\d{4}$'  # Correct format with space

    if not re.match(pattern, value):
        raise ValidationError("Invalid vehicle number format. It should be in the format XX88 XY8888 (e.g., KL60 AB1234).")

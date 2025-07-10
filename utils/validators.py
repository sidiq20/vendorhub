def validate_checkout_form(form):
    required_fields = ["name", "email", "phone", "address", "city", "state", "zip_code"]
    missing = [field for field in required_fields if not form.get(field)]
    return missing
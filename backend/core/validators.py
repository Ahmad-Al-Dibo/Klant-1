from django.utils.translation import gettext_lazy as _  # Dit is de belangrijke import!

from django.core.validators import ValidationError
import re
from datetime import date, datetime
import os


class DutchPostalCodeValidator:
    """
    Validator voor Nederlandse postcodes (bijv. 1234AB of 1234 AB)
    """
    def __init__(self, allow_space=True):
        self.allow_space = allow_space
    
    def __call__(self, value):
        if not value:
            return
        
        # Remove spaces
        value = value.replace(' ', '').upper()
        
        # Check length
        if len(value) != 6:
            raise ValidationError('Nederlandse postcode moet 6 tekens zijn (bijv. 1234AB)')
        
        # Check format: 4 digits + 2 letters
        if not value[:4].isdigit():
            raise ValidationError('Eerste 4 tekens moeten cijfers zijn')
        
        if not value[4:].isalpha():
            raise ValidationError('Laatste 2 tekens moeten letters zijn')
        
        # Check valid letters (not all letters are valid in Dutch postal codes)
        invalid_combinations = ['SA', 'SD', 'SS']
        if value[4:] in invalid_combinations:
            raise ValidationError(f'Postcode combinatie {value[4:]} is niet toegestaan')


class PhoneNumberValidator:
    """
    Validator voor telefoonnummers (Nederlands en internationaal)
    """
    def __call__(self, value):
        if not value:
            return
        
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)\+]', '', value) # verwijder spaties, streepjes, haakjes en plustekens. returnt een string met alleen cijfers
        
        # Check if it contains only digits (and optional leading +)
        if not re.match(r'^\+?[0-9]+$', cleaned):
            raise ValidationError('Ongeldig telefoonnummer formaat')
        
        # Check minimum length
        if len(cleaned) < 10:
            raise ValidationError('Telefoonnummer is te kort')
        
        # Check maximum length
        if len(cleaned) > 15:
            raise ValidationError('Telefoonnummer is te lang')


class VATNumberValidator:
    """
    Validator voor BTW-nummers (Nederlands en Europees)
    """
    def __init__(self, country_code='NL'):
        self.country_code = country_code.upper()
    
    def __call__(self, value):
        if not value:
            return
        
        value = value.upper().replace(' ', '')
        
        # Check if starts with country code
        if not value.startswith(self.country_code):
            raise ValidationError(f'BTW-nummer moet beginnen met {self.country_code}')
        
        # Remove country code for validation
        number = value[2:]
        
        # Dutch VAT number validation (NL123456789B01)
        if self.country_code == 'NL':
            if not re.match(r'^[0-9]{9}B[0-9]{2}$', number):
                raise ValidationError('Ongeldig Nederlands BTW-nummer formaat (bijv. NL123456789B01)')
            
            # Modulus 97 check for Dutch VAT
            try:
                digits = number[:-3]  # Remove 'B01'
                if int(digits) % 97 != int(number[-2:]):
                    raise ValidationError('Ongeldig Nederlands BTW-nummer')
            except ValueError:
                raise ValidationError('Ongeldig Nederlands BTW-nummer')


class BankAccountValidator:
    """
    Validator voor IBAN bankrekeningnummers
    """
    def __call__(self, value):
        if not value:
            return
        
        value = value.upper().replace(' ', '')
        
        # Basic format check
        if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$', value):
            raise ValidationError('Ongeldig IBAN formaat')
        
        # Move first 4 characters to end
        rearranged = value[4:] + value[:4]
        
        # Convert letters to numbers (A=10, B=11, ... Z=35)
        converted = ''
        for char in rearranged:
            if char.isdigit():
                converted += char
            else:
                converted += str(ord(char) - 55)
        
        # Check modulo 97
        if int(converted) % 97 != 1:
            raise ValidationError('Ongeldig IBAN nummer')


class PasswordStrengthValidator:
    """
    Validator voor wachtwoordsterkte
    """
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True,
                 require_digits=True, require_special=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
    
    def __call__(self, value):
        errors = []
        
        # Check minimum length
        if len(value) < self.min_length:
            errors.append(f'Wachtwoord moet minimaal {self.min_length} tekens lang zijn')
        
        # Check uppercase
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            errors.append('Wachtwoord moet minimaal 1 hoofdletter bevatten')
        
        # Check lowercase
        if self.require_lowercase and not re.search(r'[a-z]', value):
            errors.append('Wachtwoord moet minimaal 1 kleine letter bevatten')
        
        # Check digits
        if self.require_digits and not re.search(r'[0-9]', value):
            errors.append('Wachtwoord moet minimaal 1 cijfer bevatten')
        
        # Check special characters
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append('Wachtwoord moet minimaal 1 speciaal teken bevatten')
        
        # Check for common patterns
        common_passwords = ['password', '123456', 'qwerty', 'wachtwoord', 'admin']
        if value.lower() in common_passwords:
            errors.append('Dit wachtwoord is te veel gebruikt, kies een ander wachtwoord')
        
        # Check for username/email in password
        # This should be passed from the form/context
        # if username and username.lower() in value.lower():
        #     errors.append('Wachtwoord mag je gebruikersnaam niet bevatten')
        
        if errors:
            raise ValidationError(errors)


class FileSizeValidator:
    """
    Validator voor bestandsgrootte
    """
    def __init__(self, max_size_mb):
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def __call__(self, value):
        if value and hasattr(value, 'size'):
            if value.size > self.max_size_bytes:
                raise ValidationError(
                    f'Bestand is te groot. Maximale grootte: {self.max_size_bytes / (1024*1024):.1f} MB'
                )


class FileExtensionValidator:
    """
    Validator voor bestandsextensies
    """
    def __init__(self, allowed_extensions):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
    
    def __call__(self, value):
        if value:
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in self.allowed_extensions:
                raise ValidationError(
                    f'Ongeldig bestandstype. Toegestane types: {", ".join(self.allowed_extensions)}'
                )


class ImageDimensionValidator:
    """
    Validator voor afbeeldingsafmetingen
    """
    def __init__(self, min_width=None, max_width=None, min_height=None, max_height=None):
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height
    
    def __call__(self, value):
        if value and hasattr(value, 'image'):
            from PIL import Image
            try:
                img = Image.open(value)
                width, height = img.size
                
                errors = []
                if self.min_width and width < self.min_width:
                    errors.append(f'Minimale breedte: {self.min_width}px')
                if self.max_width and width > self.max_width:
                    errors.append(f'Maximale breedte: {self.max_width}px')
                if self.min_height and height < self.min_height:
                    errors.append(f'Minimale hoogte: {self.min_height}px')
                if self.max_height and height > self.max_height:
                    errors.append(f'Maximale hoogte: {self.max_height}px')
                
                if errors:
                    raise ValidationError(errors)
            except Exception:
                # If we can't open the image, skip dimension validation
                pass


class DateRangeValidator:
    """
    Validator voor datumbereiken
    """
    def __init__(self, min_date=None, max_date=None):
        self.min_date = min_date
        self.max_date = max_date
    
    def __call__(self, value):
        if not value:
            return
        
        if self.min_date and value < self.min_date:
            raise ValidationError(f'Datum mag niet voor {self.min_date} zijn')
        
        if self.max_date and value > self.max_date:
            raise ValidationError(f'Datum mag niet na {self.max_date} zijn')


class PercentageValidator:
    """
    Validator voor percentages (0-100)
    """
    def __call__(self, value):
        if value is not None:
            if value < 0:
                raise ValidationError('Percentage mag niet negatief zijn')
            if value > 100:
                raise ValidationError('Percentage mag niet groter zijn dan 100%')


class URLDomainValidator:
    """
    Validator voor URL domeinen
    """
    def __init__(self, allowed_domains=None, blocked_domains=None):
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []
    
    def __call__(self, value):
        from urllib.parse import urlparse
        
        if not value:
            return
        
        try:
            parsed = urlparse(value)
            domain = parsed.netloc
            
            # Check blocked domains
            for blocked in self.blocked_domains:
                if blocked in domain:
                    raise ValidationError(f'Domein {blocked} is niet toegestaan')
            
            # Check allowed domains (if specified)
            if self.allowed_domains:
                allowed = False
                for allowed_domain in self.allowed_domains:
                    if allowed_domain in domain:
                        allowed = True
                        break
                if not allowed:
                    raise ValidationError(f'Alleen domeinen van {", ".join(self.allowed_domains)} zijn toegestaan')
        
        except Exception:
            raise ValidationError('Ongeldige URL')


class NoProfanityValidator:
    """
    Validator om scheldwoorden te voorkomen
    """
    def __init__(self, profanity_list=None):
        self.profanity_list = profanity_list or [
            'scheldwoord1', 'scheldwoord2', 'badword'
        ]
    
    def __call__(self, value):
        if not value:
            return
        
        value_lower = value.lower()
        for word in self.profanity_list:
            if word in value_lower:
                raise ValidationError('Bericht bevat ongepaste inhoud')


class UniqueTogetherValidator:
    """
    Validator voor unieke combinaties van velden
    """
    def __init__(self, queryset, fields, message=None):
        self.queryset = queryset
        self.fields = fields
        self.message = message or 'Deze combinatie bestaat al'
    
    def __call__(self, value, model_instance=None):
        # This validator should be used in model clean() method
        pass


class BSNValidator:
    """
    Validator voor Nederlandse Burgerservicenummer (BSN)
    """
    def __call__(self, value):
        if not value:
            return
        
        # Remove non-digits
        bsn = re.sub(r'\D', '', str(value))
        
        # Check length
        if len(bsn) != 9:
            raise ValidationError('BSN moet 9 cijfers zijn')
        
        # Eleven-test validation
        total = 0
        for i, digit in enumerate(bsn[:-1], start=1):
            total += int(digit) * (9 - i + 1)
        total -= int(bsn[-1])
        
        if total % 11 != 0:
            raise ValidationError('Ongeldig BSN nummer')


from django.utils.deconstruct import deconstructible


@deconstructible
class MinValueValidator:
    """
    Aangepaste MaxValueValidator met betere error messages
    """
    message = _('Zorg dat deze waarde kleiner of gelijk is aan %(limit_value)s.') 
    code = 'max_value'
    
    def __init__(self, limit_value, message=None):
        self.limit_value = limit_value
        if message:
            self.message = message
    
    def __call__(self, value):
        if value is not None and value > self.limit_value:
            raise ValidationError(
                self.message,
                code=self.code,
                params={'limit_value': self.limit_value}
            )
    
    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.limit_value == other.limit_value and
            self.message == other.message and
            self.code == other.code
        )



@deconstructible
class MaxValueValidator:
    """
    Aangepaste MaxValueValidator met betere error messages
    """
    message = _('Zorg dat deze waarde kleiner of gelijk is aan %(limit_value)s.')
    code = 'max_value'
    
    def __init__(self, limit_value, message=None):
        self.limit_value = limit_value
        if message:
            self.message = message
    
    def __call__(self, value):
        if value is not None and value > self.limit_value:
            raise ValidationError(
                self.message,
                code=self.code,
                params={'limit_value': self.limit_value}
            )
    
    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.limit_value == other.limit_value and
            self.message == other.message and
            self.code == other.code
        )


@deconstructible
class RangeValidator:
    """
    Combinatie validator voor min en max waarden
    """
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
    
    def __call__(self, value):
        if value is not None:
            if self.min_value is not None and value < self.min_value:
                raise ValidationError(
                    f'Waarde moet minimaal {self.min_value} zijn',
                    code='min_value'
                )
            if self.max_value is not None and value > self.max_value:
                raise ValidationError(
                    f'Waarde mag maximaal {self.max_value} zijn',
                    code='max_value'
                )
    
    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.min_value == other.min_value and
            self.max_value == other.max_value
        )


@deconstructible
class PositiveNumberValidator:
    """
    Validator voor positieve getallen
    """
    def __init__(self, message=None):
        self.message = message or _('Waarde moet positief zijn (groter dan 0).')
        self.code = 'positive_required'
    
    def __call__(self, value):
        if value is not None and value <= 0:
            raise ValidationError(self.message, code=self.code)


@deconstructible
class NonNegativeNumberValidator:
    """
    Validator voor niet-negatieve getallen (0 of groter)
    """
    def __init__(self, message=None):
        self.message = message or _('Waarde mag niet negatief zijn.')
        self.code = 'non_negative_required'
    
    def __call__(self, value):
        if value is not None and value < 0:
            raise ValidationError(self.message, code=self.code)
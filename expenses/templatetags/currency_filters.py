from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    try:
        value = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value

    formatted = f"{value:,.2f}"
    formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    return formatted
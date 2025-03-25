from django import template

register = template.Library()

# Create a custom filter 'to' to generate a list from a float for the stars
@register.filter(name='to')
def to(value):
    # Ensure value is float, else return empty list
    try:
        return range(1, int(value) + 1)
    except TypeError:
        return []

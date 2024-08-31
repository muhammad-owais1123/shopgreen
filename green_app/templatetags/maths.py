from django import template

register = template.Library()

@register.simple_tag
def multiply(value, arg):
    return value * arg

@register.simple_tag
def divide(value, arg):
    if arg == 0:
        return "Cannot divide by zero"
    return value / arg

#@register.simple_tag
#def add(value, arg):
#    return value + arg

@register.simple_tag
def add(value, arg):
    try:
        # Convert both values to integers
        return int(value) + int(arg)
    except (ValueError, TypeError):
#        # Fallback to string concatenation if conversion fails
        return str(value) + str(arg)
@register.simple_tag
def subtract(value, arg):
    return value - arg


@register.simple_tag
def discount(value, arg):
    return value % arg

@register.simple_tag(takes_context=True)
def accumulate(context, value):
    """Accumulate a total in the context."""
    if 'total_price' not in context:
        context['total_price'] = 0
    context['total_price'] += value
    return context['total_price']
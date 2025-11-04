from django import template

register = template.Library()

@register.filter
def latex_escape(value):
    """Escape special LaTeX characters"""
    if value is None:
        return ''
    
    value = str(value)
    
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    
    for old, new in replacements.items():
        value = value.replace(old, new)
    
    return value

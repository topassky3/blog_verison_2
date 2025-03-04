from django import template

register = template.Library()

@register.inclusion_tag('tutoriales/tutorial_grid.html')
def render_tutorials(tutorials):
    """
    Renderiza la grilla de tutoriales.
    Se espera que 'tutorials' sea un queryset de tutoriales.
    """
    return {'tutorials': tutorials}

# leer_tutoriales/templatetags/comments_tags.py
from django import template

register = template.Library()

@register.inclusion_tag('leer_tutoriales/comentario.html', takes_context=True)
def render_comentario(context, comentario):
    """
    Renderiza un comentario y sus respuestas de forma recursiva.
    """
    return {
        'comentario': comentario,
        'request': context['request'],
    }

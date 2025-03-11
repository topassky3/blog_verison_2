# leer_guias/templatetags/guia_comments_tags.py
from django import template

register = template.Library()

@register.inclusion_tag('leer_guias/_guia_comment.html', takes_context=True)
def render_guia_comentario(context, comentario):
    """
    Renderiza un comentario (GuiaComment) y sus respuestas recursivamente.
    """
    return {
        'comentario': comentario,
        'request': context['request']
    }

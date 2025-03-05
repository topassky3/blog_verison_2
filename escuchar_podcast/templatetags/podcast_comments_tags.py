from django import template

register = template.Library()

@register.inclusion_tag('escuchar_podcast/comentario.html', takes_context=True)
def render_podcast_comentario(context, comentario):
    """
    Renderiza un comentario de podcast (incluyendo respuestas) usando el template correcto.
    """
    return {
        'comentario': comentario,
        'request': context['request'],
    }


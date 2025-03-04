from django import template

register = template.Library()

@register.inclusion_tag('podcast/podcast_grid.html')
def render_podcasts(podcasts):
    return {'podcasts': podcasts}

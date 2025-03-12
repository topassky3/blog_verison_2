from django.views.generic import TemplateView
from django.db.models import Q
from core.models import Tutorial, Podcast, Guia
from .utils import tokenize, compute_probability_score  # Donde guardaste las funciones


class BusquedaView(TemplateView):
    template_name = 'buscador/buscador.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()

        if not query:
            context['tutorials'] = []
            context['podcasts'] = []
            context['guias'] = []  # Agregamos guías al contexto
            context['query'] = ''
            return context

        query_tokens = tokenize(query)

        # ---------------------------
        # Búsqueda de Tutorials
        # ---------------------------
        all_tutorials = Tutorial.objects.filter(publicado=True)
        all_texts = []
        for t in all_tutorials:
            texto_completo = t.title
            for block in t.blocks.all():
                texto_completo += " " + block.content
            all_texts.append(texto_completo)

        tokens_globales = []
        for text in all_texts:
            tokens_globales.extend(tokenize(text))
        vocab_size = len(set(tokens_globales))

        tutoriales_con_score = []
        for t in all_tutorials:
            texto_completo = t.title
            for block in t.blocks.all():
                texto_completo += " " + block.content
            doc_tokens = tokenize(texto_completo)
            score = compute_probability_score(doc_tokens, query_tokens, vocab_size)
            tutoriales_con_score.append((t, score))
        tutoriales_con_score.sort(key=lambda x: x[1], reverse=True)
        context['tutorials'] = [item[0] for item in tutoriales_con_score]

        # ---------------------------
        # Búsqueda de Podcasts
        # ---------------------------
        all_podcasts = Podcast.objects.all()
        podcasts_con_score = []
        for p in all_podcasts:
            texto = p.title + " " + p.description
            doc_tokens = tokenize(texto)
            score = compute_probability_score(doc_tokens, query_tokens, vocab_size)
            podcasts_con_score.append((p, score))
        podcasts_con_score.sort(key=lambda x: x[1], reverse=True)
        context['podcasts'] = [item[0] for item in podcasts_con_score]

        # ---------------------------
        # Búsqueda de Guías
        # ---------------------------
        all_guias = Guia.objects.filter(publicado=True)
        guias_con_score = []
        for g in all_guias:
            # Concatenamos campos relevantes; por ejemplo, título, descripción y bloques de contenido
            texto_completo = g.title
            if g.description:
                texto_completo += " " + g.description
            for block in g.blocks.all():
                texto_completo += " " + block.content
            doc_tokens = tokenize(texto_completo)
            score = compute_probability_score(doc_tokens, query_tokens, vocab_size)
            guias_con_score.append((g, score))
        guias_con_score.sort(key=lambda x: x[1], reverse=True)
        context['guias'] = [item[0] for item in guias_con_score]

        context['query'] = query
        return context

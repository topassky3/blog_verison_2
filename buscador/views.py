from django.views.generic import TemplateView
from django.db.models import Q
from core.models import Tutorial, Podcast
from .utils import tokenize, compute_probability_score  # Donde guardaste las funciones


class BusquedaView(TemplateView):
    template_name = 'buscador/buscador.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()

        # Si no hay query, no hacemos nada costoso
        if not query:
            context['tutorials'] = []
            context['podcasts'] = []
            context['query'] = ''
            return context

        # 1) Tokenizo la query
        query_tokens = tokenize(query)

        # 2) Tomo todos los tutoriales publicados (podrías filtrar por algo más)
        all_tutorials = Tutorial.objects.filter(publicado=True)

        # 3) Voy a calcular un 'score' para cada tutorial
        #    Para hacerlo, necesito el vocab_size (si usaras Laplace)
        #    Ej: primero recojo tokens de TODOS los tutoriales y calculo un set.
        #    Si la base es grande, puede ser costoso. Ajusta según tu proyecto.
        all_texts = []
        for t in all_tutorials:
            # Combino título + contenido de los blocks
            texto_completo = t.title
            # Por ejemplo, concatenar todo el contenido de blocks
            for block in t.blocks.all():
                texto_completo += " " + block.content
            all_texts.append(texto_completo)

        # Tokenizar todo
        tokens_globales = []
        for text in all_texts:
            tokens_globales.extend(tokenize(text))
        vocab_size = len(set(tokens_globales))  # Distintas palabras en todos los docs

        # Ahora sí, computo el score de cada tutorial
        tutoriales_con_score = []
        for t in all_tutorials:
            # Armo el texto completo
            texto_completo = t.title
            for block in t.blocks.all():
                texto_completo += " " + block.content

            doc_tokens = tokenize(texto_completo)
            score = compute_probability_score(doc_tokens, query_tokens, vocab_size)
            tutoriales_con_score.append((t, score))

        # 4) Ordeno descendentemente por score
        #    (los de mayor probabilidad primero)
        tutoriales_con_score.sort(key=lambda x: x[1], reverse=True)

        # 5) Para no complicarnos, devuelvo la lista de tutoriales en orden
        #    OJO: esto ya está "fuera" del QuerySet de Django. Pierdes paginación nativa, etc.
        #    Si quieres paginar, hazlo manualmente con Paginator recibiendo la lista final.
        context['tutorials'] = [item[0] for item in tutoriales_con_score]

        # 6) Repite un proceso similar para podcasts (o lo que sea)
        all_podcasts = Podcast.objects.all()
        # Podrías unir description + title u otras cosas
        # O filtrar con Q: all_podcasts = Podcast.objects.filter(Q(title__icontains=query)|...)

        podcasts_con_score = []
        for p in all_podcasts:
            texto = p.title + " " + p.description
            doc_tokens = tokenize(texto)
            score = compute_probability_score(doc_tokens, query_tokens, vocab_size)
            podcasts_con_score.append((p, score))

        podcasts_con_score.sort(key=lambda x: x[1], reverse=True)
        context['podcasts'] = [item[0] for item in podcasts_con_score]

        context['query'] = query

        return context

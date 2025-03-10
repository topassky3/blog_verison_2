import re
import math
from collections import Counter


def tokenize(text):
    """
    Convierte el texto a minúsculas, quita caracteres no deseados,
    y lo divide en palabras. Ajusta a tus necesidades.
    """
    text = text.lower()
    # Elimina todo excepto letras, números y espacios
    text = re.sub(r'[^a-z0-9áéíóúüñ\s]', '', text)
    # Divide en palabras
    tokens = text.split()
    return tokens


def compute_probability_score(doc_tokens, query_tokens, vocab_size=0):
    """
    Calcula la 'probabilidad' (score) de que doc_tokens responda a query_tokens
    asumiendo un modelo de lenguaje simple (unigram + Laplace smoothing).

    doc_tokens: lista de palabras tokenizadas del documento
    query_tokens: lista de palabras tokenizadas de la consulta
    vocab_size: tamaño total de vocabulario que se va a considerar
                (para la corrección de Laplace)
    """
    # Contamos las apariciones de cada token en el doc
    doc_counts = Counter(doc_tokens)
    doc_length = len(doc_tokens)

    # Si no hay tokens en el documento, evitamos división por 0
    if doc_length == 0:
        return 0.0

    # Score inicial
    log_score = 0.0
    # Laplace smoothing
    alpha = 1.0

    for token in query_tokens:
        # Frecuencia del token en el doc
        freq = doc_counts[token]
        # Probabilidad con Laplace
        # P(token | doc) = (freq + alpha) / (doc_length + alpha * vocab_size)
        prob = (freq + alpha) / (doc_length + alpha * vocab_size)
        log_score += math.log(prob)

    # Retornamos la exponencial de la suma de logs
    # (o directamente el log_score si prefieres rankear por log-prob)
    return math.exp(log_score)

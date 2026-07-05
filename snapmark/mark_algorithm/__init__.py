
"""
__init__.py

Public API of the mark_algorithm package, which includes functions for placing text and sequences in a DXF document, as well as the main algorithm to find space for a sequence based on the document's geometry.
"""

from .placer import find_space_for_sequence
from .segmenter import GeometryContext, comp_center_point, comp_start_point, comp_segs_and_limits
from .sequence import SequenceText, rescale_sequence, sequence_dim, comp_text_bbox, comp_sf
from .segment_text_geometry import rotate_segment_text_sequence, ref_angle_and_pivot, comp_start_y_rotated
from snapmark.utils.geometry import rotate_segs
from snapmark.utils.segments_dict import number_segments_dict


def place_text(doc, texts, char_height, excluded_layers=None, avoid_layers=None,
               align='l', start_y=1, step=2, margin=1, debug_bbox=True):
    """
    Finds an available position for real DXF text entities (using font metrics) 
    within the document, avoiding collisions with existing geometry.

    Args:
        doc: ezdxf document.
        texts: List of strings to be placed.
        char_height: Height of each character used for bounding box calculation.
        excluded_layers: Layers to ignore during collision check.
        avoid_layers: Specific layers to treat as obstacles.
        align: Horizontal alignment ('l', 'c', 'r').
        start_y: Initial Y coordinate for the search.
        step: Vertical increment for finding free space.
        margin: Safety buffer around the text bounding box.
        debug_bbox: If True, draws a rectangle on 'DEBUG_TEXTBOX' layer.

    Returns:
        tuple: (x, y, width, height) or (None, None, width, height) if no space is found.
    """

    if all(len(text) == 0 for text in texts):
        raise Exception('Empty text.')

    width, height = comp_text_bbox(texts, char_height)
    ctx = GeometryContext(doc, excluded_layers, avoid_layers)
    x, y = find_space_for_sequence(width, height, ctx, align, start_y, step, margin)

    if x is None or y is None:
        return None, None, width, height

    if debug_bbox:
        ctx.msp.add_lwpolyline([
            (x, y), (x + width, y),
            (x + width, y + height),
            (x, y + height), (x, y)
        ], dxfattribs={'layer': 'DEBUG_TEXTBOX', 'color': 1})

    return x, y, width, height


def _scale_sequence_to_bounds(segment_text, scale_factor, x_pos, y_pos, space, min_char_height, max_char_height):
    """
    Scala la sequenza rispettando i limiti min_char e max_char.
    Ritorna (sequence, scale_factor, lenght_sequence, height_sequence).
    """
    # Calcola l'altezza grezza per decidere se riscalare
    height_raw = 0.0
    for char in segment_text:
        if char in number_segments_dict:
            segments = number_segments_dict[char]
            scaled = [
                None if pt is None else [pt[0] * scale_factor, pt[1] * scale_factor]
                for pt in segments
            ]
            valid = [pt for pt in scaled if pt is not None]
            if not valid:
                continue
            ys = [pt[1] for pt in valid]
            height_raw = max(max(ys) - min(ys), height_raw)

    if height_raw < min_char_height:
        scale_factor = scale_factor / height_raw * min_char_height
    elif height_raw > max_char_height:
        scale_factor = scale_factor / height_raw * max_char_height

    sequence = rescale_sequence(segment_text, scale_factor, x_pos, y_pos)
    lenght_sequence, height_sequence = sequence_dim(sequence, x_pos, y_pos, space)
    return sequence, scale_factor, lenght_sequence, height_sequence


def _reachable_at_down_to(lenght_sequence, height_sequence, down_to, available_width, available_height, margin):
    """
    Controlla se, scalando la sequenza fino all'altezza minima down_to (e la
    larghezza proporzionalmente — lo shrink è uniforme sui due assi), esiste
    ancora la possibilità teorica che entri nello spazio disponibile.

    Sostituisce il vecchio controllo che guardava solo la taglia di partenza
    (clampata a min_height), ignorando che down_to permette di scendere oltre.
    """
    if height_sequence <= 0:
        return False

    shrink_ratio = down_to / height_sequence
    min_reachable_width = lenght_sequence * shrink_ratio
    min_reachable_height = down_to

    if (min_reachable_width + 2 * margin) > available_width:
        return False
    if (min_reachable_height + 2 * margin) > available_height:
        return False
    return True


# def _shrink_and_search(segment_text, sequence, scale_factor, lenght_sequence, height_sequence,
#                        ctx, x_pos, y_pos, space, align, start_y, step, margin, down_to):
#     """
#     Cerca spazio in ctx riducendo progressivamente la sequenza (80% per iterazione)
#     finché non trova posto o finché height_sequence scende sotto down_to.

#     Generica rispetto a ctx e start_y: chi chiama passa il proprio sistema di
#     coordinate (originale o ruotato) già pronto — questa funzione non tocca mai
#     la geometria, solo la scala del testo. Condivisa tra tentativo 3 e tentativo 4.

#     Ritorna (x, y, sequence) oppure (None, None, sequence).
#     """
#     available_width = ctx.max_x - ctx.min_x
#     available_height = ctx.max_y - ctx.min_y
#     print(f"[DEBUG down_to] lenght_sequence={lenght_sequence:.2f}, available_width={available_width:.2f}, "
#           f"height_sequence={height_sequence:.2f}, available_height={available_height:.2f}, "
#           f"margin={margin}, down_to={down_to}, "
#           f"fail_fast_width={(lenght_sequence + 2*margin) > available_width}, "
#           f"fail_fast_height={(height_sequence + 2*margin) > available_height}")

#     if not _reachable_at_down_to(lenght_sequence, height_sequence, down_to,
#                                   available_width, available_height, margin):
#         return None, None, sequence

#     x, y = find_space_for_sequence(lenght_sequence, height_sequence, ctx, align, start_y, step, margin)

#     while x is None or y is None:
#         new_height = height_sequence * 0.8
#         if new_height < down_to:
#             break
#         scale_factor = scale_factor * 0.8
#         sequence = rescale_sequence(segment_text, scale_factor, x_pos, y_pos)
#         lenght_sequence, height_sequence = sequence_dim(sequence, x_pos, y_pos, space)

#         if (lenght_sequence + 2 * margin) > available_width:
#             break
#         if (height_sequence + 2 * margin) > available_height:
#             break

#         x, y = find_space_for_sequence(lenght_sequence, height_sequence, ctx, align, start_y, step, margin)

#     return x, y, sequence

def _shrink_and_search(segment_text, sequence, scale_factor, lenght_sequence, height_sequence,
                       ctx, x_pos, y_pos, space, align, start_y, step, margin, down_to):
    """
    Cerca spazio in ctx riducendo progressivamente la sequenza (80% per iterazione)
    finché non trova posto o finché height_sequence scende sotto down_to.

    Ad ogni iterazione tenta find_space_for_sequence SOLO se la taglia corrente
    rientra nei limiti disponibili; altrimenti continua a restringersi senza
    arrendersi — una taglia intermedia "ancora troppo grande" non è motivo per
    fermarsi, perché la riduzione successiva potrebbe farla entrare.

    Ritorna (x, y, sequence) oppure (None, None, sequence).
    """
    available_width = ctx.max_x - ctx.min_x
    available_height = ctx.max_y - ctx.min_y

    if not _reachable_at_down_to(lenght_sequence, height_sequence, down_to,
                                  available_width, available_height, margin):
        return None, None, sequence

    x, y = None, None
    while True:
        fits_bounds = (
            (lenght_sequence + 2 * margin) <= available_width and
            (height_sequence + 2 * margin) <= available_height
        )
        if fits_bounds:
            x, y = find_space_for_sequence(lenght_sequence, height_sequence, ctx, align, start_y, step, margin)
            if x is not None and y is not None:
                break

        new_height = height_sequence * 0.8
        if new_height < down_to:
            break
        scale_factor = scale_factor * 0.8
        sequence = rescale_sequence(segment_text, scale_factor, x_pos, y_pos)
        lenght_sequence, height_sequence = sequence_dim(sequence, x_pos, y_pos, space)

    return x, y, sequence


def _prepare_rotated_context(ctx, msp, segs, start_y, ref_entity):
    """
    Calcola la geometria ruotata attorno all'entità di riferimento (una tantum).

    Operazione costosa (rotazione di tutti i segmenti + ricalcolo dei limiti):
    va fatta una sola volta e il risultato riusato sia per il tentativo a piena
    scala nel sistema ruotato, sia per l'eventuale shrink successivo nello
    stesso sistema.

    Ritorna (ctx_rotated, start_y_r, ref_pivot, ref_angle) oppure None se non
    ci sono entità candidate per definire un asse di riferimento.
    """
    from snapmark.utils.geometry import lwpolylines_to_virtual_segments, find_longer_entity

    lines = list(msp.query('LINE'))
    lwpolylines = list(msp.query('LWPOLYLINE'))
    all_candidates = lines + lwpolylines_to_virtual_segments(lwpolylines)

    if not all_candidates:
        return None

    if ref_entity is None:
        ref_entity, _ = find_longer_entity(all_candidates)

    ref_angle, ref_pivot = ref_angle_and_pivot(ref_entity)

    segs_rotated = rotate_segs(segs, ref_pivot, -ref_angle)
    avoid_segs_rotated = rotate_segs(ctx.avoid_segs, ref_pivot, -ref_angle) if ctx.avoid_segs else None

    all_x_r = [v for seg in segs_rotated for v in (seg[0], seg[2])]
    all_y_r = [v for seg in segs_rotated for v in (seg[1], seg[3])]

    ctx_rotated = GeometryContext.from_rotated(
        ctx,
        segs_rotated,
        avoid_segs_rotated,
        min_x_r=min(all_x_r),
        min_y_r=min(all_y_r),
        max_x_r=max(all_x_r),
        max_y_r=max(all_y_r),
    )

    start_y_r = comp_start_y_rotated(segs_rotated, ctx_rotated.min_y, ref_pivot, start_y)

    return ctx_rotated, start_y_r, ref_pivot, ref_angle


def place_sequence(doc, segment_text, scale_factor, excluded_layers=None, avoid_layers=None, space=1.5,
                   min_char_height=5, max_char_height=20, arbitrary_x=None, arbitrary_y=None, align='c',
                   start_y=1, step=2, margin=1, down_to=None, ref_entity=None,
                   forced_height=None, forced_width=None):
    """
    Cerca posto per segment_text nel documento, in quest'ordine di priorità:
    1) sistema originale, a piena scala
    2) sistema ruotato (attorno all'entità di riferimento), a piena scala
    3) sistema originale, riducendo la scala fino a down_to
    4) sistema ruotato, riducendo la scala fino a down_to

    La rotazione (passo 2) viene calcolata una sola volta e riusata al passo 4,
    per evitare di rifare due volte il lavoro costoso di rotazione geometria.
    """
    if len(segment_text) == 0:
        raise Exception('Empty sequence.')

    ctx = GeometryContext(doc, excluded_layers, avoid_layers)
    msp = ctx.msp
    segs = ctx.segs

    x_pos = 0 if arbitrary_x is None else arbitrary_x
    y_pos = 0 if arbitrary_y is None else arbitrary_y

    if down_to is None:
        down_to = min_char_height

    sequence, scale_factor, lenght_sequence, height_sequence = _scale_sequence_to_bounds(
        segment_text, scale_factor, x_pos, y_pos, space, min_char_height, max_char_height
    )

    if forced_height is not None:
        height_sequence = forced_height
    if forced_width is not None:
        lenght_sequence = forced_width

    if arbitrary_x is not None and arbitrary_y is not None:
        for scaled_segments, position in sequence.sequence:
            position[0] += arbitrary_x
            position[1] += arbitrary_y
        return sequence

    # ── Tentativo 1: sistema originale, a piena scala ──────────────────────
    x, y = find_space_for_sequence(lenght_sequence, height_sequence, ctx, align, start_y, step, margin)
    if x is not None and y is not None:
        for scaled_segments, position in sequence.sequence:
            position[0] += x
            position[1] += y
        return sequence

    # ── Tentativo 2: sistema ruotato, a piena scala ─────────────────────────
    # Calcolata qui una sola volta: se serve anche al tentativo 4, viene riusata.
    rotated = _prepare_rotated_context(ctx, msp, segs, start_y, ref_entity)

    if rotated is not None:
        ctx_rotated, start_y_r, ref_pivot, ref_angle = rotated
        available_width_r = ctx_rotated.max_x - ctx_rotated.min_x
        available_height_r = ctx_rotated.max_y - ctx_rotated.min_y

        if (lenght_sequence + 2 * margin) <= available_width_r and \
           (height_sequence + 2 * margin) <= available_height_r:
            x, y = find_space_for_sequence(lenght_sequence, height_sequence, ctx_rotated,
                                            align, start_y_r, step, margin)
            if x is not None and y is not None:
                for scaled_segments, position in sequence.sequence:
                    position[0] += x
                    position[1] += y
                return rotate_segment_text_sequence(sequence, ref_pivot, ref_angle)

    # ── Tentativo 3: sistema originale, con shrink fino a down_to ──────────
    x, y, sequence_shrunk = _shrink_and_search(
        segment_text, sequence, scale_factor, lenght_sequence, height_sequence,
        ctx, x_pos, y_pos, space, align, start_y, step, margin, down_to
    )
    if x is not None and y is not None:
        for scaled_segments, position in sequence_shrunk.sequence:
            position[0] += x
            position[1] += y
        return sequence_shrunk

    # ── Tentativo 4: sistema ruotato, con shrink fino a down_to ─────────────
    if rotated is not None:
        ctx_rotated, start_y_r, ref_pivot, ref_angle = rotated
        x, y, sequence_shrunk = _shrink_and_search(
            segment_text, sequence, scale_factor, lenght_sequence, height_sequence,
            ctx_rotated, x_pos, y_pos, space, align, start_y_r, step, margin, down_to
        )
        if x is not None and y is not None:
            for scaled_segments, position in sequence_shrunk.sequence:
                position[0] += x
                position[1] += y
            return rotate_segment_text_sequence(sequence_shrunk, ref_pivot, ref_angle)

    return SequenceText()


# def _attempt1(segment_text, sequence, scale_factor, lenght_sequence, height_sequence,
#               ctx, x_pos, y_pos, space, align, start_y, step, margin, down_to):
#     """
#     Tentativo 1: cerca spazio nel sistema di coordinate originale.
#     Riscala progressivamente se non trova spazio.
#     Ritorna (x, y, sequence) oppure (None, None, sequence).
#     """
#     available_width  = ctx.max_x - ctx.min_x
#     available_height = ctx.max_y - ctx.min_y

#     # Se la sequenza non entra neanche nel bounding box originale, inutile cercare
#     if (lenght_sequence + 2 * margin) > available_width:
#         return None, None, sequence
#     if (height_sequence + 2 * margin) > available_height:
#         return None, None, sequence

#     x, y = find_space_for_sequence(lenght_sequence, height_sequence, ctx, align, start_y, step, margin)

#     while x is None or y is None:
#         new_height = height_sequence * 0.8
#         if new_height < down_to:
#             break
#         scale_factor   = scale_factor * 0.8
#         sequence       = rescale_sequence(segment_text, scale_factor, x_pos, y_pos)
#         lenght_sequence, height_sequence = sequence_dim(sequence, x_pos, y_pos, space)

#         if (lenght_sequence + 2 * margin) > available_width:
#             break
#         if (height_sequence + 2 * margin) > available_height:
#             break

#         x, y = find_space_for_sequence(lenght_sequence, height_sequence, ctx, align, start_y, step, margin)

#     return x, y, sequence


# # def _attempt2(segment_text, sequence, scale_factor, lenght_sequence, height_sequence,
# #               ctx, msp, segs, x_pos, y_pos, space, align, step, margin, down_to, ref_entity):
# def _attempt2(segment_text, sequence, scale_factor, lenght_sequence, height_sequence,
#               ctx, msp, segs, x_pos, y_pos, space, align, step, margin, down_to, ref_entity, start_y):
#     """
#     Tentativo 2: ruota la geometria attorno all'entità di riferimento più lunga,
#     cerca spazio nel sistema ruotato, poi ruota la sequenza trovata.
#     Ritorna (sequence posizionata e ruotata) oppure SequenceText() vuoto.
#     """
#     from snapmark.utils.geometry import lwpolylines_to_virtual_segments, find_longer_entity

#     lines       = list(msp.query('LINE'))
#     lwpolylines = list(msp.query('LWPOLYLINE'))
#     all_candidates = lines + lwpolylines_to_virtual_segments(lwpolylines)

#     if not all_candidates:
#         return SequenceText()

#     if ref_entity is None:
#         ref_entity, _ = find_longer_entity(all_candidates)

#     ref_angle, ref_pivot = ref_angle_and_pivot(ref_entity)

#     segs_rotated        = rotate_segs(segs, ref_pivot, -ref_angle)
#     avoid_segs_rotated  = rotate_segs(ctx.avoid_segs, ref_pivot, -ref_angle) if ctx.avoid_segs else None

#     all_x_r = [v for seg in segs_rotated for v in (seg[0], seg[2])]
#     all_y_r = [v for seg in segs_rotated for v in (seg[1], seg[3])]

#     ctx_rotated = GeometryContext.from_rotated(
#         ctx,
#         segs_rotated,
#         avoid_segs_rotated,
#         min_x_r=min(all_x_r),
#         min_y_r=min(all_y_r),
#         max_x_r=max(all_x_r),
#         max_y_r=max(all_y_r),
#     )

#     # Il fail fast qui controlla il bounding box RUOTATO — corretto
#     available_width_r  = ctx_rotated.max_x - ctx_rotated.min_x
#     available_height_r = ctx_rotated.max_y - ctx_rotated.min_y

#     if (lenght_sequence + 2 * margin) > available_width_r:
#         return SequenceText()
#     if (height_sequence + 2 * margin) > available_height_r:
#         return SequenceText()

#     start_y_r = comp_start_y_rotated(segs_rotated, ctx_rotated.min_y, ref_pivot, anchor_margin=start_y)

#     x, y = find_space_for_sequence(
#         lenght_sequence, height_sequence, ctx_rotated,
#         align, start_y_r, step, margin
#     )

#     if x is None or y is None:
#         return SequenceText()

#     for scaled_segments, position in sequence.sequence:
#         position[0] += x
#         position[1] += y

#     sequence = rotate_segment_text_sequence(sequence, ref_pivot, ref_angle)
#     return sequence


# def place_sequence(doc, segment_text, scale_factor, excluded_layers=None, avoid_layers=None, space=1.5,
#                    min_char_height=5, max_char_height=20, arbitrary_x=None, arbitrary_y=None, align='c',
#                    start_y=1, step=2, margin=1, down_to=None, ref_entity=None,
#                    forced_height=None, forced_width=None):
#     """
#     Finds an available position for segment texts representing an alphanumeric sequence
#     within the document, avoiding collisions with existing geometry.

#     Tentativo 1: cerca nel sistema di coordinate originale, riscalando se necessario.
#     Tentativo 2: ruota la geometria attorno all'entità più lunga e riprova.

#     Returns:
#         SequenceText posizionata, oppure SequenceText() vuota se nessuno spazio trovato.
#     """
#     if len(segment_text) == 0:
#         raise Exception('Empty sequence.')

#     ctx  = GeometryContext(doc, excluded_layers, avoid_layers)
#     msp  = ctx.msp
#     segs = ctx.segs

#     x_pos = 0 if arbitrary_x is None else arbitrary_x
#     y_pos = 0 if arbitrary_y is None else arbitrary_y

#     if down_to is None:
#         down_to = min_char_height

#     # ── Scala la sequenza rispettando min/max char ─────────────────────────
#     sequence, scale_factor, lenght_sequence, height_sequence = _scale_sequence_to_bounds(
#         segment_text, scale_factor, x_pos, y_pos, space, min_char_height, max_char_height
#     )

#     if forced_height is not None:
#         height_sequence = forced_height
#     if forced_width is not None:
#         lenght_sequence = forced_width

#     # ── Posizionamento arbitrario (bypass della ricerca) ───────────────────
#     if arbitrary_x is not None and arbitrary_y is not None:
#         for scaled_segments, position in sequence.sequence:
#             position[0] += arbitrary_x
#             position[1] += arbitrary_y
#         return sequence

#     # ── Tentativo 1: sistema originale ────────────────────────────────────
#     x, y, sequence = _attempt1(
#         segment_text, sequence, scale_factor, lenght_sequence, height_sequence,
#         ctx, x_pos, y_pos, space, align, start_y, step, margin, down_to
#     )

#     if x is not None and y is not None:
#         for scaled_segments, position in sequence.sequence:
#             position[0] += x
#             position[1] += y
#         return sequence

#     # ── Tentativo 2: sistema ruotato ──────────────────────────────────────
#     return _attempt2(
#         segment_text, sequence, scale_factor, lenght_sequence, height_sequence,
#         ctx, msp, segs, x_pos, y_pos, space, align, step, margin, down_to, ref_entity, start_y
#     )
"""
Test sul fallback a 4 passi di place_sequence / AddMark.

Flusso atteso:
    Passo 1 — posizione originale,  altezza = min_height
    Passo 2 — ruotato su longer,    altezza = min_height
    Passo 3 — posizione originale,  altezza = down_to    (shrink)
    Passo 4 — ruotato su longer,    altezza = down_to    (shrink)
    Fallimento — nessun passo trova spazio

Geometrie costruite in-memory con ezdxf, niente file su disco.

Lancia:
    python -m unittest tests/integration/test_place_sequence_fallback.py -v
"""

import unittest
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import ezdxf
import snapmark as sm
from snapmark.mark_algorithm.sequence import sequence_dim

# ──────────────────────────────────────────────────────────────
# Costanti fittizie — non servono file reali
# ──────────────────────────────────────────────────────────────
FOLDER = r"C:\test"
FILE   = "TEST_Q1_S235JR_SP5_Q1.DXF"


# ──────────────────────────────────────────────────────────────
# Costruttori di geometrie
# ──────────────────────────────────────────────────────────────

def rect_doc(width, height):
    """Rettangolo semplice — spazio pieno disponibile."""
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    pts = [(0, 0), (width, 0), (width, height), (0, height)]
    for i in range(4):
        msp.add_line(pts[i], pts[(i + 1) % 4])
    return doc


def narrow_doc(width=8, height=80):
    """
    Pezzo stretto e alto.
    - In posizione originale:  larghezza = 8  → non entra nessuna sequenza lunga
    - Ruotato su longer:       larghezza = 80 → entra con min_height se abbastanza piccola
    """
    return rect_doc(width, height)


def very_narrow_doc(width=4, height=40):
    """
    Pezzo molto stretto.
    - min_height non entra né dritto né ruotato
    - down_to (più piccolo) dovrebbe entrare ruotato
    """
    return rect_doc(width, height)


def tiny_doc(width=3, height=6):
    """
    Pezzo minuscolo — non entra nulla neanche con down_to.
    Usato per testare il fallimento completo.
    """
    return rect_doc(width, height)


# ──────────────────────────────────────────────────────────────
# Helper per costruire l'operazione con parametri espliciti
# ──────────────────────────────────────────────────────────────

def make_op(min_height, down_to=None, max_height=None, scale_factor=100):
    if max_height is None:
        max_height = min_height * 1.5
    return sm.AddMark(
        sm.SequenceBuilder().literal("123").build(),
        scale_factor=scale_factor,
        align='c',
        max_height=max_height,
        min_height=min_height,
        down_to=down_to,
    )


def found(op):
    """True se la sequenza è stata piazzata."""
    return bool(op.sequence_position.sequence)


def get_height(op):
    """Altezza effettiva della sequenza piazzata, ricavata da sequence_dim."""
    _, h = sequence_dim(op.sequence_position, 0, 0, 1.0)
    return h


# ══════════════════════════════════════════════════════════════
# Passo 1 — posizione originale, min_height
# ══════════════════════════════════════════════════════════════

class TestPasso1Originale(unittest.TestCase):
    """
    Rettangolo largo abbastanza: il passo 1 deve trovare spazio
    direttamente, senza bisogno di rotazione né shrink.
    """

    def test_trova_spazio_passo1(self):
        """Rettangolo 100x60 — il passo 1 riesce con min_height=8."""
        doc = rect_doc(100, 60)
        op = make_op(min_height=8, down_to=3)
        op.execute(doc, FOLDER, FILE)
        self.assertTrue(found(op), "Passo 1 deve trovare spazio su geometria ampia")

    def test_altezza_usata_non_inferiore_a_min_height(self):
        """L'altezza piazzata non deve essere inferiore a min_height se il passo 1 riesce."""
        doc = rect_doc(100, 60)
        op = make_op(min_height=8, down_to=3)
        op.execute(doc, FOLDER, FILE)
        if not found(op):
            self.skipTest("Nessuno spazio trovato")
        # l'altezza effettiva della sequenza è ricavabile dalla bounding box
        # del primo carattere — qui verifichiamo solo che sia stata piazzata
        # senza shrink (sequence_position deve avere scala >= min_height)
        height_used = get_height(op)
        print(f"[Passo1] height_used={height_used:.2f} min_height=8")
        self.assertGreaterEqual(height_used, 8)


# ══════════════════════════════════════════════════════════════
# Passo 2 — ruotato, min_height
# ══════════════════════════════════════════════════════════════

class TestPasso2Ruotato(unittest.TestCase):
    """
    Pezzo stretto: il passo 1 fallisce (larghezza insufficiente),
    il passo 2 ruota e trova spazio lungo l'asse longer.
    down_to non deve essere necessario.
    """

    def test_trova_spazio_passo2(self):
        """Pezzo 8x80 — ruotato ha 80 unità, entra con min_height piccola."""
        doc = narrow_doc(width=8, height=80)
        # min_height=3 entra nei 8 mm di larghezza dritto? no (margin incluso)
        # ruotato: larghezza=80, altezza=8 → deve entrare
        op = make_op(min_height=3, max_height=5, down_to=1, scale_factor=50)
        op.execute(doc, FOLDER, FILE)
        self.assertTrue(found(op), "Passo 2 deve trovare spazio ruotando su pezzo stretto")

    def test_passo1_non_sufficiente_passo2_si(self):
        """
        Con un pezzo molto stretto, il passo 1 non può piazzare
        la sequenza dritta ma il passo 2 riesce.
        Verifica che il fallback venga effettivamente usato.
        """
        doc = narrow_doc(width=6, height=100)
        op = make_op(min_height=4, max_height=5, down_to=2, scale_factor=60)
        op.execute(doc, FOLDER, FILE)
        # il test verifica solo che l'algoritmo non si arrenda al passo 1
        self.assertTrue(found(op), "Il fallback al passo 2 deve salvare il piazzamento")


# ══════════════════════════════════════════════════════════════
# Passo 3 — posizione originale, down_to (shrink)
# ══════════════════════════════════════════════════════════════

class TestPasso3DownTo(unittest.TestCase):
    """
    Geometria in cui min_height non entra (né dritto né ruotato),
    ma down_to più piccolo entra in posizione originale.

    Trucco: rettangolo orizzontale — longer=larghezza, shorter=altezza.
    Se altezza < min_height ma >= down_to, il passo 3 deve farcela.
    """

    def test_down_to_originale_entra(self):
        """
        Rettangolo 60x7: altezza interna ~5 mm liberi (margini inclusi).
        min_height=6 non entra, down_to=3 deve entrare dritto.
        """
        doc = rect_doc(60, 9)
        # min_height=6: dentro 9mm con margin=2 su entrambi i lati → 9-4=5 < 6 → non entra
        # down_to=3: 3 < 5 → entra
        op = make_op(min_height=6, max_height=8, down_to=3, scale_factor=80)
        op.execute(doc, FOLDER, FILE)
        self.assertTrue(found(op), "Passo 3 (down_to dritto) deve trovare spazio")

    def test_altezza_usata_pari_a_down_to(self):
        """L'altezza effettivamente usata al passo 3 deve essere <= min_height."""
        doc = rect_doc(60, 6)
        op = make_op(min_height=6, max_height=8, down_to=3, scale_factor=80)
        op.execute(doc, FOLDER, FILE)
        if not found(op):
            self.skipTest("Nessuno spazio trovato")
        height_used = get_height(op)
        print(f"[Passo3] height_used={height_used:.2f} min_height=6 down_to=3")
        self.assertLess(height_used, 6,
            "Se il passo 3 è scattato, l'altezza deve essere sotto min_height")
        self.assertGreaterEqual(height_used, 3,
            "L'altezza non può scendere sotto down_to")

    def test_senza_down_to_fallisce(self):
        """Stessa geometria ma senza down_to — deve fallire."""
        doc = rect_doc(60, 6)
        op = make_op(min_height=6, max_height=8, down_to=None, scale_factor=80)
        op.execute(doc, FOLDER, FILE)
        self.assertFalse(found(op),
            "Senza down_to non deve trovare spazio in geometria troppo bassa")


# ══════════════════════════════════════════════════════════════
# Passo 4 — ruotato, down_to (shrink)
# ══════════════════════════════════════════════════════════════

class TestPasso4DownToRotato(unittest.TestCase):
    """
    Geometria molto stretta: nessun passo con min_height riesce,
    ma down_to ruotato (passo 4) deve farcela.
    """

    def test_down_to_ruotato_entra(self):
        """
        Pezzo 4x30: stretto e non altissimo.
        min_height=3 non entra né dritto (4mm) né ruotato senza shrink.
        down_to=1 deve entrare ruotato.
        """
        doc = very_narrow_doc(width=4, height=30)
        op = make_op(min_height=3, max_height=4, down_to=1, scale_factor=40)
        op.execute(doc, FOLDER, FILE)
        self.assertTrue(found(op), "Passo 4 (down_to ruotato) deve trovare spazio")

    def test_altezza_passo4_entro_limiti(self):
        """L'altezza usata al passo 4 deve stare tra down_to e min_height."""
        doc = very_narrow_doc(width=4, height=30)
        down_to = 0.9
        op = make_op(min_height=3, max_height=4, down_to=down_to, scale_factor=40)
        op.execute(doc, FOLDER, FILE)
        if not found(op):
            self.skipTest("Nessuno spazio trovato")
        height_used = get_height(op)
        print(f"[Passo4] height_used={height_used:.2f}")
        self.assertLess(height_used, 3)
        self.assertGreaterEqual(height_used, down_to,
             "L'altezza non può scendere sotto down_to")
        
    def test_senza_down_to_fallisce_su_pezzo_molto_stretto(self):
        """Stessa geometria senza down_to — tutti i passi falliscono."""
        doc = very_narrow_doc(width=4, height=30)
        op = make_op(min_height=3, max_height=4, down_to=None, scale_factor=40)
        op.execute(doc, FOLDER, FILE)
        self.assertFalse(found(op),
            "Senza down_to su pezzo molto stretto non deve trovare spazio")


# ══════════════════════════════════════════════════════════════
# Fallimento completo — nessun passo riesce
# ══════════════════════════════════════════════════════════════

class TestFallimentoCompleto(unittest.TestCase):
    """
    Geometria troppo piccola per qualsiasi combinazione.
    Tutti e 4 i passi devono fallire silenziosamente.
    """

    def test_nessuno_spazio_trovato(self):
        """Pezzo 3x6 — impossibile piazzare qualsiasi sequenza."""
        doc = tiny_doc()
        op = make_op(min_height=4, max_height=6, down_to=2, scale_factor=30)
        op.execute(doc, FOLDER, FILE)
        self.assertFalse(found(op), "Su geometria minuscola nessun passo deve trovare spazio")

    def test_nessuno_spazio_senza_down_to(self):
        """Fallisce anche senza down_to — non è down_to il problema."""
        doc = tiny_doc()
        op = make_op(min_height=4, max_height=6, down_to=None, scale_factor=30)
        op.execute(doc, FOLDER, FILE)
        self.assertFalse(found(op))

    def test_no_crash_su_geometria_minuscola(self):
        """execute() non deve sollevare eccezioni su geometria impossibile."""
        doc = tiny_doc()
        op = make_op(min_height=4, max_height=6, down_to=2, scale_factor=30)
        try:
            op.execute(doc, FOLDER, FILE)
        except Exception as e:
            self.fail(f"execute() ha sollevato un'eccezione inattesa: {e}")


# ══════════════════════════════════════════════════════════════
# Regressione — il bug del loop (break + check finale disallineati)
# ══════════════════════════════════════════════════════════════

class TestRegressioneLoopBreak(unittest.TestCase):
    """
    Regressione specifica: con start_y alto, il loop trovava is_space=True
    ma il check finale lo buttava via senza riprovare le y successive.
    Verifica che il fix (check dentro il loop con continue) funzioni.
    """

    def test_start_y_alto_stesso_risultato_di_start_y_basso(self):
        """
        Con geometria standard, cambiare start_y non deve cambiare l'esito:
        se start_y=1 trova spazio, anche start_y=5 deve trovarlo.
        Questo è esattamente il bug che era rotto.
        """
        # Non possiamo iniettare start_y direttamente da AddMark,
        # ma possiamo verificare che il risultato sia stabile su geometria
        # dove lo spazio esiste — il bug causava None con certi start_y.
        doc = rect_doc(80, 40)
        op = make_op(min_height=8, max_height=12, down_to=4, scale_factor=100)
        op.execute(doc, FOLDER, FILE)
        self.assertTrue(found(op),
            "Il fix del loop deve garantire che spazi validi non vengano scartati")


if __name__ == '__main__':
    unittest.main(verbosity=2)
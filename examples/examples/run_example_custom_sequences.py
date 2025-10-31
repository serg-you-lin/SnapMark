import snapmark as sm
import os

# ===== LIVELLO PRINCIPIANTE =====
# Caso più comune: marca col nome file
sm.mark_by_name("Examples/Input")

def part_number(folder, filename):
    """
    Estrae il part number da nomenclatura tipo: S532_P5_S235JR_SP4_Q2.dxf
    
    Ritorna: "P5"
    """
    # Rimuovi estensione
    name = filename.rsplit('.', 1)[0]
    
    # Split su underscore
    parts = name.split('_')
    
    # Cerca la parte che inizia con 'P' seguito da numeri
    for part in parts:
        if part.startswith('P') and len(part) > 1 and part[1:].isdigit():
            return part
    
    return ""

# def get_folder_chars(n):
#     """Ritorna funzione che estrae n caratteri dalla cartella."""
#     def extract(folder, filename):
#         folder_name = os.path.basename(os.path.normpath(folder))
#         return folder_name[:n]
#     return extract

# ===== LIVELLO INTERMEDIO =====
# Costruzione custom ma semplice
seq = (sm.SequenceBuilder()
       .folder(num_chars=2)     # Prime 2 lettere cartella
       .custom(part_number) 
       .build())

sm.mark_with_sequence("Examples/Input_multiple", sequence=seq)  # Passi sequence custom

# # ===== LIVELLO AVANZATO =====
# # Con iteration manager (come fai ora)
# folder = "Examples/Input"
# seq = sm.SequenceBuilder().file_name().build()

# manager = sm.IterationManager(folder, use_backup_system=True)
# manager.add_operation(
#     sm.AddMark(seq, scale_factor=100)
# )
# manager.execute()


# ===== VECCHIO CODICE (ancora funziona) =====
#seq_old = sm.Conc(sm.Conc.FILE_NAME)  # Deprecato ma funzionale
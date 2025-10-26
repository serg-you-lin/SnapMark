import snapmark as sm

# ===== LIVELLO PRINCIPIANTE =====
# Caso più comune: marca col nome file
sm.mark_by_name("Examples/Input")

def part_number():
    # Funzione di estrazione personalizzata che prende spunto da custom dellìapi perpoter essre concatenata
    pass

# Nome file con prima parte (prima di '_')
sm.mark_by_splitted_text("Examples/Input_customizable", separator='_', part_index=0)


# ===== LIVELLO INTERMEDIO =====
# Costruzione custom ma semplice
seq = (sm.SequenceBuilder()
       .file_part(part_index=0)  # Prima parte
       .folder(num_chars=2)      # Prime 2 lettere cartella
       .build())

sm.mark_with_sequence("Examples/Input_multiple", sequence=seq)  # Passi sequence custom

seq = (sm.SequenceBuilder()
       .file_part(part_index=0)  # Prima parte
       .custom('part_number')      # Prime 2 lettere cartella
       .build())
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
seq_old = sm.Conc(sm.Conc.FILE_NAME)  # Deprecato ma funzionale
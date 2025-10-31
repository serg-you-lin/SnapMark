"""
Esempio: pipeline multipla di operazioni su cartella DXF
"""

import snapmark as sm

if __name__ == "__main__":
    folder_path = "Examples/Input"

    # Crea gestore iterazioni
    manager = sm.IterationManager(folder_path)

    # Aggiunge operazioni alla pipeline
    manager.add_operation(
        sm.Aligner(),
        sm.AddMark(sm.Conc(sm.Conc.FILE_NAME)),
        sm.CountHoles(sm.find_circle_by_radius(5, 10))
    )

    print(f"👉 Esecuzione pipeline su: {folder_path}")
    manager.execute()

    print("✅ Pipeline completata.")

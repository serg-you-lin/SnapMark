"""
Esempio: marcatura di tutti i file in una cartella
"""

import snapmark as sm

if __name__ == "__main__":
    folder_path = "Examples/Input"

    sequence = sm.Conc(sm.Conc.FILE_NAME)
    mark = sm.AddMark(sequence, scale_factor=100)

    print(f"👉 Marca tutti i file nella cartella: {folder_path}")
    sm.Operation.process_folder(folder_path, mark)

    print("✅ Marcatura cartella completata.")

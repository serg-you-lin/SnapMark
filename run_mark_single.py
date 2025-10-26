"""
Esempio: marcatura di un singolo file DXF
"""
import snapmark as sm

if __name__ == "__main__":
    file_path = ("Examples\Input\F1.dxf")

    sequence = sm.Conc(sm.Conc.FILE_NAME)
    mark = sm.AddMark(sequence, scale_factor=100)

    print(f"👉 Marca singolo file: {file_path}")
    mark.execute_single(file_path)

    print("✅ Marcatura completata.")

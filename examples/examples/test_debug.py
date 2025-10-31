import snapmark as sm

# Test diretto del componente
seq = sm.SequenceBuilder().folder(num_chars=3).build()

# Test con percorso esempio
test_folder = "Examples/Input"
test_file = "F1.dxf"

result = seq.get_sequence_text(test_folder, test_file)
print(f"Folder: {test_folder}")
print(f"Risultato: '{result}'")
print(f"Lunghezza: {len(result)}")

# Test anche con SequenceBuilder completo
seq2 = (sm.SequenceBuilder()
        .file_name()
        .literal("-")
        .folder(num_chars=3)
        .build())

result2 = seq2.get_sequence_text(test_folder, test_file)
print(f"\nSequenza completa: '{result2}'")
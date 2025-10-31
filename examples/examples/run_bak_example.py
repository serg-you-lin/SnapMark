import snapmark as sm

folder_path = r'Examples/Input'
sequence = sm.Conc(sm.Conc.FIRST_FOLDER_CHAR, sm.Conc.FILE_NAME)
print('sequenza', sequence)

ToMark = sm.iteration_manager(folder_path, use_backup_system=True)
ToMark.add_operation(sm.AddMark(sequence, min_char=10, max_char=20, align='c', scale_factor=100, down_to=2))
ToMark.file_selection_logic()

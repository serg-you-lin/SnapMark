import os

class Sequence:
    def get_sequence_text(self, folder, file_name):
        if self.text == None:
            raise Exception('Costruire la sequenza')   #Con raise non serve il return
        else:
            return self.text

    def prompt_seq(self):
        self.text = input("Inserire testo della marcatura: ")


class Conc(Sequence):   # creare sequenza concatenando le varie stringhe
    FIRST_FOLDER_CHAR = '[FDFC]'
    FOLDER_NAME ='[FDN]'
    LAST_FILE_CHAR_IF_LETTER = '[LIL]'
    FILE_NAME = '[FLN]'
    FILE_NAME_CAMPANA = '[FLC]'
    PART_NUMBER_CAMPANA = '[PNC]'
    LETTERA_DIVERSA_OGNI_NOME = '[LDON]'
    OEP_FILE_NAME = '[OEPFN]'

    def __init__(self, *text):
        self.text = text
        self.number = 1

    def __sep_logic(file_name, sep):
        separator = file_name.find(sep)
        name = file_name[:separator]
        return name

    def num_char(self, number=1):
        self.number = number

        return self 

                

    def get_sequence_text(self, folder, file_name):
        text_list = []
        for t in self.text:
            if t == Conc.FIRST_FOLDER_CHAR:
                # Ottieni il nome dell'ultima cartella nel percorso
                folder_name = os.path.basename(os.path.normpath(folder))
                num = self.number
                first_char_folder = folder_name[:num]
                text_list.append(first_char_folder)

            elif t == Conc.FILE_NAME:
                last_dot = file_name.rfind('.')
                text_list.append(file_name[:last_dot])
                # text_list.append(Conc.__sep_logic('.'))

            elif t == Conc.FILE_NAME_CAMPANA:
                # text_list.append(Conc.__sep_logic('_'))
                first_underscore = file_name.find('_')
                text_list.append(file_name[:first_underscore])

            elif t == Conc.PART_NUMBER_CAMPANA:
                first_underscore = file_name.find("_")
                second_underscore = file_name.find("_", first_underscore + 1)
                name = file_name[first_underscore:second_underscore]
                text_list.append(name)

            elif t == Conc.LAST_FILE_CHAR_IF_LETTER:
                first_underscore = file_name.find('_')
                if first_underscore > 0:
                    last_char = file_name[first_underscore - 1]
                    if last_char.isalpha():
                        text_list.append(last_char)

            elif t == Conc.OEP_FILE_NAME:
                pass
                
            else:
                text_list.append(t)

        return '-'.join(text_list)    
        


    def solo_questa_folder(self):
        pass

class FixSeq(Sequence):
    def __init__(self, text):
        self.text = text

class PromptSeq(Sequence):
    def __init__(self):
        self.text = input("Insert sequence text: " )
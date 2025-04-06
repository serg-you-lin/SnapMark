from SnapMark.Operations.Basic_Operations import *

class Counter(Operation):
    def __init__(self):
        self.counter = 0

    def execute(self, doc, folder, file_name):
        pass

    def message(self, file_name):
        pass

    def add_to_counter(self, quantity):
        self.counter += quantity

    def count_message(self):
        pass


class CountFiles(Counter):
    def __init__(self):
        super().__init__()

    def execute(self, doc, folder, file_name):
        self.add_to_counter(1)

    def count_message(self):
        print(f"Nella cartella selezionata ci sono {self.counter} files.")


class CountHoles(Counter):
    def __init__(self, find_circle_function, mess=False):
        super().__init__()
        self.find_circle_function = find_circle_function
        self.create_new = False
        self.message_text = None
        self.holes_count = None
        self.mess = mess
        self.function = None

    def execute(self, doc, folder, file_name):
        holes = self.find_circle_function(doc)
        if self.function:
            self.holes_count = count_holes(holes) * self.function(file_name)
        else:
            self.holes_count = count_holes(holes)
        self.add_to_counter(self.holes_count)
        return self.create_new
    
    def message(self, file_name):
        if self.mess:
            if not self.holes_count:
                self.message_text = f"Nel file non sono presenti fori del diametro specificato"
            else:
                self.message_text = f"Nel file {file_name} sono presenti {self.holes_count} fori dal diametro selezionato"
            print(self.message_text)

    def count_message(self):
        print(f"Totale fori: {self.counter}")

    def mult(self, function):
        self.function = function
        return self

import snapmark as sm

def mult_function(file_name):
    Q_underscore = file_name.find("_Q")
    if Q_underscore == -1:
        return 1
    quantity = file_name[Q_underscore:]
    factor = ''.join(c for c in quantity if c.isdigit())
    result = int(factor) if factor else 1
    print(f"  [MULT] {file_name} → x{result}")  # ← DEBUG
    return result

folder = "Examples/Input_multiple"

print("=== TEST 1: Stesso range, no backup, con verbose ===")
counter = sm.CountHoles(
    sm.find_circle_by_radius(min_diam=5, max_diam=13),
    mess=True  # ← Mostra conteggio per file
)

manager = sm.iteration_manager(folder, use_backup_system=False)
manager.add_operation(counter)
manager.execute()

print("\n=== TEST 2: Con moltiplicatore ===")
counter2 = sm.CountHoles(
    sm.find_circle_by_radius(min_diam=5, max_diam=13),
    mess=True
).mult(mult_function)

manager2 = sm.iteration_manager(folder, use_backup_system=False)
manager2.add_operation(counter2)
manager2.execute()
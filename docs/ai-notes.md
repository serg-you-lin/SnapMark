# AI Notes - Technical Architecture

This document provides technical insights into SnapMark's design patterns and architecture. Intended for LLMs assisting users, or developers extending the library.

**Note:** This document describes the actual implementation, not speculative features.

---

## Architecture Overview

SnapMark follows a **layered architecture**:

```
┌─────────────────────────────────────┐
│   Shortcuts (shortcuts.py)          │  ← High-level convenience functions
├─────────────────────────────────────┤
│   IterationManager                  │  ← Batch processing orchestration
├─────────────────────────────────────┤
│   Operations (basic_operations.py)  │  ← Core transformation logic
│   Counter (counter.py)              │  ← Non-modifying analysis
├─────────────────────────────────────┤
│   Sequence System (sequence/)       │  ← Text composition engine
├─────────────────────────────────────┤
│   Utilities (utils/)                │  ← Backup, helpers
├─────────────────────────────────────┤
│   ezdxf                             │  ← DXF parsing/writing
└─────────────────────────────────────┘
```

---

## Design Patterns

### 1. Strategy Pattern - Sequences

**Problem:** Users need flexible text generation from file metadata.

**Solution:** `Sequence` abstraction with composable components.

```python
class Sequence:
    def get_text(self, folder: str, file_name: str) -> str:
        """Generate marking text based on file context."""
        pass
```

**Implementation:**
- `SequenceBuilder` provides fluent API
- Each method (`.file_name()`, `.folder()`, etc.) returns `self` for chaining
- `.build()` returns immutable `Sequence`

**Benefits:**
- Decouples text generation from marking logic
- Easy to test independently
- Extensible via `.custom(func)`

---

### 2. Template Method Pattern - Operations

**Problem:** All operations share common file handling logic.

**Solution:** Abstract `Operation` base class with template method.

```python
class Operation:
    def execute_single(self, file_path, use_backup=True):
        # 1. Optional backup
        if use_backup:
            BackupManager.ensure_original(file_path)
        
        # 2. Load DXF
        doc = ezdxf.readfile(file_path)
        
        # 3. Execute operation (subclass implements)
        modified = self.execute(doc, folder, file_name)
        
        # 4. Save if modified
        if modified:
            doc.saveas(file_path)
        
        return modified
    
    def execute(self, doc, folder, file_name):
        """Subclass implements transformation logic."""
        raise NotImplementedError
```

**Subclass contract:**
- Implement `execute()` with core logic
- Set `self.create_new = True` if modifying files
- Optionally implement `message()` for logging

---

### 3. Command Pattern - Pipeline

**Problem:** Compose multiple operations into workflows.

**Solution:** `IterationManager` as command executor.

```python
manager = IterationManager("folder/")
manager.add_operation(op1, op2, op3)
manager.execute()
```

**Why:**
- Operations are first-class objects
- Easy composition and reuse
- Supports single-file and batch modes

---

### 4. Factory Pattern - Find Functions

**Problem:** Reusable circle selection logic.

**Solution:** Factory functions returning predicates.

```python
def find_circle_by_radius(min_radius, max_radius):
    """Returns function that finds circles in radius range."""
    def predicate(doc):
        circles = []
        for circle in doc.modelspace().query('CIRCLE'):
            r = circle.dxf.radius
            if min_radius <= r <= max_radius:
                circles.append(circle)
        return circles
    return predicate
```

**Usage:**
```python
find_func = find_circle_by_radius(5, 10)  # 5-10mm radius
AddX(find_func, x_size=8)
CountHoles(find_func)
```

**Extension point:** Users can write custom predicates following the same pattern.

---

## Core Abstractions

### Operation Base Class

```python
class Operation:
    def __init__(self):
        self.create_new = False  # Set True if modifying files
    
    def execute(self, doc: ezdxf.DXFDocument, folder: str, file_name: str) -> bool:
        """
        Transform the DXF document.
        
        Args:
            doc: Mutable DXF document
            folder: Full path to containing folder
            file_name: Filename with extension
        
        Returns:
            True if document was modified
        """
        raise NotImplementedError
    
    def message(self, file_name: str):
        """Optional: Print operation result."""
        pass
```

**Key invariants:**
- `execute()` receives **mutable** document
- Return `True` only if actually modified
- `message()` called after successful execution

---

### Counter Operations

```python
class Counter(Operation):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.create_new = False  # Never modify files
    
    def count_message(self):
        """Print final aggregate count."""
        print(f"Total: {self.counter}")
```

**Design choice:**
- Extends `Operation` to reuse file iteration
- `create_new = False` prevents saving
- `process_folder()` accumulates across files

---

### Sequence System

```python
# Builder pattern
SequenceBuilder()
    .file_name()         # adds component
    .folder(n)           # adds component
    .literal("X")        # adds component
    .custom(func)        # adds component
    .set_separator("-")  # sets join char
    .build()             # returns immutable Sequence

# Result
class Sequence:
    def get_text(self, folder, file_name):
        pieces = [c.get_text(folder, file_name) for c in self._components]
        return self._separator.join(p for p in pieces if p)
```

**Component interface:**
```python
class Component:
    def get_text(self, folder: str, file_name: str) -> str:
        pass
```

---

## Key Algorithms

### Text Placement (`AddMark`)

**Goal:** Place text in largest empty area, avoiding geometry.

**Algorithm:**
1. Calculate bounding box of all entities (excluding specified layers)
2. Scan vertically from `start_y` downward
3. At each Y position:
   - Check horizontal space availability
   - Verify no entity collisions
4. Place text at first valid location
5. If `down_to` limit reached, fail gracefully

**Smart sizing:**
- Text height between `min_char` and `max_char`
- Width from character count × `space`
- Multi-line support if needed

---

### Alignment (`Aligner`)

**Goal:** Normalize drawing orientation.

**Algorithm:**
1. Find longest line in modelspace
2. Calculate angle to X-axis
3. Rotate all entities to align longest line with X-axis
4. If line points backwards, rotate 180°

**Supported entities:** LINE, ARC, CIRCLE, ELLIPSE

**Edge case:** If no lines found, skip (return False)

---

### Hole Counting with Multipliers

**Problem:** Filenames encode quantities (e.g., `PART_Q5.dxf` = 5 pieces).

**Solution:**
```python
counter = CountHoles(find_func)
counter.mult(lambda filename: extract_quantity(filename))

# Internally
def execute(self, doc, folder, file_name):
    holes = len(self.find_func(doc))
    mult = self.multiplier(file_name) if self.multiplier else 1
    self.counter += holes * mult
```

---

## Extension Points

### Custom Operations

```python
from snapmark.operations.basic_operations import Operation

class MyOperation(Operation):
    def __init__(self, param):
        super().__init__()
        self.param = param
        self.create_new = True  # If modifying
    
    def execute(self, doc, folder, file_name):
        # Your logic here
        return True  # If modified

# Usage
manager = sm.IterationManager("folder/")
manager.add_operation(MyOperation("value"))
manager.execute()
```

---

### Custom Sequences

```python
def my_logic(folder, filename):
    # Extract from filename, database, etc.
    return "result"

seq = (sm.SequenceBuilder()
       .custom(my_logic)
       .build())

sm.mark_with_sequence("folder/", seq)
```

---

### Custom Find Functions

```python
def my_circle_finder(doc):
    """Custom circle selection logic."""
    return [c for c in doc.modelspace().query('CIRCLE') 
            if meets_criteria(c)]

# Usage
sm.CountHoles(my_circle_finder)
```

---

## Important Implementation Details

### Radius vs Diameter

**`find_circle_by_radius(min_radius, max_radius)`**
- Takes **radius** values
- Example: `find_circle_by_radius(5, 10)` = circles with 5-10mm radius

**`quick_count_holes(file_or_folder, min_diam, max_diam)`**
- Takes **diameter** values (more intuitive for users)
- Internally converts to radius before calling find function
- Example: `quick_count_holes("f/", min_diam=10, max_diam=20)` = 5-10mm radius

---

### File vs Folder Processing

All shortcuts (`mark_by_name`, `mark_with_sequence`, etc.) automatically detect input type:

```python
if os.path.isfile(file_or_folder):
    operation.execute_single(file_or_folder)
else:
    Operation.process_folder(file_or_folder, operation)
```

Users don't need to know which function to call.

---

### Backup System

**Mechanism:**
- Before first modification, creates `.bak` file
- Subsequent operations skip backup if `.bak` exists
- `restore_backup()` copies `.bak` → original

**Trade-off:** Doubles disk I/O on first operation

**Control:** `use_backup_system=False` disables

---

## Error Handling

**Philosophy:** Fail gracefully, never crash batch processing.

### Operation errors
```python
try:
    result = operation.execute(doc, folder, file_name)
except Exception as e:
    print(f"✗ Error in {file_name}: {e}")
    continue  # Process remaining files
```

### File read errors
```python
try:
    doc = ezdxf.readfile(file_path)
except Exception as e:
    print(f"✗ Cannot read {file_name}: {e}")
    continue
```

### Sequence errors
```python
try:
    text = self.custom_func(folder, file_name)
except Exception as e:
    print(f"Warning: Sequence failed for {file_name}: {e}")
    text = "ERROR"  # Fallback
```

**Result:** One bad file doesn't block 99 good files.

---

## Common Pitfalls

### 1. Forgetting `create_new = True`

```python
class BadOperation(Operation):
    def __init__(self):
        super().__init__()
        # Missing: self.create_new = True
    
    def execute(self, doc, folder, file_name):
        doc.layers.new('NEW')
        return True

# File won't be saved!
```

**Fix:** Always set `self.create_new = True` if modifying.

---

### 2. Modifying during iteration

```python
# Bad: Iterator breaks
for entity in doc.modelspace():
    if should_remove(entity):
        doc.modelspace().delete_entity(entity)

# Good: Collect first
to_remove = [e for e in doc.modelspace() if should_remove(e)]
for e in to_remove:
    doc.modelspace().delete_entity(e)
```

---

### 3. Sequence returns None

```python
def bad_custom(folder, filename):
    if condition:
        return "value"
    # Forgot else case - returns None

# Fix: Always return string
def good_custom(folder, filename):
    if condition:
        return "value"
    return ""  # Empty string, not None
```

---

## Architectural Decisions

### Why class-based operations?

- Better IDE support (autocomplete, type hints)
- Natural state management
- Familiar pattern for Python developers

### Why immutable sequences?

- Prevents accidental modification
- Safe reuse across operations
- Thread-safe by design

### Why single-threaded?

- DXF I/O is disk-bound, not CPU-bound
- ezdxf not fully thread-safe
- Simpler error handling

---

## Testing Approach

**What to test:**
- Sequence component behavior
- Operation `create_new` flags
- Find function predicates
- Backup creation/restoration

**How to test:**
- Mock ezdxf documents
- Temp directories for integration tests
- Edge cases: empty files, missing layers

---

## Conclusion

SnapMark's architecture:
- **Simple** - High-level API hides complexity
- **Extensible** - Clear extension points
- **Robust** - Graceful error handling
- **Composable** - Small operations combine well
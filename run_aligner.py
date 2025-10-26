"""
Example: automatic allignment of DXF files on a specific folder.
"""

import snapmark as sm

if __name__ == "__main__":
    folder_path = "Examples/Input"

    aligner = sm.Aligner()

    print(f"👉 Allignment files on: {folder_path}")
    sm.Operation.process_folder(folder_path, aligner)

    print("✅ Allignment complete.")

import os

# Static files
__all__ = []

# Include all files in the 'generated/' directory
generated_path = os.path.join(os.path.dirname(__file__))
print(f"GENERATEDPATH{generated_path}")
if os.path.exists(generated_path):
    __all__.extend(
        file[:-3]
        for file in os.listdir(generated_path)
        if file.endswith(".py") and file != "__init__.py"
    )
    for file in os.listdir(generated_path):
        if file.endswith(".py") and file != "__init__.py":
           print(file)

else:
    print("PATH NOT FOUND")
# Import all modules listed in __all__
from . import *  # This ensures everything in __all__ is available for import()
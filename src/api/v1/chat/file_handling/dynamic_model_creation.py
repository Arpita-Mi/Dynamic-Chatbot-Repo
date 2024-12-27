import sys
import importlib.util
import os
from logger.logger import logger , log_format


def replace_table_and_class_name(static_model_path, dynamic_model_path, organization_name):
    try:
        # Define the new file path
        new_file_path = f"{dynamic_model_path}/{organization_name}_model.py"
        
        # Ensure the directory exists
        if not os.path.exists(dynamic_model_path):
            os.makedirs(dynamic_model_path)
        
        # Read the content of the static model file
        with open(static_model_path, 'r') as file:
            content = file.read()
        logger.info(log_format(msg="file handling process for dynamic models"))
        
        # Replace the table name and class name
        new_table_name = f"{organization_name.lower()}_details"
        new_class_name = f"{organization_name.capitalize()}Details"
        content = content.replace("__tablename__ = 'incident_details'", f"__tablename__ = '{new_table_name}'")
        content = content.replace("class IncidentDetails(Base):", f"class {new_class_name}(Base):")
        logger.info(log_format(msg="replace the chatbot name in new file creation"))
        
        # Write the updated content to the new file
        with open(new_file_path, 'w') as file:
            file.write(content)
        logger.info(log_format(msg="File successfully created at:"))
        print(f"File successfully created at: {new_file_path}")
        return new_class_name

    except FileNotFoundError as e:
        logger.error(log_format(msg=f"Static model file not found : {e}",
                               file_path=static_model_path))
    except Exception as e:
        logger.error(log_format(msg=f"Unexpected error in replace_table_and_class_name : {e}"))



def register_dynamic_model(dynamic_model_class,new_file_path):
    """
    Dynamically add the new model to the Base metadata.
    """
    from database.base_model import Base
     
    module_name = os.path.splitext(os.path.basename(new_file_path))[0]
    sys.path.insert(0, os.path.dirname(new_file_path))
    module = importlib.import_module(module_name)
    sys.path.pop(0)
    dynamic_model_class = getattr(module, dynamic_model_class)
    if not hasattr(Base, '__model_registry__'):
        Base.__model_registry__ = set()
    Base.__model_registry__.add(dynamic_model_class)
    dynamic_model_class.metadata = Base.metadata
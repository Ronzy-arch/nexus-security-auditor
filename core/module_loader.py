import importlib
import inspect
from pathlib import Path
from core.base_module import BaseAuditModule


class ModuleLoader:
    def __init__(self, modules_dir="modules"):
        self.modules_dir = Path(modules_dir)

    def list_modules(self):
        # Mendaftar semua nama modul yang tersedia di folder modules
        modules = []
        if not self.modules_dir.exists():
            return modules
            
        for path in self.modules_dir.glob("*.py"):
            if path.name.startswith("__"):
                continue
            modules.append(path.stem)
        return modules

    def load_modules(self):
        # Memuat objek modul secara dinamis
        loaded_instances = []
        
        for module_name in self.list_modules():
            try:
                # Import file secara dinamis
                mod = importlib.import_module(f"modules.{module_name}")
                
                # Mencari kelas di dalam file yang merupakan turunan dari BaseAuditModule
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if issubclass(obj, BaseAuditModule) and obj is not BaseAuditModule:
                        loaded_instances.append(obj())
            except Exception as e:
                print(f"Gagal memuat modul {module_name}: {str(e)}")
                
        return loaded_instances

# Activación funcional de las clases de optimización

from optimusprime import (
    MemoryScrubbingOptimizer,
    CacheCoherencyOptimizer,
    MemoryBandwidthManager,
    AggressiveWriteCache,
    CustomIOScheduler,
    IOPriorityInheritance,
    MetadataOptimizer
)

class SystemOptimizationManager:
    """Gestor principal para coordinar todos los optimizadores"""
    
    def __init__(self):
        # Inicializar todos los optimizadores
        self.memory_scrubber = MemoryScrubbingOptimizer()
        self.cache_coherency = CacheCoherencyOptimizer()
        self.bandwidth_manager = MemoryBandwidthManager()
        self.write_cache = AggressiveWriteCache()
        self.io_scheduler = CustomIOScheduler()
        self.io_priority = IOPriorityInheritance()
        self.metadata_optimizer = MetadataOptimizer()
        
        # Estado de los optimizadores
        self.optimizers_active = False
        
    def initialize_all_optimizers(self):
        """Inicializa y activa todos los optimizadores del sistema"""
        try:
            print("[INFO] Iniciando activación de optimizadores...")
            
            # 1. Activar Memory Scrubbing Optimizer
            self.memory_scrubber.enable()
            self.memory_scrubber.set_scrubbing_interval(60)  # cada 60 segundos
            self.memory_scrubber.start_background_scrubbing()
            print("[✓] MemoryScrubbingOptimizer activado")
            
            # 2. Activar Cache Coherency Optimizer
            self.cache_coherency.enable()
            self.cache_coherency.set_coherency_protocol("MESI")
            self.cache_coherency.initialize_cache_lines()
            print("[✓] CacheCoherencyOptimizer activado")
            
            # 3. Activar Memory Bandwidth Manager
            self.bandwidth_manager.enable()
            self.bandwidth_manager.set_bandwidth_limit(80)  # 80% del ancho de banda
            self.bandwidth_manager.configure_qos_policies()
            print("[✓] MemoryBandwidthManager activado")
            
            # 4. Activar Aggressive Write Cache
            self.write_cache.enable()
            self.write_cache.set_cache_size(512 * 1024 * 1024)  # 512MB
            self.write_cache.set_write_policy("write-back")
            self.write_cache.start_cache_flush_daemon()
            print("[✓] AggressiveWriteCache activado")
            
            # 5. Activar Custom IO Scheduler
            self.io_scheduler.enable()
            self.io_scheduler.set_scheduling_algorithm("deadline")
            self.io_scheduler.set_queue_depth(256)
            self.io_scheduler.start_scheduling()
            print("[✓] CustomIOScheduler activado")
            
            # 6. Activar IO Priority Inheritance
            self.io_priority.enable()
            self.io_priority.set_priority_levels(5)
            self.io_priority.enable_priority_boosting()
            self.io_priority.configure_inheritance_chain()
            print("[✓] IOPriorityInheritance activado")
            
            # 7. Activar Metadata Optimizer
            self.metadata_optimizer.enable()
            self.metadata_optimizer.set_optimization_level("aggressive")
            self.metadata_optimizer.enable_metadata_caching()
            self.metadata_optimizer.start_optimization_engine()
            print("[✓] MetadataOptimizer activado")
            
            self.optimizers_active = True
            print("[SUCCESS] Todos los optimizadores han sido activados correctamente")
            
            # Configurar monitoreo
            self._setup_monitoring()
            
        except Exception as e:
            print(f"[ERROR] Fallo en la activación de optimizadores: {str(e)}")
            self.shutdown_all_optimizers()
            raise
    
    def _setup_monitoring(self):
        """Configura el monitoreo de rendimiento para los optimizadores"""
        import threading
        import time
        
        def monitor_performance():
            while self.optimizers_active:
                # Recolectar métricas de cada optimizador
                metrics = {
                    "memory_scrubbing": self.memory_scrubber.get_metrics(),
                    "cache_coherency": self.cache_coherency.get_metrics(),
                    "bandwidth_usage": self.bandwidth_manager.get_current_usage(),
                    "write_cache_hits": self.write_cache.get_hit_ratio(),
                    "io_queue_depth": self.io_scheduler.get_queue_status(),
                    "priority_inversions": self.io_priority.get_inversion_count(),
                    "metadata_optimizations": self.metadata_optimizer.get_optimization_count()
                }
                
                # Log métricas cada 30 segundos
                self._log_metrics(metrics)
                time.sleep(30)
        
        monitor_thread = threading.Thread(target=monitor_performance, daemon=True)
        monitor_thread.start()
    
    def _log_metrics(self, metrics):
        """Registra las métricas de rendimiento"""
        import json
        from datetime import datetime
        
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "metrics": metrics
        }
        
        # Guardar en archivo de log
        with open("optimizer_metrics.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def shutdown_all_optimizers(self):
        """Desactiva todos los optimizadores de manera segura"""
        print("[INFO] Desactivando optimizadores...")
        
        self.optimizers_active = False
        
        # Desactivar cada optimizador en orden inverso
        self.metadata_optimizer.disable()
        self.io_priority.disable()
        self.io_scheduler.stop_scheduling()
        self.write_cache.flush_and_disable()
        self.bandwidth_manager.disable()
        self.cache_coherency.disable()
        self.memory_scrubber.stop_background_scrubbing()
        
        print("[INFO] Todos los optimizadores han sido desactivados")

# Integración con el script principal
def integrate_optimizers_into_main_script():
    """Función para integrar los optimizadores en tu script principal"""
    
    # Localizar el punto de entrada principal del script
    # Asumiendo que tienes una función main() o similar
    
    # Crear instancia del gestor de optimización
    optimization_manager = SystemOptimizationManager()
    
    # Activar todos los optimizadores al inicio
    optimization_manager.initialize_all_optimizers()
    
    # Retornar el gestor para uso posterior
    return optimization_manager

# Hook de inicialización automática
def auto_init_hook():
    """Hook para inicialización automática al importar el módulo"""
    import atexit
    
    # Crear y activar el gestor global
    global GLOBAL_OPTIMIZER_MANAGER
    GLOBAL_OPTIMIZER_MANAGER = SystemOptimizationManager()
    GLOBAL_OPTIMIZER_MANAGER.initialize_all_optimizers()
    
    # Registrar limpieza al salir
    atexit.register(lambda: GLOBAL_OPTIMIZER_MANAGER.shutdown_all_optimizers())

# Ejemplo de uso en tu script principal
if __name__ == "__main__":
    # Opción 1: Inicialización manual
    optimizer_mgr = integrate_optimizers_into_main_script()
    
    # Tu código existente aquí...
    
    # Opción 2: Inicialización automática
    # Simplemente llama a auto_init_hook() al inicio de tu script
    # auto_init_hook()
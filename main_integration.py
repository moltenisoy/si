# Agregar esto al inicio de tu script principal (después de las definiciones de clase)

def initialize_system_optimizers():
    """Punto de entrada para inicializar todos los optimizadores"""
    
    print("=" * 60)
    print("SISTEMA DE OPTIMIZACIÓN AVANZADA")
    print("=" * 60)
    
    try:
        # Crear el gestor de optimización
        optimizer_manager = SystemOptimizationManager()
        
        # Activar todos los optimizadores
        optimizer_manager.initialize_all_optimizers()
        
        # Verificar estado
        if optimizer_manager.optimizers_active:
            print("\n[✓] Sistema de optimización completamente operacional")
            print("[i] Monitoreo activo en optimizer_metrics.log")
        
        return optimizer_manager
        
    except Exception as e:
        print(f"\n[✗] Error crítico en inicialización: {e}")
        return None

# Llamar esta función donde se inicializa tu sistema
# Por ejemplo, en tu función main() o al inicio del script
optimizer_manager = initialize_system_optimizers()
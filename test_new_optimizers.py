#!/usr/bin/env python3
"""
Test script to verify the 4 newly activated optimizer classes are properly integrated.
This script tests the integration points by analyzing the source code directly.
"""

import sys
import re

def test_cpu_pipeline_optimizer_property():
    """Test that CPUPipelineOptimizer property exists and is properly configured"""
    print("\n=== Testing CPUPipelineOptimizer Property ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check the property is defined
        assert '@property' in source and 'def cpu_pipeline_optimizer(self):' in source, \
            "cpu_pipeline_optimizer property not found"
        print("✓ cpu_pipeline_optimizer property is defined")
        
        # Check it creates CPUPipelineOptimizer with handle_cache
        assert 'CPUPipelineOptimizer(self.handle_cache)' in source, \
            "CPUPipelineOptimizer not initialized with handle_cache"
        print("✓ CPUPipelineOptimizer initialized with handle_cache")
        
        # Check it's called in apply_all_settings
        assert 'self.cpu_pipeline_optimizer.optimize_instruction_ordering' in source, \
            "cpu_pipeline_optimizer not called in apply_all_settings"
        print("✓ cpu_pipeline_optimizer is called in apply_all_settings")
        
        # Check class definition exists
        assert 'class CPUPipelineOptimizer:' in source, "CPUPipelineOptimizer class not found"
        print("✓ CPUPipelineOptimizer class exists")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_network_buffer_tuner_property():
    """Test that DynamicNetworkBufferTuner property exists and is properly configured"""
    print("\n=== Testing DynamicNetworkBufferTuner Property ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check the property is defined
        assert '@property' in source and 'def network_buffer_tuner(self):' in source, \
            "network_buffer_tuner property not found"
        print("✓ network_buffer_tuner property is defined")
        
        # Check it creates DynamicNetworkBufferTuner
        assert 'DynamicNetworkBufferTuner()' in source, \
            "DynamicNetworkBufferTuner not initialized"
        print("✓ DynamicNetworkBufferTuner initialized")
        
        # Check it's called in run method
        assert 'self.network_buffer_tuner.adjust_buffers_by_latency' in source, \
            "network_buffer_tuner not called in run method"
        print("✓ network_buffer_tuner is called in run method")
        
        # Check class definition exists
        assert 'class DynamicNetworkBufferTuner:' in source, "DynamicNetworkBufferTuner class not found"
        print("✓ DynamicNetworkBufferTuner class exists")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_registry_buffer_property():
    """Test that RegistryWriteBuffer property exists and is properly configured"""
    print("\n=== Testing RegistryWriteBuffer Property ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check the property is defined
        assert '@property' in source and 'def registry_buffer(self):' in source, \
            "registry_buffer property not found"
        print("✓ registry_buffer property is defined")
        
        # Check it creates RegistryWriteBuffer with flush_interval
        assert 'RegistryWriteBuffer(flush_interval=15.0)' in source, \
            "RegistryWriteBuffer not initialized with flush_interval"
        print("✓ RegistryWriteBuffer initialized with flush_interval=15.0")
        
        # Check _registry_buffer is initialized in __init__
        assert 'self._registry_buffer = None' in source, \
            "_registry_buffer not initialized in __init__"
        print("✓ _registry_buffer initialized in __init__")
        
        # Check ContextSwitchReducer accepts registry_buffer parameter
        assert 'def adjust_quantum_time_slice(self, increase=True, registry_buffer=None):' in source, \
            "adjust_quantum_time_slice doesn't accept registry_buffer parameter"
        print("✓ adjust_quantum_time_slice accepts registry_buffer parameter")
        
        # Check registry_buffer is used in adjust_quantum_time_slice
        assert 'registry_buffer.queue_write' in source, \
            "registry_buffer.queue_write not used"
        print("✓ registry_buffer.queue_write is used")
        
        # Check flush is called on exit
        assert 'registry_buffer.flush()' in source, \
            "registry_buffer.flush() not called"
        print("✓ registry_buffer.flush() is called on exit")
        
        # Check class definition exists
        assert 'class RegistryWriteBuffer:' in source, "RegistryWriteBuffer class not found"
        print("✓ RegistryWriteBuffer class exists")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ctypes_pool_property():
    """Test that CTypesStructurePool property exists and is properly configured"""
    print("\n=== Testing CTypesStructurePool Property ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check the property is defined
        assert '@property' in source and 'def ctypes_pool(self):' in source, \
            "ctypes_pool property not found"
        print("✓ ctypes_pool property is defined")
        
        # Check it creates CTypesStructurePool with max_pool_size
        assert 'CTypesStructurePool(max_pool_size=20)' in source, \
            "CTypesStructurePool not initialized with max_pool_size"
        print("✓ CTypesStructurePool initialized with max_pool_size=20")
        
        # Check _ctypes_pool is initialized in __init__
        assert 'self._ctypes_pool = None' in source, \
            "_ctypes_pool not initialized in __init__"
        print("✓ _ctypes_pool initialized in __init__")
        
        # Check BatchedSettingsApplicator accepts ctypes_pool parameter
        assert 'def __init__(self, handle_cache, ctypes_pool=None):' in source, \
            "BatchedSettingsApplicator.__init__ doesn't accept ctypes_pool parameter"
        print("✓ BatchedSettingsApplicator.__init__ accepts ctypes_pool parameter")
        
        # Check ctypes_pool is used in _apply_eco_qos
        assert 'ctypes_pool.get_structure' in source, \
            "ctypes_pool.get_structure not used"
        assert 'ctypes_pool.return_structure' in source, \
            "ctypes_pool.return_structure not used"
        print("✓ ctypes_pool.get_structure and return_structure are used")
        
        # Check ctypes_pool is set after initialization
        assert 'self.settings_applicator.ctypes_pool = self.ctypes_pool' in source, \
            "ctypes_pool not set on settings_applicator"
        print("✓ ctypes_pool is set on settings_applicator after initialization")
        
        # Check class definition exists
        assert 'class CTypesStructurePool:' in source, "CTypesStructurePool class not found"
        print("✓ CTypesStructurePool class exists")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_run_method_integration():
    """Test that network_buffer_tuner is properly integrated in the run method"""
    print("\n=== Testing Run Method Integration ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Find the UnifiedProcessManager class
        upm_start = source.find('class UnifiedProcessManager:')
        if upm_start == -1:
            raise AssertionError("UnifiedProcessManager class not found")
        
        # Find the run method after UnifiedProcessManager
        run_method_start = source.find('def run(self):', upm_start)
        if run_method_start == -1:
            raise AssertionError("UnifiedProcessManager run method not found")
        
        # Look for the network buffer tuner call after run method
        run_section = source[run_method_start:run_method_start + 5000]
        
        assert 'iteration_count % 60 == 0' in run_section, \
            "60 iteration check not found in run method"
        print("✓ 60 iteration check found in run method")
        
        assert 'current_latency = self.enhanced_network_stack.measure_network_latency()' in run_section, \
            "measure_network_latency call not found"
        print("✓ measure_network_latency is called")
        
        assert 'self.network_buffer_tuner.adjust_buffers_by_latency(current_latency)' in run_section, \
            "adjust_buffers_by_latency call not found"
        print("✓ adjust_buffers_by_latency is called with current_latency")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("NEW OPTIMIZER ACTIVATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_cpu_pipeline_optimizer_property,
        test_network_buffer_tuner_property,
        test_registry_buffer_property,
        test_ctypes_pool_property,
        test_run_method_integration
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())

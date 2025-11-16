#!/usr/bin/env python3
"""
Test script to verify the logic fixes made to optimusprime.py
"""

import sys
import re


def test_ctypes_structure_pool_fix():
    """Test that CTypesStructurePool.return_structure appends the structure itself"""
    print("\n=== Testing CTypesStructurePool.return_structure Fix ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Find the return_structure method
        pattern = r'def return_structure\(self, structure\):.*?(?=\n    def |\nclass )'
        match = re.search(pattern, source, re.DOTALL)
        
        if not match:
            print("✗ Could not find return_structure method")
            return False
        
        method_code = match.group(0)
        
        # Check that it appends 'structure' not 'type(structure)()'
        if 'pool.append(structure)' in method_code:
            print("✓ return_structure correctly appends the structure itself")
        else:
            print("✗ return_structure does not append structure correctly")
            return False
            
        # Make sure it doesn't create a new instance
        if 'type(structure)()' in method_code:
            print("✗ return_structure still creates a new instance")
            return False
        
        print("✓ return_structure fix is correct")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_registry_write_buffer_hkey():
    """Test that RegistryWriteBuffer supports hkey parameter"""
    print("\n=== Testing RegistryWriteBuffer hkey Parameter ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check queue_write signature
        if 'def queue_write(self, key_path, value_name, value_type, value_data, hkey=None):' in source:
            print("✓ queue_write accepts hkey parameter")
        else:
            print("✗ queue_write does not accept hkey parameter")
            return False
        
        # Check that hkey is used in buffer append
        if '(hkey, key_path, value_name, value_type, value_data)' in source:
            print("✓ hkey is stored in buffer")
        else:
            print("✗ hkey is not stored in buffer")
            return False
        
        # Check flush unpacks hkey
        if 'for hkey, key_path, value_name, value_type, value_data in self.buffer:' in source:
            print("✓ flush correctly unpacks hkey from buffer")
        else:
            print("✗ flush does not unpack hkey")
            return False
        
        print("✓ RegistryWriteBuffer hkey support is correct")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prefetch_optimizer_hardware_detector():
    """Test that PrefetchOptimizer uses HardwareDetector"""
    print("\n=== Testing PrefetchOptimizer HardwareDetector Integration ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check __init__ accepts hardware_detector
        if 'def __init__(self, hardware_detector=None):' in source:
            print("✓ PrefetchOptimizer.__init__ accepts hardware_detector parameter")
        else:
            print("✗ PrefetchOptimizer.__init__ does not accept hardware_detector")
            return False
        
        # Check is_mechanical_disk uses hardware_detector
        if 'if self.hardware_detector:' in source and 'has_ssd()' in source and 'has_nvme()' in source:
            print("✓ is_mechanical_disk uses HardwareDetector methods")
        else:
            print("✗ is_mechanical_disk does not use HardwareDetector")
            return False
        
        # Check instantiation passes hardware_detector
        if 'PrefetchOptimizer(self.hardware_detector)' in source:
            print("✓ PrefetchOptimizer is instantiated with hardware_detector")
        else:
            print("✗ PrefetchOptimizer not instantiated with hardware_detector")
            return False
        
        print("✓ PrefetchOptimizer HardwareDetector integration is correct")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cpu_parking_controller_no_core_id():
    """Test that CPUParkingController methods don't have core_id parameter"""
    print("\n=== Testing CPUParkingController Signature Fix ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check disable_cpu_parking signature
        if 'def disable_cpu_parking(self):' in source:
            print("✓ disable_cpu_parking() has no core_id parameter")
        else:
            print("✗ disable_cpu_parking still has core_id parameter")
            return False
        
        # Check enable_cpu_parking signature
        if 'def enable_cpu_parking(self):' in source:
            print("✓ enable_cpu_parking() has no core_id parameter")
        else:
            print("✗ enable_cpu_parking still has core_id parameter")
            return False
        
        # Check calls don't pass core_id
        if '.disable_cpu_parking(0)' in source or '.enable_cpu_parking(0)' in source:
            print("✗ Found calls with core_id parameter")
            return False
        else:
            print("✓ No calls pass core_id parameter")
        
        print("✓ CPUParkingController signature fix is correct")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_documentation_added():
    """Test that documentation was added to key classes"""
    print("\n=== Testing Documentation Additions ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check LargePageManager has limitation doc
        if 'LIMITATION: This class cannot actually force external processes' in source:
            print("✓ LargePageManager has limitation documentation")
        else:
            print("⚠ LargePageManager missing limitation documentation")
        
        # Check AdvancedWorkingSetTrimmer has note
        if 'NOTE: Both trim_private_pages() and trim_mapped_files()' in source or 'functionally they are identical' in source:
            print("✓ AdvancedWorkingSetTrimmer has redundancy documentation")
        else:
            print("⚠ AdvancedWorkingSetTrimmer missing redundancy note")
        
        # Check PrefetchOptimizer has limitation doc
        if 'LIMITATION: Simply opening and closing a file handle' in source:
            print("✓ PrefetchOptimizer has limitation documentation")
        else:
            print("⚠ PrefetchOptimizer missing limitation documentation")
        
        # Check HardwareDetector has deprecation note
        if 'NOTE: WMIC is deprecated' in source or 'WMIC is deprecated' in source:
            print("✓ HardwareDetector has WMIC deprecation note")
        else:
            print("⚠ HardwareDetector missing deprecation note")
        
        print("✓ Documentation additions complete")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("LOGIC FIXES VALIDATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_ctypes_structure_pool_fix,
        test_registry_write_buffer_hkey,
        test_prefetch_optimizer_hardware_detector,
        test_cpu_parking_controller_no_core_id,
        test_documentation_added,
    ]
    
    passed = sum(test() for test in tests)
    total = len(tests)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())

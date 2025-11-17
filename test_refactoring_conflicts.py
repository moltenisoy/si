#!/usr/bin/env python3
"""
Test script to verify the refactoring of critical logic conflicts.
This script tests that the Single Source of Truth principle is properly enforced.
"""

import sys
import re

def test_large_system_cache_conflict_resolution():
    """Test that LargeSystemCache conflict is resolved"""
    print("\n=== Testing LargeSystemCache Conflict Resolution ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all occurrences of LargeSystemCache writes
        large_cache_pattern = r'winreg\.SetValueEx\([^,]+,\s*["\']LargeSystemCache["\']\s*,\s*0\s*,\s*winreg\.REG_DWORD\s*,'
        matches = list(re.finditer(large_cache_pattern, content))
        
        print(f"  Found {len(matches)} LargeSystemCache write operations")
        
        # Check that AggressiveWriteCache.optimize_write_cache_for_gaming does NOT set LargeSystemCache
        aggressive_cache_start = content.find('class AggressiveWriteCache:')
        aggressive_cache_end = content.find('\nclass ', aggressive_cache_start + 1)
        aggressive_cache_section = content[aggressive_cache_start:aggressive_cache_end]
        
        gaming_method_start = aggressive_cache_section.find('def optimize_write_cache_for_gaming')
        gaming_method_end = aggressive_cache_section.find('\n    def ', gaming_method_start + 1)
        if gaming_method_end == -1:
            gaming_method_end = aggressive_cache_section.find('\nclass ', gaming_method_start)
        gaming_method = aggressive_cache_section[gaming_method_start:gaming_method_end]
        
        assert 'LargeSystemCache' not in gaming_method, \
            "AggressiveWriteCache.optimize_write_cache_for_gaming should NOT set LargeSystemCache"
        print("✓ AggressiveWriteCache.optimize_write_cache_for_gaming does NOT set LargeSystemCache")
        
        # Check that AdvancedFileSystemCache.optimize_cache_for_gaming DOES set LargeSystemCache to 0
        adv_cache_start = content.find('class AdvancedFileSystemCache:')
        adv_cache_end = content.find('\nclass ', adv_cache_start + 1)
        adv_cache_section = content[adv_cache_start:adv_cache_end]
        
        assert 'LargeSystemCache' in adv_cache_section, \
            "AdvancedFileSystemCache should set LargeSystemCache"
        assert re.search(r'LargeSystemCache["\'],\s*0\s*,\s*winreg\.REG_DWORD\s*,\s*0', adv_cache_section), \
            "AdvancedFileSystemCache should set LargeSystemCache to 0"
        print("✓ AdvancedFileSystemCache.optimize_cache_for_gaming sets LargeSystemCache to 0")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tcp_window_size_conflict_resolution():
    """Test that TcpWindowSize conflict is resolved"""
    print("\n=== Testing TcpWindowSize Conflict Resolution ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all occurrences of TcpWindowSize writes
        tcp_window_pattern = r'winreg\.SetValueEx\([^,]+,\s*["\']TcpWindowSize["\']\s*,\s*0\s*,\s*winreg\.REG_DWORD\s*,'
        matches = list(re.finditer(tcp_window_pattern, content))
        
        print(f"  Found {len(matches)} TcpWindowSize write operations")
        
        # Check that NetworkOptimizer.optimize_tcp_window_scaling does NOT set TcpWindowSize
        network_opt_start = content.find('class NetworkOptimizer:')
        network_opt_end = content.find('\nclass ', network_opt_start + 1)
        network_opt_section = content[network_opt_start:network_opt_end]
        
        tcp_method_start = network_opt_section.find('def optimize_tcp_window_scaling')
        tcp_method_end = network_opt_section.find('\n    def ', tcp_method_start + 1)
        tcp_method = network_opt_section[tcp_method_start:tcp_method_end]
        
        assert 'TcpWindowSize' not in tcp_method, \
            "NetworkOptimizer.optimize_tcp_window_scaling should NOT set TcpWindowSize"
        print("✓ NetworkOptimizer.optimize_tcp_window_scaling does NOT set TcpWindowSize")
        
        # Check that DynamicNetworkBufferTuner.adjust_buffers_by_latency does NOT set TcpWindowSize
        buffer_tuner_start = content.find('class DynamicNetworkBufferTuner:')
        buffer_tuner_end = content.find('\nclass ', buffer_tuner_start + 1)
        buffer_tuner_section = content[buffer_tuner_start:buffer_tuner_end]
        
        adjust_method_start = buffer_tuner_section.find('def adjust_buffers_by_latency')
        adjust_method_end = buffer_tuner_section.find('\n    def ', adjust_method_start + 1)
        if adjust_method_end == -1:
            adjust_method_end = buffer_tuner_section.find('\nclass ', adjust_method_start)
        adjust_method = buffer_tuner_section[adjust_method_start:adjust_method_end]
        
        assert 'TcpWindowSize' not in adjust_method, \
            "DynamicNetworkBufferTuner.adjust_buffers_by_latency should NOT set TcpWindowSize"
        print("✓ DynamicNetworkBufferTuner.adjust_buffers_by_latency does NOT set TcpWindowSize")
        
        # Check that EnhancedNetworkStackOptimizer.adjust_tcp_window_scaling DOES set TcpWindowSize
        enhanced_start = content.find('class EnhancedNetworkStackOptimizer:')
        enhanced_end = content.find('\nclass ', enhanced_start + 1)
        enhanced_section = content[enhanced_start:enhanced_end]
        
        enhanced_method_start = enhanced_section.find('def adjust_tcp_window_scaling')
        enhanced_method_end = enhanced_section.find('\n    def ', enhanced_method_start + 1)
        enhanced_method = enhanced_section[enhanced_method_start:enhanced_method_end]
        
        assert 'TcpWindowSize' in enhanced_method, \
            "EnhancedNetworkStackOptimizer.adjust_tcp_window_scaling should set TcpWindowSize"
        print("✓ EnhancedNetworkStackOptimizer.adjust_tcp_window_scaling sets TcpWindowSize")
        
        # Verify only one class writes TcpWindowSize
        assert len(matches) == 1, \
            f"Expected exactly 1 TcpWindowSize write operation, found {len(matches)}"
        print("✓ Only one class (EnhancedNetworkStackOptimizer) writes TcpWindowSize")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_responsiveness_conflict_resolution():
    """Test that SystemResponsiveness conflict is resolved"""
    print("\n=== Testing SystemResponsiveness Conflict Resolution ===")
    try:
        with open('/home/runner/work/si/si/optimusprime.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all occurrences of SystemResponsiveness writes
        resp_pattern = r'winreg\.SetValueEx\([^,]+,\s*["\']SystemResponsiveness["\']\s*,\s*0\s*,\s*winreg\.REG_DWORD\s*,'
        matches = list(re.finditer(resp_pattern, content))
        
        print(f"  Found {len(matches)} SystemResponsiveness write operations")
        
        # Check that KernelOptimizer.optimize_timer_resolution does NOT set SystemResponsiveness
        kernel_opt_start = content.find('class KernelOptimizer:')
        kernel_opt_end = content.find('\nclass ', kernel_opt_start + 1)
        kernel_opt_section = content[kernel_opt_start:kernel_opt_end]
        
        timer_method_start = kernel_opt_section.find('def optimize_timer_resolution')
        timer_method_end = kernel_opt_section.find('\n    def ', timer_method_start + 1)
        timer_method = kernel_opt_section[timer_method_start:timer_method_end]
        
        assert 'SystemResponsiveness' not in timer_method, \
            "KernelOptimizer.optimize_timer_resolution should NOT set SystemResponsiveness"
        print("✓ KernelOptimizer.optimize_timer_resolution does NOT set SystemResponsiveness")
        
        # Check that SystemResponsivenessController still has the functionality
        resp_controller_start = content.find('class SystemResponsivenessController:')
        resp_controller_end = content.find('\nclass ', resp_controller_start + 1)
        resp_controller_section = content[resp_controller_start:resp_controller_end]
        
        assert 'SystemResponsiveness' in resp_controller_section, \
            "SystemResponsivenessController should still set SystemResponsiveness"
        print("✓ SystemResponsivenessController retains SystemResponsiveness management")
        
        # Check that EnhancedSystemResponsivenessOptimizer has the functionality
        enhanced_resp_start = content.find('class EnhancedSystemResponsivenessOptimizer:')
        enhanced_resp_end = content.find('\nclass ', enhanced_resp_start + 1)
        enhanced_resp_section = content[enhanced_resp_start:enhanced_resp_end]
        
        assert 'SystemResponsiveness' in enhanced_resp_section, \
            "EnhancedSystemResponsivenessOptimizer should set SystemResponsiveness"
        print("✓ EnhancedSystemResponsivenessOptimizer retains SystemResponsiveness management")
        
        # Verify exactly two classes write SystemResponsiveness (SystemResponsivenessController and EnhancedSystemResponsivenessOptimizer)
        assert len(matches) == 2, \
            f"Expected exactly 2 SystemResponsiveness write operations, found {len(matches)}"
        print("✓ Exactly two classes manage SystemResponsiveness (SystemResponsivenessController and EnhancedSystemResponsivenessOptimizer)")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("REFACTORING CONFLICT RESOLUTION TEST SUITE")
    print("=" * 60)
    
    results = []
    results.append(("LargeSystemCache Conflict", test_large_system_cache_conflict_resolution()))
    results.append(("TcpWindowSize Conflict", test_tcp_window_size_conflict_resolution()))
    results.append(("SystemResponsiveness Conflict", test_system_responsiveness_conflict_resolution()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print()
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

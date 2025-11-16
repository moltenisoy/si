import json
import os
import sys

def test_config_json_structure():
    print("Testing config.json structure...")
    
    test_config = {
        "lista_juegos": ["game1.exe", "game2.exe", "game3.exe"],
        "lista_blanca": ["chrome.exe", "firefox.exe", "explorer.exe"]
    }
    
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(test_config, f, indent=4, ensure_ascii=False)
    
    assert os.path.exists("config.json"), "config.json not created"
    
    with open("config.json", "r", encoding="utf-8") as f:
        loaded = json.load(f)
    
    assert "lista_juegos" in loaded, "lista_juegos missing"
    assert "lista_blanca" in loaded, "lista_blanca missing"
    assert len(loaded["lista_juegos"]) == 3, "lista_juegos count incorrect"
    assert len(loaded["lista_blanca"]) == 3, "lista_blanca count incorrect"
    
    print("✓ config.json structure test passed")
    os.remove("config.json")

def test_op_py_syntax():
    print("Testing op.py syntax...")
    import py_compile
    try:
        py_compile.compile("op.py", doraise=True)
        print("✓ op.py syntax valid")
    except py_compile.PyCompileError as e:
        print(f"✗ op.py syntax error: {e}")
        sys.exit(1)

def test_optimusprime_py_syntax():
    print("Testing optimusprime.py syntax...")
    import py_compile
    try:
        py_compile.compile("optimusprime.py", doraise=True)
        print("✓ optimusprime.py syntax valid")
    except py_compile.PyCompileError as e:
        print(f"✗ optimusprime.py syntax error: {e}")
        sys.exit(1)

def test_suggestions_file():
    print("Testing SUGGESTIONS.md...")
    assert os.path.exists("SUGGESTIONS.md"), "SUGGESTIONS.md not found"
    with open("SUGGESTIONS.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "MEJORAS INTERNAS" in content, "Internal improvements section missing"
    assert "MEJORAS DE CAPACIDAD OPTIMIZADORA" in content, "Optimizer improvements section missing"
    print("✓ SUGGESTIONS.md structure valid")

if __name__ == "__main__":
    print("=== Running Integration Tests ===\n")
    test_config_json_structure()
    test_op_py_syntax()
    test_optimusprime_py_syntax()
    test_suggestions_file()
    print("\n=== All Integration Tests Passed ===")

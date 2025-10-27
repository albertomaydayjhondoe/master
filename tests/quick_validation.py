"""
🧪 Test Rápido - Validación Sistema Meta Ads €400
Test simplificado sin dependencias externas
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

class QuickTester:
    """Test rápido del sistema sin servicios externos"""
    
    def __init__(self):
        self.test_results = {}
        
    def run_quick_validation(self):
        """Ejecutar validación rápida del sistema"""
        
        print("🧪 Meta Ads €400 Quick Validation")
        print("=" * 50)
        
        tests = [
            ("File Structure", self.test_file_structure),
            ("Configuration Files", self.test_configuration_files),
            ("Landing Page Templates", self.test_landing_page_templates),
            ("ML Models Structure", self.test_ml_models_structure),
            ("Railway Configuration", self.test_railway_configuration),
            ("Dashboard Components", self.test_dashboard_components),
            ("UTM Tracking Setup", self.test_utm_tracking_setup),
            ("Authorization System", self.test_authorization_system)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}...")
            print("-" * 30)
            
            try:
                result = test_func()
                if result:
                    print(f"✅ {test_name}: PASS")
                    passed_tests += 1
                else:
                    print(f"❌ {test_name}: FAIL")
                    
                self.test_results[test_name] = result
                
            except Exception as e:
                print(f"⚠️ {test_name}: ERROR - {str(e)}")
                self.test_results[test_name] = False
        
        # Reporte final
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 50)
        print("📊 QUICK VALIDATION RESULTS")
        print("=" * 50)
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        
        if success_rate >= 80:
            print("\n🎉 SYSTEM STRUCTURE VALIDATED!")
            print("✅ Ready for service startup and testing")
        else:
            print("\n⚠️ SYSTEM NEEDS ATTENTION")
            print("❌ Some components missing or misconfigured")
        
        return success_rate >= 80
    
    def test_file_structure(self) -> bool:
        """Test 1: Verificar estructura de archivos"""
        
        required_files = [
            "v2/meta_ads_400/complete_workflow.py",
            "v2/landing_pages/landing_generator.py", 
            "v2/unified_orchestrator/main.py",
            "dashboard_meta_centric.py",
            "dashboard_ml_authorization.py",
            "ml_core/api/endpoints/meta_centric_analysis.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
            else:
                print(f"  ✅ {file_path}")
        
        if missing_files:
            print(f"  ❌ Missing files: {missing_files}")
            return False
        
        print(f"  📊 All {len(required_files)} core files present")
        return True
    
    def test_configuration_files(self) -> bool:
        """Test 2: Verificar archivos de configuración"""
        
        config_files = [
            "railway.json",
            "Procfile", 
            "docker/Dockerfile.railway",
            "requirements.txt",
            "requirements-dummy.txt"
        ]
        
        present_files = []
        for config_file in config_files:
            if os.path.exists(config_file):
                present_files.append(config_file)
                print(f"  ✅ {config_file}")
            else:
                print(f"  ⚠️ Missing: {config_file}")
        
        success_rate = len(present_files) / len(config_files)
        print(f"  📊 Configuration files: {success_rate:.1%}")
        
        return success_rate >= 0.8
    
    def test_landing_page_templates(self) -> bool:
        """Test 3: Verificar templates de landing pages"""
        
        # Verificar que el landing generator tiene templates
        landing_generator_file = "v2/landing_pages/landing_generator.py"
        
        if os.path.exists(landing_generator_file):
            with open(landing_generator_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Verificar componentes clave
                required_components = [
                    "LandingPageGenerator",
                    "UTMTrackingData", 
                    "music_template",
                    "utm_params",
                    "/api/utm/track"
                ]
                
                present_components = []
                for component in required_components:
                    if component in content:
                        present_components.append(component)
                        print(f"  ✅ {component}")
                    else:
                        print(f"  ❌ Missing: {component}")
                
                success_rate = len(present_components) / len(required_components)
                print(f"  📊 Template components: {success_rate:.1%}")
                
                return success_rate >= 0.8
        else:
            print(f"  ❌ Landing generator file not found")
            return False
    
    def test_ml_models_structure(self) -> bool:
        """Test 4: Verificar estructura de modelos ML"""
        
        ml_components = [
            "ml_core/api/endpoints/meta_centric_analysis.py",
            "ml_core/models/factory.py",
            "config/ml/model_config.yaml"
        ]
        
        present_components = []
        for component in ml_components:
            if os.path.exists(component):
                present_components.append(component)
                print(f"  ✅ {component}")
            else:
                print(f"  ⚠️ Missing: {component}")
        
        # Verificar que dummy mode está configurado
        config_file = "config/app_settings.py"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
                if "DUMMY_MODE" in content:
                    print(f"  ✅ DUMMY_MODE configured")
                    present_components.append("dummy_mode")
        
        success_rate = len(present_components) / (len(ml_components) + 1)
        print(f"  📊 ML components: {success_rate:.1%}")
        
        return success_rate >= 0.7
    
    def test_railway_configuration(self) -> bool:
        """Test 5: Verificar configuración Railway"""
        
        # Verificar railway.json
        if os.path.exists("railway.json"):
            try:
                with open("railway.json", 'r') as f:
                    railway_config = json.load(f)
                
                # Verificar estructura básica
                required_sections = ["build", "deploy", "environments"]
                present_sections = []
                
                for section in required_sections:
                    if section in railway_config:
                        present_sections.append(section)
                        print(f"  ✅ railway.json[{section}]")
                    else:
                        print(f"  ❌ Missing: railway.json[{section}]")
                
                # Verificar Procfile
                if os.path.exists("Procfile"):
                    with open("Procfile", 'r') as f:
                        procfile_content = f.read()
                        
                    if "web:" in procfile_content and "uvicorn" in procfile_content:
                        print(f"  ✅ Procfile configured")
                        present_sections.append("procfile")
                    else:
                        print(f"  ❌ Procfile misconfigured")
                
                success_rate = len(present_sections) / (len(required_sections) + 1)
                print(f"  📊 Railway config: {success_rate:.1%}")
                
                return success_rate >= 0.8
                
            except json.JSONDecodeError:
                print(f"  ❌ railway.json invalid JSON")
                return False
        else:
            print(f"  ❌ railway.json not found")
            return False
    
    def test_dashboard_components(self) -> bool:
        """Test 6: Verificar componentes de dashboard"""
        
        dashboard_files = [
            "dashboard_meta_centric.py",
            "dashboard_ml_authorization.py"
        ]
        
        working_dashboards = []
        
        for dashboard_file in dashboard_files:
            if os.path.exists(dashboard_file):
                with open(dashboard_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Verificar componentes Streamlit
                    if "streamlit" in content and "st." in content:
                        print(f"  ✅ {dashboard_file}: Streamlit configured")
                        working_dashboards.append(dashboard_file)
                    else:
                        print(f"  ⚠️ {dashboard_file}: Missing Streamlit components")
            else:
                print(f"  ❌ Missing: {dashboard_file}")
        
        success_rate = len(working_dashboards) / len(dashboard_files)
        print(f"  📊 Dashboard components: {success_rate:.1%}")
        
        return success_rate >= 0.5  # Al menos un dashboard funcionando
    
    def test_utm_tracking_setup(self) -> bool:
        """Test 7: Verificar configuración UTM tracking"""
        
        landing_generator = "v2/landing_pages/landing_generator.py"
        
        if os.path.exists(landing_generator):
            with open(landing_generator, 'r', encoding='utf-8') as f:
                content = f.read()
                
                utm_components = [
                    "/api/utm/track",
                    "/api/utm/convert", 
                    "UTMTrackingData",
                    "utm_params",
                    "track_conversion"
                ]
                
                present_utm = []
                for component in utm_components:
                    if component in content:
                        present_utm.append(component)
                        print(f"  ✅ {component}")
                    else:
                        print(f"  ⚠️ Missing: {component}")
                
                success_rate = len(present_utm) / len(utm_components)
                print(f"  📊 UTM tracking: {success_rate:.1%}")
                
                return success_rate >= 0.8
        else:
            print(f"  ❌ Landing generator not found")
            return False
    
    def test_authorization_system(self) -> bool:
        """Test 8: Verificar sistema de autorización"""
        
        auth_dashboard = "dashboard_ml_authorization.py"
        
        if os.path.exists(auth_dashboard):
            with open(auth_dashboard, 'r', encoding='utf-8') as f:
                content = f.read()
                
                auth_components = [
                    "get_pending_authorizations",
                    "approve_authorization",
                    "MLAuthorizationRequest",
                    "auto_approve_under_euros",
                    "Autorizaciones Pendientes"
                ]
                
                present_auth = []
                for component in auth_components:
                    if component in content:
                        present_auth.append(component)
                        print(f"  ✅ {component}")
                    else:
                        print(f"  ⚠️ Missing: {component}")
                
                success_rate = len(present_auth) / len(auth_components)
                print(f"  📊 Authorization system: {success_rate:.1%}")
                
                return success_rate >= 0.8
        else:
            print(f"  ❌ Authorization dashboard not found")
            return False

def main():
    """Ejecutar validación rápida"""
    
    print("🎯 Quick validation without external dependencies")
    print("⚡ Checking system structure and configuration")
    print("")
    
    tester = QuickTester()
    is_ready = tester.run_quick_validation()
    
    print("\n" + "=" * 50)
    
    if is_ready:
        print("🎉 SYSTEM VALIDATION PASSED!")
        print("")
        print("✅ Core structure validated")
        print("✅ Configuration files present")  
        print("✅ Components properly structured")
        print("")
        print("🚀 READY FOR API CONFIGURATION!")
        print("")
        
        return True
    else:
        print("⚠️ SYSTEM NEEDS FIXES")
        print("")
        print("❌ Some components missing or misconfigured")
        print("🔧 Please check the failed tests above")
        print("")
        
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
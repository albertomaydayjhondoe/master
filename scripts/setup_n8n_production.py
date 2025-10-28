#!/usr/bin/env python3
"""
🔄 n8n Production Setup - All 4 Workflows Active
Complete workflow automation for Stakas MVP viral system
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, List

class N8nProductionSetup:
    """Setup complete n8n workflows for production"""
    
    def __init__(self):
        self.n8n_url = "http://localhost:5678"
        self.workflows_dir = Path(__file__).parent.parent / "orchestration" / "n8n_workflows"
        self.workflows = [
            "main_orchestrator.json",
            "ml_decision_engine.json", 
            "device_farm_trigger.json",
            "meta_ads_orchestrator.json"
        ]
        
    def check_n8n_status(self) -> bool:
        """Check if n8n is running"""
        try:
            response = requests.get(f"{self.n8n_url}/healthz", timeout=5)
            if response.status_code == 200:
                print("✅ n8n is running")
                return True
            else:
                print(f"❌ n8n responded with status {response.status_code}")
                return False
        except requests.ConnectionError:
            print("❌ n8n is not running. Please start n8n first.")
            print("👉 Run: docker run -p 5678:5678 n8nio/n8n")
            return False
        except Exception as e:
            print(f"❌ Error checking n8n: {e}")
            return False
    
    def load_workflow(self, workflow_file: str) -> Dict:
        """Load workflow from JSON file"""
        file_path = self.workflows_dir / workflow_file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            print(f"📋 Loaded workflow: {workflow_file}")
            return workflow_data
        except FileNotFoundError:
            print(f"❌ Workflow file not found: {workflow_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {workflow_file}: {e}")
            return {}
    
    def create_workflow(self, workflow_data: Dict) -> Dict:
        """Create workflow in n8n"""
        try:
            # Create workflow
            response = requests.post(
                f"{self.n8n_url}/rest/workflows",
                json=workflow_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Created workflow: {workflow_data.get('name', 'Unknown')}")
                return result
            else:
                print(f"❌ Failed to create workflow: {response.status_code}")
                print(f"   Response: {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error creating workflow: {e}")
            return {}
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate workflow in n8n"""
        try:
            response = requests.patch(
                f"{self.n8n_url}/rest/workflows/{workflow_id}/activate",
                json={"active": True},
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"✅ Activated workflow ID: {workflow_id}")
                return True
            else:
                print(f"❌ Failed to activate workflow {workflow_id}: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error activating workflow {workflow_id}: {e}")
            return False
    
    def setup_all_workflows(self) -> Dict[str, str]:
        """Setup and activate all 4 workflows"""
        workflow_ids = {}
        
        print("🔄 Setting up n8n workflows for production...")
        
        for workflow_file in self.workflows:
            print(f"\n📋 Processing: {workflow_file}")
            
            # Load workflow
            workflow_data = self.load_workflow(workflow_file)
            if not workflow_data:
                continue
            
            # Create workflow
            created_workflow = self.create_workflow(workflow_data)
            if not created_workflow:
                continue
            
            workflow_id = created_workflow.get('id')
            if workflow_id:
                workflow_ids[workflow_file] = workflow_id
                
                # Activate workflow
                self.activate_workflow(workflow_id)
                
                # Small delay between workflows
                time.sleep(2)
        
        return workflow_ids
    
    def create_production_webhooks(self) -> Dict[str, str]:
        """Create production webhooks for system integration"""
        webhooks = {
            'launch_campaign': '/webhook/launch-campaign',
            'ml_analysis': '/webhook/ml-analysis',
            'device_farm_trigger': '/webhook/device-farm',
            'meta_ads_callback': '/webhook/meta-ads-callback'
        }
        
        print("\n🔗 Production webhooks configured:")
        for name, endpoint in webhooks.items():
            full_url = f"{self.n8n_url}{endpoint}"
            print(f"   {name}: {full_url}")
        
        return webhooks
    
    def verify_setup(self, workflow_ids: Dict) -> bool:
        """Verify all workflows are active and working"""
        print("\n🔍 Verifying n8n setup...")
        
        try:
            # Get all workflows
            response = requests.get(f"{self.n8n_url}/rest/workflows", timeout=10)
            if response.status_code != 200:
                print("❌ Failed to get workflows list")
                return False
            
            workflows = response.json()
            active_count = 0
            
            for workflow in workflows:
                if workflow.get('active', False):
                    active_count += 1
                    print(f"   ✅ {workflow.get('name', 'Unknown')} - ACTIVE")
                else:
                    print(f"   ⚠️ {workflow.get('name', 'Unknown')} - INACTIVE")
            
            print(f"\n📊 Active workflows: {active_count}/{len(workflows)}")
            return active_count >= len(self.workflows)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error verifying setup: {e}")
            return False
    
    def run_production_setup(self) -> bool:
        """Run complete n8n production setup"""
        print("🚀 N8N PRODUCTION SETUP - STAKAS MVP")
        print("="*50)
        
        # Step 1: Check n8n status
        if not self.check_n8n_status():
            return False
        
        # Step 2: Setup workflows
        workflow_ids = self.setup_all_workflows()
        
        if not workflow_ids:
            print("❌ No workflows were created")
            return False
        
        # Step 3: Setup webhooks
        webhooks = self.create_production_webhooks()
        
        # Step 4: Verify setup
        success = self.verify_setup(workflow_ids)
        
        if success:
            print("\n✅ N8N PRODUCTION SETUP COMPLETE!")
            print(f"📊 {len(workflow_ids)} workflows active")
            print(f"🔗 {len(webhooks)} webhooks configured")
            print("🎯 System ready for Stakas MVP campaigns")
        else:
            print("\n❌ Setup completed with errors")
        
        return success

def main():
    """Main entry point"""
    setup = N8nProductionSetup()
    success = setup.run_production_setup()
    
    if success:
        print("\n🎵 Ready to make Stakas go viral! 🚀")
        return 0
    else:
        print("\n💥 Setup failed - check n8n installation")
        return 1

if __name__ == "__main__":
    exit(main())
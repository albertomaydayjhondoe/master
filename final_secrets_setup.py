#!/usr/bin/env python3
"""
🚀 Auto-configurador Final de Secrets para Stakas MVP
Configura automáticamente todos los secrets necesarios
"""

import subprocess
import sys
import webbrowser

def main():
    print("🚀 STAKAS MVP - AUTO CONFIGURADOR DE SECRETS")
    print("📺 Repo: albertomaydayjhondoe/master")
    print("🎵 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
    print("=" * 60)
    
    # Secrets con valores conocidos
    secrets = {
        "DOCKERHUB_USERNAME": "agora90",
        "DOCKERHUB_TOKEN": "dckr_pat_W1iWIosKBkESIHmkZ3piRLyGNWk"
    }
    
    # Railway token necesita ser obtenido
    print("\n🚂 RAILWAY TOKEN REQUERIDO:")
    print("1. Abre: https://railway.app/account")
    print("2. Login with GitHub")
    print("3. Tokens → Create Token")
    print("4. Name: 'GitHub Actions Deploy'")
    
    railway_token = input("\n🔑 Pega tu Railway token aquí: ").strip()
    if railway_token:
        secrets["RAILWAY_TOKEN"] = railway_token
        print("✅ Railway token configurado")
    else:
        print("❌ Railway token requerido para continuar")
        return
    
    # Discord webhook opcional
    discord_webhook = input("\n🤖 Discord webhook URL (opcional, Enter para saltar): ").strip()
    if discord_webhook:
        secrets["DISCORD_WEBHOOK_URL"] = discord_webhook
        print("✅ Discord webhook configurado")
    
    print(f"\n📋 CONFIGURANDO {len(secrets)} SECRETS EN GITHUB...")
    
    # Método 1: Intentar con GitHub CLI
    gh_cli_success = False
    try:
        # Verificar si gh está disponible y autenticado
        result = subprocess.run(["gh", "auth", "status"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ GitHub CLI detectado y autenticado")
            
            # Configurar cada secret
            success_count = 0
            for secret_name, secret_value in secrets.items():
                print(f"📝 Configurando {secret_name}...")
                
                cmd = [
                    "gh", "secret", "set", secret_name,
                    "--repo", "albertomaydayjhondoe/master",
                    "--body", secret_value
                ]
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"   ✅ {secret_name} configurado")
                        success_count += 1
                    else:
                        print(f"   ❌ Error: {result.stderr}")
                except Exception as e:
                    print(f"   ❌ Exception: {e}")
            
            if success_count == len(secrets):
                gh_cli_success = True
                print(f"\n🎉 {success_count}/{len(secrets)} secrets configurados via GitHub CLI!")
            else:
                print(f"\n⚠️  Solo {success_count}/{len(secrets)} secrets configurados")
                
    except FileNotFoundError:
        print("❌ GitHub CLI no encontrado")
    except Exception as e:
        print(f"❌ Error con GitHub CLI: {e}")
    
    # Método 2: Instrucciones manuales si GitHub CLI falla
    if not gh_cli_success:
        print("\n📋 CONFIGURACIÓN MANUAL REQUERIDA:")
        print("-" * 50)
        
        print("🌐 Ve a: https://github.com/albertomaydayjhondoe/master/settings/secrets/actions")
        print("\n🔑 Configura estos secrets:")
        
        for secret_name, secret_value in secrets.items():
            print(f"\n   Name: {secret_name}")
            print(f"   Value: {secret_value}")
        
        # Abrir URL automáticamente
        choice = input("\n🌐 ¿Abrir GitHub Secrets en navegador? (y/N): ").lower()
        if choice == 'y':
            try:
                webbrowser.open("https://github.com/albertomaydayjhondoe/master/settings/secrets/actions")
                print("✅ Página abierta en navegador")
            except:
                print("❌ Error abriendo navegador")
    
    # Verificar secrets configurados
    print("\n🔍 VERIFICANDO SECRETS...")
    try:
        result = subprocess.run([
            "gh", "secret", "list", 
            "--repo", "albertomaydayjhondoe/master"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Secrets en el repositorio:")
            print(result.stdout)
        else:
            print("❌ No se pudieron verificar secrets")
    except:
        print("⚠️  Verifica manualmente en GitHub")
    
    # Trigger deployment
    print(f"\n🚀 DEPLOYMENT READY!")
    print("Una vez configurados todos los secrets:")
    
    trigger_choice = input("\n🎯 ¿Trigger deployment ahora? (y/N): ").lower()
    if trigger_choice == 'y':
        try:
            result = subprocess.run([
                "gh", "workflow", "run", "deploy-railway.yml",
                "--repo", "albertomaydayjhondoe/master",
                "--field", "deploy_to_railway=true"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Deployment triggered!")
                print("📊 Monitorea en: https://github.com/albertomaydayjhondoe/master/actions")
            else:
                print(f"❌ Error triggering deployment: {result.stderr}")
        except:
            print("⚠️  Trigger manualmente desde GitHub Actions")
    
    print(f"\n🎵 STAKAS MVP DEPLOYMENT SUMMARY:")
    print(f"   📺 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
    print(f"   🐳 Docker: agora90/stakas-mvp:latest")
    print(f"   💰 Budget: €500/month Meta Ads")
    print(f"   🎯 Target: Drill/Rap Español audience")
    print(f"   🚀 Status: Ready for 24/7 viral content!")
    
    print(f"\n📊 URLs importantes:")
    print(f"   • GitHub Actions: https://github.com/albertomaydayjhondoe/master/actions")
    print(f"   • Railway Dashboard: https://railway.app/dashboard")
    print(f"   • Docker Hub: https://hub.docker.com/r/agora90/stakas-mvp")

if __name__ == "__main__":
    main()
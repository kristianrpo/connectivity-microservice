#!/usr/bin/env python
"""
Script to verify if a citizen is registered in the external API.
"""

import os
import sys
import django
import requests

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django.setup()

from django.conf import settings
from apps.citizen_registration.models import CitizenRegistrationTrace


def verify_citizen_in_external_api(citizen_id: int):
    """
    Verify if a citizen exists in the external API.
    
    Args:
        citizen_id: The citizen ID to verify
    """
    api_url = settings.EXTERNAL_GOVCARPETA_API_URL
    endpoint = f"{api_url}/apis/validateCitizen/{citizen_id}"
    
    print("=" * 70)
    print(f"🔍 VERIFICANDO CIUDADANO {citizen_id} EN API EXTERNA")
    print("=" * 70)
    print(f"URL: {endpoint}")
    print()
    
    try:
        response = requests.get(endpoint, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅ CIUDADANO ENCONTRADO EN LA API EXTERNA!")
            print()
            print("Datos del ciudadano:")
            print("-" * 70)
            citizen_data = response.json()
            for key, value in citizen_data.items():
                print(f"  {key}: {value}")
            print("-" * 70)
            return True
            
        elif response.status_code == 204:
            print("❌ CIUDADANO NO ENCONTRADO EN LA API EXTERNA")
            print("   El ciudadano no existe en el sistema centralizado")
            return False
            
        else:
            print(f"⚠️  RESPUESTA INESPERADA: {response.status_code}")
            if response.text:
                print(f"   Respuesta: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ ERROR AL CONECTAR CON LA API: {str(e)}")
        return False


def check_local_trace(citizen_id: int):
    """
    Check local trace records for this citizen.
    
    Args:
        citizen_id: The citizen ID to check
    """
    print()
    print("=" * 70)
    print(f"📋 VERIFICANDO TRAZAS LOCALES PARA CIUDADANO {citizen_id}")
    print("=" * 70)
    
    traces = CitizenRegistrationTrace.objects.filter(
        id_citizen=citizen_id
    ).order_by('-created_at')
    
    if not traces.exists():
        print("❌ No hay trazas locales para este ciudadano")
        print("   El evento de registro nunca fue procesado")
        return
    
    print(f"✅ Encontradas {traces.count()} traza(s) local(es)")
    print()
    
    for i, trace in enumerate(traces, 1):
        print(f"Traza #{i}:")
        print(f"  Message ID: {trace.message_id}")
        print(f"  Estado: {trace.status}")
        print(f"  Creado: {trace.created_at}")
        print(f"  Enviado: {trace.sent_at or 'N/A'}")
        
        if trace.status == 'ERROR':
            print(f"  ❌ Error: {trace.error_message}")
        elif trace.status == 'SENT':
            print(f"  ✅ Status Code: {trace.status_code}")
            if trace.response_data:
                print(f"  Respuesta: {trace.response_data}")
        
        print()


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Uso: python scripts/verify_citizen_registration.py <citizen_id>")
        print()
        print("Ejemplo:")
        print("  python scripts/verify_citizen_registration.py 123456789")
        sys.exit(1)
    
    try:
        citizen_id = int(sys.argv[1])
    except ValueError:
        print("❌ Error: El ID del ciudadano debe ser un número")
        sys.exit(1)
    
    # Check local traces first
    check_local_trace(citizen_id)
    
    # Verify in external API
    verify_citizen_in_external_api(citizen_id)
    
    print()
    print("=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 70)


if __name__ == '__main__':
    main()

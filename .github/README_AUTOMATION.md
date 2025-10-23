# Automatización: Auditoría y limpieza de referencias a redes sociales

¿Qué hace?
- Ejecuta un script que audita el repositorio en busca de menciones a redes sociales (TikTok, Twitter/X, Instagram, etc.), genera inventarios y detecta posibles integraciones de código.
- Reemplaza menciones documentales aisladas a "TikTok" por las redes listadas en el README principal o por "redes sociales" si no hay una lista explícita.
- Crea una rama `audit/socials-cleanup` con los cambios y abre un PR draft para revisión.

Archivos generados por el workflow/script:
- `audit_socials_inventory.txt` — inventario de ficheros y líneas con menciones.
- `code_integration_hits.txt` — heurística de ubicaciones de código que parecen integraciones.
- `candidates_dup.txt` — lista de ficheros candidatos a consolidación.

Cómo ejecutar localmente (ejemplo):
1. Clonar y situarse en el repo:
   - git clone git@github.com:albertomaydayjhondoe/master.git
   - cd master
2. Crear rama de trabajo:
   - git checkout -b ci/audit-socials-workflow
3. Añadir los archivos `scripts/audit_socials.sh` y `.github/workflows/audit_socials.yml` (los contenidos están en este PR).
4. Hacer commits y push:
   - git add .
   - git commit -m "ci: add socials audit workflow"
   - git push origin ci/audit-socials-workflow
5. Crear PR draft (o usar la acción para ejecutarlo).

Precauciones de seguridad:
- El workflow y el script NO añaden ni almacenan credenciales. No incluyas tokens ni secretos en este repositorio.
- Revisa el PR draft antes de aceptar merges automáticos.
- El script no borra ramas remotas automáticamente sin una autorización explícita y pasos separados.

Notas:
- El script intenta ejecutar tests básicos (npm test, pytest) como verificación. Si los tests fallan por cambios realizados, se registrará el fallo en el PR.
- Para cambios en integraciones activas (APIs, clientes), el script solo marca/describe las ubicaciones y solicita revisión manual; no modifica integraciones activas sin confirmación.

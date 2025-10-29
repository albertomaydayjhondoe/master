# Meta System V3.6 - README

Este módulo automatiza el lanzamiento viral de videoclips musicales integrando ML, optimización bayesiana y distribución en Meta Ads, YouTube y Spotify. 

## Estructura
- `meta_system_v3.6.json`: Definición del workflow n8n.
- `meta_system_entrypoint.py`: Entrypoint Python para ejecución automatizada.
- `input_example.json`: Ejemplo de input estructurado.
- `output_example.json`: Ejemplo de output estructurado.

## Uso
1. Prepara un input JSON siguiendo el formato de `input_example.json`.
2. Ejecuta:
   ```
   python meta_system_entrypoint.py input_example.json
   ```
3. El output será un JSON estructurado como `output_example.json`.

## Integración n8n
- El workflow puede ser llamado por trigger programado o API REST.
- Outputs y logs se integran automáticamente con los módulos de reporting y retargeting del sistema.

## Notas
- El pipeline real debe implementar la lógica de ML, scoring y campañas según las fases descritas en la especificación.
- El script actual es una plantilla lista para integración y pruebas end-to-end.

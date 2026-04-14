# Cómo reportar problemas

## Crear un nuevo ticket

1. Ve a la pestaña **Issues** del repositorio
2. Haz clic en **New issue**
3. Selecciona la plantilla adecuada (si existe)
4. Completa la información requerida

## Tipos de issues habituales

| Tipo | Descripción | Ejemplo de título |
|------|-------------|-----------------|
| | `[ERROR]` | Clases, propiedades o axiomas incorrectos | `[ERROR] Clase Persona sin rango en edad` |
| | `[MISSING]` | Conceptos o relaciones faltantes | `[MISSING] Agregar propiedad tieneHabilidad` |
| | `[IMPROVE]` | Mejoras en definiciones o estructura | `[IMPROVE] Definición ambigua de Evento` |
| | `[ALIGN]` | Alineación con otras ontologías | `[ALIGN] Mapear con FOAF` |
| | `[DOCS]` | Documentación incompleta o errónea | `[DOCS] Falta ejemplo de uso` |

## Información requerida

- **Ontología afectada**: Archivo `.owl`, `.ttl`, `.rdf`, etc.
- **URI del recurso**: IRI completo de la clase/propiedad (ej: `http://ejemplo.org/ontologia#Persona`)
- **Descripción del problema**: Qué está mal o falta
- **Justificación**: Referencias a estándares o uso real
- **Solución propuesta** (opcional): Cómo corregirlo

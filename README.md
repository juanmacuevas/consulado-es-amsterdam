# Archivo de Contenidos del Consulado de España en Ámsterdam

Este repositorio proporciona una vista actualizada y organizada de la información disponible en el sitio web del Consulado de España en Ámsterdam. El propósito principal es facilitar el acceso y seguimiento de actualizaciones o modificaciones en los servicios consulares y otra información relevante para la comunidad española residente o con planes de viaje a los Países Bajos.

A diferencia del sitio web oficial, cuya estructura puede complicar la búsqueda de información específica, este proyecto presenta los contenidos en un formato de texto plano. Cada documento incluye un enlace directo a su fuente original en el sitio web del Ministerio de Exteriores, permitiendo una verificación fácil de la información.

## Contenido y Actualizaciones

La información se organiza en carpetas denominadas [Páginas](./Páginas) y [Servicios Consulares](./Servicios%20Consulares), y se actualiza automáticamente cada semana. Esto asegura que los usuarios tengan acceso a la información más reciente y pertinente. Además, mediante el uso del buscador de GitHub, el repositorio facilita la búsqueda rápida de documentos con palabras específicas, como por ejemplo [pasaporte](https://github.com/search?q=repo%3Ajuanmacuevas%2Fconsulado-es-amsterdam+language%3AMarkdown+pasaporte&type=code) o [elecciones](https://github.com/search?q=repo%3Ajuanmacuevas%2Fconsulado-es-amsterdam%20elecciones&type=code).

Para aquellos interesados en el historial de actualizaciones, el [historial de cambios](https://github.com/juanmacuevas/consulado-es-amsterdam/commits) en el repositorio proporciona un registro detallado de todas las modificaciones aplicadas.

## Actualización Automática de la Información

El mecanismo detrás de estas actualizaciones semanales se basa en un script de Python. Este script automatizado (GitHub Actions) se ejecuta cada lunes y navega por todo el sitio web del consulado, identifica cambios en el contenido desde su última ejecución y actualiza este repositorio con la información más reciente.

### Ejecutando el Script Localmente

Para aquellos con interés en ejecutar el script de actualización manualmente, sigue estos pasos en tu terminal:

```
git clone https://github.com/juanmacuevas/consulado-es-amsterdam 
cd consulado-es-amsterdam
pip install -r requirements.txt 
python download-servicios-consulares.py
```

Si encuentras algún problema o tienes sugerencias para mejorar este proyecto, por favor, abre un issue en este repositorio. Tu contribución es bienvenida.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para detalles.

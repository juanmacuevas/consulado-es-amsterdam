# Archivo de Contenidos del Consulado de España en Ámsterdam

Este repositorio (no oficial) proporciona una vista actualizada y organizada de la información disponible en el sitio web del Consulado de España en Ámsterdam. El propósito principal es facilitar el acceso y seguimiento de actualizaciones o modificaciones en los servicios consulares y otra información relevante para la comunidad española residente o con planes de viaje a los Países Bajos.

A diferencia del sitio web oficial, cuya estructura puede complicar la búsqueda de información específica, este proyecto presenta los contenidos en un formato de texto plano. Cada documento incluye un enlace directo a su fuente original en el sitio web del Ministerio de Exteriores, permitiendo una verificación fácil de la información.

## Contenido y Búsqueda

La información se organiza en carpetas denominadas [Páginas](./Páginas) y [Servicios Consulares](./Servicios%20Consulares), y se actualiza automáticamente cada semana. Esto asegura que los usuarios tengan acceso a la información más reciente y pertinente. 
Además, mediante el uso del buscador de GitHub, el repositorio facilita la búsqueda rápida de documentos con palabras específicas, como por ejemplo [pasaporte](https://github.com/search?q=repo%3Ajuanmacuevas%2Fconsulado-es-amsterdam+language%3AMarkdown+pasaporte&type=code) o [elecciones](https://github.com/search?q=repo%3Ajuanmacuevas%2Fconsulado-es-amsterdam%20elecciones&type=code).

## Información Actualizada Periódicamente

El mecanismo para detectar cambios (script de Python automatizado con GitHub Actions) se ejecuta cada lunes y navega por todo el sitio web del consulado, identifica diferencias en el contenido desde su última visita y actualiza este repositorio con la información más reciente.
Se muestra un registro detallado de todas las modificaciones aplicadas en el [historial de cambios](https://github.com/juanmacuevas/consulado-es-amsterdam/commits) proporcionado por el repositorio. Existe la opción de recibir notificaciones dándole al botón "👁️ Watch" del repositorio.

## Comentarios y Quejas sobre los Contenidos

Algunos documentos contienen errores, bien sea por información incorrecta, desactualizada en la fuente original, o debido a desafíos en el proceso de copia automatizada. Si encuentras algún error o inexactitud en los documentos, te animamos a contribuir añadiendo un comentario en la línea específica que contiene el error: haz clic en el número de la línea, click en los tres puntos, y elige "Reference in new issue". Para ver los números de línea debes estar en modo "Code" o "Blame", no en "Preview".

Los errores identificados serán comunicados al Consulado para su corrección, contribuyendo así a la mejora continua de la calidad de la información ofrecida tanto en este repositorio como en la fuente oficial.


### Ejecutando el Script Localmente

Para aquellos con interés en ejecutar el script de actualización manualmente, estos son los comandos de terminal:

```
git clone https://github.com/juanmacuevas/consulado-es-amsterdam 
cd consulado-es-amsterdam
pip install -r requirements.txt 
python download-servicios-consulares.py
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para detalles.

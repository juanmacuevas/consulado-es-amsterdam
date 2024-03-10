# Historial de Cambios en la Web del Consulado Español en Ámsterdam

Este proyecto ofrece un registro continuo y actualizado de la información disponible en el sitio web del Consulado Español en Ámsterdam. Su objetivo es facilitar el seguimiento de cualquier cambio o actualización en los servicios consulares, noticias y otros avisos importantes para la comunidad española en los Países Bajos.

## ¿Qué encontrarás aquí?

Este repositorio mantiene un registro actualizado de los cambios en el sitio web del Consulado Español en Ámsterdam, incluyendo anuncios de servicios consulares, trámites y consejos útiles. La información se actualiza automáticamente cada semana y se organiza en formatos legibles y fáciles de buscar, asegurando que tengas acceso a datos relevantes y recientes.

Los documentos actualizados se almacenan en las carpetas [Páginas](./Páginas) y [Servicios Consulares](./Servicios%20Consulares), permitiéndote un acceso directo y organizado a la información. Para ver un registro detallado de todos los cambios realizados en este repositorio, puedes consultar el [historial de cambios](https://github.com/juanmacuevas/consulado-es-amsterdam/commits).

## Actualización Automática de la Información

El mecanismo detrás de estas actualizaciones semanales se basa en un script de Python. Este script automatizado navega por el sitio web del consulado, identifica cambios en el contenido desde su última ejecución y actualiza este repositorio con la información más reciente.

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

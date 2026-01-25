# 🏗️ Sistema de Gestión - Alambrados del Carmen

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://alambrados.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

> **Aplicación integral de gestión comercial, control de stock y producción para empresas de cercos y alambrados.**

## 📖 Sobre el Proyecto

Este proyecto nació de la necesidad de digitalizar y optimizar los procesos de **"Alambrados del Carmen"**. El objetivo fue reemplazar planillas manuales y cuadernos por un sistema centralizado, robusto y fácil de usar que pudiera operar tanto en la nube como en entornos locales sin internet.

La aplicación permite gestionar el ciclo completo del negocio: desde la **cotización** y emisión de presupuestos en PDF, pasando por el control de **stock en tiempo real**, hasta el seguimiento de la **producción** y el fraguado de materiales.

## 🚀 Funcionalidades Principales

### 1. 📝 Cotizador Inteligente y Ventas
* **Carga Rápida en Lote:** Tabla interactiva para ingresar múltiples códigos de productos simultáneamente (ideal para pedidos grandes).
* **Buscador Predictivo:** Búsqueda por nombre de producto para ítems específicos.
* **Generación de PDF:** Emisión automática de presupuestos profesionales con logo, detalles y legales, listos para imprimir o enviar por WhatsApp.
* **Doble Modalidad:** Permite guardar como "Solo Presupuesto" (sin descontar stock) o "Confirmar Venta" (actualizando inventario).

### 2. 📦 Gestión de Stock Avanzada
* **Persistencia de Datos:** Sistema de base de datos local (CSV) con lógica de seguridad para evitar pérdida de información.
* **Edición "Tipo Excel":** Modificación directa de precios, cantidades y nombres desde la grilla.
* **Cálculo Financiero:** Visualización automática de márgenes de ganancia (Precio Venta - Costo).
* **Control de Acopio:** Distinción entre stock físico real y mercadería reservada/acopiada.

### 3. 🏭 Módulo de Producción
* **Control de Fraguado:** Seguimiento de fechas de elaboración para postes de hormigón.
* **Alertas Automáticas:** El sistema avisa cuándo un lote cumple los 28 días de fraguado y está listo para liberar al stock.
* **Ingreso Directo:** Posibilidad de crear y dar de alta productos nuevos directamente desde la fábrica.

### 4. 📊 Historial y Auditoría
* **Registro Completo:** Base de datos de todas las operaciones realizadas.
* **Reimpresión:** Motor inteligente capaz de reconstruir y volver a generar el PDF de cualquier venta pasada, incluso si los precios actuales han cambiado.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** [Python](https://www.python.org/)
* **Framework Web:** [Streamlit](https://streamlit.io/) (para una interfaz rápida y responsive).
* **Manejo de Datos:** [Pandas](https://pandas.pydata.org/) (manipulación de CSVs y DataFrames).
* **Reportes:** `fpdf` (generación de documentos PDF pixel-perfect).
* **Lógica:** `ast`, `re`, `datetime` (procesamiento de datos y fechas).

## 💻 Demo y Uso

Podés probar la aplicación en vivo desplegada en Streamlit Cloud:
👉 **[Ver Aplicación en Vivo](https://alambrados.streamlit.app)**

## 🔧 Instalación Local

Si deseás correr este proyecto en tu propia máquina:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/Martin-Comito/alambrados.git](https://github.com/Martin-Comito/alambrados.git)
    cd alambrados
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install streamlit pandas fpdf xlsxwriter pytz
    ```

3.  **Ejecutar la aplicación:**
    ```bash
    streamlit run cotizador.py
    ```

## 👨‍💻 Autor

**Martín Cómito**
* *Data Science & AI Student | Python Developer*
* 📍 Carmen de Areco, Buenos Aires
* 🎓 ISFT 213 Ensenada

Estoy enfocado en crear soluciones tecnológicas que aporten valor real a los negocios, combinando lógica de programación con análisis de datos.

---
*Hecho con ❤️ y mucho ☕ en Buenos Aires.*

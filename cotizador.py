import streamlit as st
import pandas as pd
import os
from datetime import date
from fpdf import FPDF

# CONFIGURACIÓN DE PÁGINA 
st.set_page_config(page_title="Sistema Alambrados del Carmen", layout="wide", page_icon="🏗️")

# RUTAS Y ARCHIVOS
STOCK_FILE = "stock_del_carmen.csv"
GASTOS_FILE = "gastos_del_carmen.csv"
VENTAS_FILE = "ventas_del_carmen.csv"
LOGO_FILE = "alambradoslogo.jpeg"  

# INICIALIZACIÓN 
def inicializar_archivos():
    # Agregamos 'Codigo' como columna nueva
    cols_stock = ["Codigo", "Producto", "Cantidad", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    
    if not os.path.exists(STOCK_FILE):
        pd.DataFrame(columns=cols_stock).to_csv(STOCK_FILE, index=False)
    else:
        # Parche para agregar columna Codigo si no existe en versiones viejas
        df = pd.read_csv(STOCK_FILE)
        if "Codigo" not in df.columns:
            df.insert(0, "Codigo", "") # Agrega columna vacía al principio
            df.to_csv(STOCK_FILE, index=False)
    
    if not os.path.exists(GASTOS_FILE):
        pd.DataFrame(columns=["Fecha", "Insumo", "Cantidad", "Monto"]).to_csv(GASTOS_FILE, index=False)
    if not os.path.exists(VENTAS_FILE):
        pd.DataFrame(columns=["Fecha", "Cliente", "Total", "Detalle"]).to_csv(VENTAS_FILE, index=False)

def cargar_datos(archivo):
    return pd.read_csv(archivo)

#  CLASE PARA EL PDF 
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            # Logo en la esquina superior izquierda (x, y, w)
            self.image(LOGO_FILE, 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(80) # Mover a la derecha
        self.cell(30, 10, 'PRESUPUESTO', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Alambrados del Carmen S.A. - Haciendo clientes felices', 0, 0, 'C')

    def water_mark(self):
        # Marca de agua centrada y grande
        if os.path.exists(LOGO_FILE):
            self.set_alpha(0.1) # Transparencia muy bajita (10%)
            self.image(LOGO_FILE, x=50, y=80, w=110)
            self.set_alpha(1) # Restaurar opacidad

# Función para generar el PDF
def generar_pdf(cliente, items, total):
    pdf = PDF()
    pdf.add_page()
    pdf.water_mark()
    
    # Datos del Cliente
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {date.today()}", ln=True)
    pdf.ln(10)
    
    # Tabla de Productos
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Código", 1)
    pdf.cell(80, 10, "Descripción", 1)
    pdf.cell(25, 10, "Cant.", 1)
    pdf.cell(25, 10, "Unitario", 1)
    pdf.cell(30, 10, "Subtotal", 1)
    pdf.ln()
    
    pdf.set_font("Arial", size=10)
    for item in items:
        # Asumiendo que item tiene: [Codigo, Producto, Cantidad, PrecioUnit, Subtotal]
        pdf.cell(30, 10, str(item['Codigo']), 1)
        pdf.cell(80, 10, str(item['Producto']), 1)
        pdf.cell(25, 10, str(item['Cantidad']), 1)
        pdf.cell(25, 10, f"${item['Precio']:.0f}", 1)
        pdf.cell(30, 10, f"${item['Subtotal']:.0f}", 1)
        pdf.ln()
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(160, 10, "TOTAL PRESUPUESTO", 0)
    pdf.cell(30, 10, f"${total:,.2f}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1')

inicializar_archivos()

#  ESTADO DE SESIÓN (CARRITO DE COMPRAS) 
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# INTERFAZ 
st.title("🏗️ Alambrados del Carmen S.A.")

tab_cot, tab_stock, tab_hist = st.tabs(["📝 Cotizador Modular", "📦 Stock Fácil", "📊 Historial"])

# TAB 1: COTIZADOR MODULAR (TIPO CARRITO)
with tab_cot:
    df_s = cargar_datos(STOCK_FILE)
    
    col_izq, col_der = st.columns([1, 1])
    
    with col_izq:
        st.subheader("1. Armar Pedido")
        cliente = st.text_input("Nombre del Cliente")
        
        # Buscador inteligente (por Nombre o Código)
        st.write("---")
        opciones_prod = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']} - ${x['Precio Venta']}", axis=1)
        seleccion_str = st.selectbox("Buscar Producto (Nombre o Código):", options=["Seleccionar..."] + list(opciones_prod))
        
        c_cant, c_boton = st.columns([1, 2])
        cantidad = c_cant.number_input("Cantidad", min_value=1.0, value=1.0)
        
        if c_boton.button("➕ Agregar al Presupuesto") and seleccion_str != "Seleccionar...":
            # Extraer datos del string seleccionado
            cod_prod = seleccion_str.split("]")[0].replace("[", "")
            # Buscar en el DF
            fila = df_s[df_s["Codigo"] == cod_prod].iloc[0]
            
            # Agregar al carrito
            item = {
                "Codigo": fila["Codigo"],
                "Producto": fila["Producto"],
                "Cantidad": cantidad,
                "Precio": fila["Precio Venta"],
                "Subtotal": cantidad * fila["Precio Venta"]
            }
            st.session_state.carrito.append(item)
            st.success(f"Agregado: {fila['Producto']}")
            st.rerun()

    with col_der:
        st.subheader("2. Detalle del Presupuesto")
        if len(st.session_state.carrito) > 0:
            df_carrito = pd.DataFrame(st.session_state.carrito)
            st.dataframe(df_carrito, hide_index=True, use_container_width=True)
            
            # Botón para borrar último ítem si se equivocó
            if st.button("🗑️ Borrar último ítem"):
                st.session_state.carrito.pop()
                st.rerun()
                
            total_presupuesto = df_carrito["Subtotal"].sum()
            st.metric("TOTAL A COBRAR", f"$ {total_presupuesto:,.2f}")
            
            st.markdown("---")
            c_pdf, c_venta = st.columns(2)
            
            # GENERAR PDF
            pdf_bytes = generar_pdf(cliente if cliente else "Consumidor Final", st.session_state.carrito, total_presupuesto)
            c_pdf.download_button(
                label="📄 Descargar PDF con Logo",
                data=pdf_bytes,
                file_name=f"Presupuesto_{cliente}.pdf",
                mime="application/pdf"
            )
            
            # CONFIRMAR VENTA (DESCUENTA STOCK)
            if c_venta.button("✅ Confirmar Venta (Bajar Stock)"):
                # 1. Descontar del Stock real
                for item in st.session_state.carrito:
                    # Buscar índice del producto
                    idx = df_s.index[df_s["Codigo"] == item["Codigo"]].tolist()
                    if idx:
                        df_s.at[idx[0], "Cantidad"] -= item["Cantidad"]
                
                df_s.to_csv(STOCK_FILE, index=False)
                
                # 2. Guardar en Historial
                nuevo_registro = pd.DataFrame([{
                    "Fecha": date.today(),
                    "Cliente": cliente,
                    "Total": total_presupuesto,
                    "Detalle": str([x["Producto"] for x in st.session_state.carrito])
                }])
                pd.concat([cargar_datos(VENTAS_FILE), nuevo_registro]).to_csv(VENTAS_FILE, index=False)
                
                # 3. Limpiar carrito
                st.session_state.carrito = []
                st.success("¡Venta registrada y stock actualizado!")
                st.rerun()
                
        else:
            st.info("El presupuesto está vacío. Agregá productos desde la izquierda.")

# TAB 2: STOCK FÁCIL 
with tab_stock:
    st.header("📦 Control de Stock")
    df_s = cargar_datos(STOCK_FILE)
    
    # 1. INGRESO RÁPIDO 
    with st.expander("⚡ Ingreso Rápido de Mercadería (Usar este)", expanded=True):
        st.write("Seleccioná el producto que llegó y poné la cantidad. Se suma solo.")
        c_prod_in, c_cant_in, c_btn_in = st.columns([2, 1, 1])
        
        lista_prods = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']}", axis=1)
        prod_ingreso = c_prod_in.selectbox("Producto que ingresó:", options=lista_prods)
        cant_ingreso = c_cant_in.number_input("Cantidad a sumar", min_value=1.0)
        
        if c_btn_in.button("📥 Sumar al Stock"):
            cod_b = prod_ingreso.split("]")[0].replace("[", "")
            idx = df_s.index[df_s["Codigo"] == cod_b].tolist()
            if idx:
                df_s.at[idx[0], "Cantidad"] += cant_ingreso
                df_s.to_csv(STOCK_FILE, index=False)
                st.success(f"Se sumaron {cant_ingreso} a {prod_ingreso}")
                st.rerun()

    st.markdown("---")
    
    # 2. TABLA COMPLETA 
    st.subheader("Listado Completo (Editable)")
    st.info("Hacé doble clic en la celda que quieras cambiar (Precio, Código, etc).")
    
    df_edit = st.data_editor(
        df_s,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_stock_erp",
        column_config={
            "Codigo": st.column_config.TextColumn("Código Interno", help="Ej: A001"),
            "Precio Costo": st.column_config.NumberColumn("Costo", format="$ %d"),
            "Precio Venta": st.column_config.NumberColumn("Venta", format="$ %d"),
            "Cantidad": st.column_config.NumberColumn("Stock", format="%.1f"),
        }
    )
    
    if st.button("💾 Guardar Cambios Manuales"):
        df_edit.to_csv(STOCK_FILE, index=False)
        st.success("Guardado.")
        st.rerun()

# TAB 3: HISTORIAL
with tab_hist:
    st.header("Historial de Ventas")
    df_v = cargar_datos(VENTAS_FILE)
    st.dataframe(df_v.sort_values(by="Fecha", ascending=False), use_container_width=True)

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
    # Definimos las columnas
    cols_stock = ["Codigo", "Producto", "Cantidad", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    
    if not os.path.exists(STOCK_FILE):
        pd.DataFrame(columns=cols_stock).to_csv(STOCK_FILE, index=False)
    else:
        # Parche inteligente: Si el archivo existe, revisamos las columnas
        try:
            df = pd.read_csv(STOCK_FILE)
            guardar = False
            
            # 1. Si falta la columna Codigo, la agregamos al principio
            if "Codigo" not in df.columns:
                df.insert(0, "Codigo", "")
                guardar = True
            
            # 2. Si faltan otras columnas, las agregamos
            for col in cols_stock:
                if col not in df.columns:
                    df[col] = 0.0
                    guardar = True
            
            if guardar:
                df.to_csv(STOCK_FILE, index=False)
        except:
            # Si el archivo está muy roto, creamos uno backup y uno nuevo
            if os.path.exists(STOCK_FILE):
                os.rename(STOCK_FILE, f"stock_backup_{date.today()}.csv")
            pd.DataFrame(columns=cols_stock).to_csv(STOCK_FILE, index=False)
    
    if not os.path.exists(GASTOS_FILE):
        pd.DataFrame(columns=["Fecha", "Insumo", "Cantidad", "Monto"]).to_csv(GASTOS_FILE, index=False)
    if not os.path.exists(VENTAS_FILE):
        pd.DataFrame(columns=["Fecha", "Cliente", "Total", "Detalle"]).to_csv(VENTAS_FILE, index=False)

def cargar_datos(archivo):
    return pd.read_csv(archivo)

# CLASE PDF 
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            self.image(LOGO_FILE, 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'PRESUPUESTO', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Alambrados del Carmen S.A. - Haciendo clientes felices', 0, 0, 'C')

    def water_mark(self):
        if os.path.exists(LOGO_FILE):
            self.set_alpha(0.1)
            self.image(LOGO_FILE, x=50, y=80, w=110)
            self.set_alpha(1)

def generar_pdf(cliente, items, total):
    pdf = PDF()
    pdf.add_page()
    pdf.water_mark()
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {date.today()}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Código", 1)
    pdf.cell(80, 10, "Descripción", 1)
    pdf.cell(25, 10, "Cant.", 1)
    pdf.cell(25, 10, "Unitario", 1)
    pdf.cell(30, 10, "Subtotal", 1)
    pdf.ln()
    
    pdf.set_font("Arial", size=10)
    for item in items:
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

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# INTERFAZ 
st.title("🏗️ Alambrados del Carmen S.A.")

tab_cot, tab_stock, tab_hist = st.tabs(["📝 Cotizador Modular", "📦 Stock Fácil", "📊 Historial"])

# TAB 1: COTIZADOR
with tab_cot:
    df_s = cargar_datos(STOCK_FILE)
    
    # LIMPIEZA DE DATOS 
    df_s["Codigo"] = df_s["Codigo"].fillna("").astype(str)
    df_s["Precio Venta"] = pd.to_numeric(df_s["Precio Venta"], errors='coerce').fillna(0.0)
    
    col_izq, col_der = st.columns([1, 1])
    
    with col_izq:
        st.subheader("1. Armar Pedido")
        cliente = st.text_input("Nombre del Cliente")
        
        st.write("---")
        # Generar lista segura para el selectbox
        opciones_prod = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']} - ${float(x['Precio Venta']):.0f}", axis=1)
        seleccion_str = st.selectbox("Buscar Producto:", options=["Seleccionar..."] + list(opciones_prod))
        
        c_cant, c_boton = st.columns([1, 2])
        cantidad = c_cant.number_input("Cantidad", min_value=1.0, value=1.0)
        
        if c_boton.button("➕ Agregar") and seleccion_str != "Seleccionar...":
            cod_prod = seleccion_str.split("]")[0].replace("[", "")
            # Buscamos asegurando tipos
            fila = df_s[df_s["Codigo"] == cod_prod].iloc[0]
            
            item = {
                "Codigo": fila["Codigo"],
                "Producto": fila["Producto"],
                "Cantidad": cantidad,
                "Precio": float(fila["Precio Venta"]),
                "Subtotal": cantidad * float(fila["Precio Venta"])
            }
            st.session_state.carrito.append(item)
            st.success(f"Agregado: {fila['Producto']}")
            st.rerun()

    with col_der:
        st.subheader("2. Detalle")
        if len(st.session_state.carrito) > 0:
            df_carrito = pd.DataFrame(st.session_state.carrito)
            st.dataframe(df_carrito, hide_index=True, use_container_width=True)
            
            if st.button("🗑️ Borrar último"):
                st.session_state.carrito.pop()
                st.rerun()
                
            total_presupuesto = df_carrito["Subtotal"].sum()
            st.metric("TOTAL", f"$ {total_presupuesto:,.2f}")
            
            st.markdown("---")
            c_pdf, c_venta = st.columns(2)
            
            pdf_bytes = generar_pdf(cliente if cliente else "Consumidor Final", st.session_state.carrito, total_presupuesto)
            c_pdf.download_button("📄 Bajar PDF", pdf_bytes, f"P_{cliente}.pdf", "application/pdf")
            
            if c_venta.button("✅ Confirmar Venta"):
                for item in st.session_state.carrito:
                    idx = df_s.index[df_s["Codigo"] == item["Codigo"]].tolist()
                    if idx:
                        cant_actual = float(df_s.at[idx[0], "Cantidad"])
                        df_s.at[idx[0], "Cantidad"] = cant_actual - item["Cantidad"]
                
                df_s.to_csv(STOCK_FILE, index=False)
                
                nuevo = pd.DataFrame([{
                    "Fecha": date.today(),
                    "Cliente": cliente,
                    "Total": total_presupuesto,
                    "Detalle": str([x["Producto"] for x in st.session_state.carrito])
                }])
                pd.concat([cargar_datos(VENTAS_FILE), nuevo]).to_csv(VENTAS_FILE, index=False)
                
                st.session_state.carrito = []
                st.success("¡Venta OK!")
                st.rerun()
        else:
            st.info("Presupuesto vacío.")

# TAB 2: STOCK (SOLUCIÓN AL ERROR)
with tab_stock:
    st.header("📦 Control de Stock")
    df_s = cargar_datos(STOCK_FILE)
    
    # LIMPIEZA AUTOMÁTICA DE TIPOS DE DATOS 
    # Esto evita el error de "check_type_compatibilities"
    df_s["Codigo"] = df_s["Codigo"].fillna("").astype(str)
    df_s["Producto"] = df_s["Producto"].fillna("Sin Nombre").astype(str)
    df_s["Unidad"] = df_s["Unidad"].fillna("un.").astype(str)
    
    # Forzamos a números (si hay error, pone 0)
    cols_num = ["Cantidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    for col in cols_num:
        df_s[col] = pd.to_numeric(df_s[col], errors='coerce').fillna(0.0)
    # --------------------------------------------------------

    with st.expander("⚡ Ingreso Rápido"):
        c1, c2, c3 = st.columns([2, 1, 1])
        opc = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']}", axis=1)
        p_ing = c1.selectbox("Producto:", options=opc)
        c_ing = c2.number_input("Cantidad +", min_value=1.0)
        
        if c3.button("📥 Sumar"):
            cod = p_ing.split("]")[0].replace("[", "")
            idx = df_s.index[df_s["Codigo"] == cod].tolist()
            if idx:
                val_act = float(df_s.at[idx[0], "Cantidad"])
                df_s.at[idx[0], "Cantidad"] = val_act + c_ing
                df_s.to_csv(STOCK_FILE, index=False)
                st.success(f"Sumados {c_ing} un.")
                st.rerun()

    st.subheader("Listado Completo")
    st.info("Hacé doble clic para editar.")
    
    # Ahora sí, el data_editor recibirá datos limpios
    df_edit = st.data_editor(
        df_s,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_stock_erp",
        column_config={
            "Codigo": st.column_config.TextColumn("Código", help="Clave única"),
            "Precio Costo": st.column_config.NumberColumn("Costo", format="$ %d"),
            "Precio Venta": st.column_config.NumberColumn("Venta", format="$ %d"),
            "Cantidad": st.column_config.NumberColumn("Stock", format="%.1f"),
            "Stock Minimo": st.column_config.NumberColumn("Mínimo", format="%d"),
        }
    )
    
    if st.button("💾 Guardar Todo"):
        df_edit.to_csv(STOCK_FILE, index=False)
        st.success("Guardado.")
        st.rerun()

# TAB 3: HISTORIAL
with tab_hist:
    st.header("Historial")
    df_v = cargar_datos(VENTAS_FILE)
    st.dataframe(df_v.sort_values(by="Fecha", ascending=False), use_container_width=True)

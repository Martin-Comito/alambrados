import streamlit as st
import pandas as pd
import os
import io
from datetime import date, timedelta, datetime
import pytz
from fpdf import FPDF

# --- AUTO-CONFIGURACIÓN DE TEMA CORPORATIVO (EL SECRETO) ---
# Esto crea un archivo que fuerza los colores ROJOS de la marca
def configurar_tema_alambrados():
    config_dir = ".streamlit"
    config_path = os.path.join(config_dir, "config.toml")
    
    # Definimos el tema rojo/blanco basado en el logo
    tema_corporativo = """
[theme]
base="light"
primaryColor="#D32F2F"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#31333F"
font="sans serif"
"""
    # Si no existe la configuración, la creamos
    if not os.path.exists(config_path):
        try:
            os.makedirs(config_dir, exist_ok=True)
            with open(config_path, "w") as f:
                f.write(tema_corporativo)
            return True # Indica que se creó y necesita reinicio
        except:
            pass
    return False

# Ejecutar configuración antes de nada
necesita_reinicio = configurar_tema_alambrados()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Alambrados del Carmen", layout="wide", page_icon="🏗️")

# Si se acaba de aplicar el tema nuevo, avisamos al usuario
if necesita_reinicio:
    st.warning("🎨 ¡Tema Corporativo Instalado! Por favor, detené la aplicación y volvé a ejecutarla para ver los colores Rojos.")
    st.stop()

# --- ESTILOS EXTRA (CSS) ---
# Para terminar de ajustar detalles que el tema automático no cubre
st.markdown("""
    <style>
        /* Agrandar el logo en la barra lateral */
        [data-testid="stSidebar"] img {
            margin-top: 20px;
            border-radius: 5px;
            border: 2px solid #D32F2F;
        }
        /* Títulos en Rojo Institucional */
        h1, h2, h3 {
            color: #B71C1C !important;
        }
        /* Destacar métricas */
        [data-testid="stMetricValue"] {
            color: #D32F2F;
        }
    </style>
""", unsafe_allow_html=True)

# --- RUTAS Y ARCHIVOS ---
STOCK_FILE = "stock_del_carmen.csv"
GASTOS_FILE = "gastos_del_carmen.csv"
VENTAS_FILE = "ventas_del_carmen.csv"
PRODUCCION_FILE = "produccion_del_carmen.csv"
LOGO_FILE = "alambrados.jpeg" # El logo rojo

# --- FUNCIONES ---
def ahora_arg():
    try:
        tz = pytz.timezone('America/Argentina/Buenos_Aires')
        return datetime.now(tz)
    except:
        return datetime.now()

def generar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Stock')
    return output.getvalue()

def cargar_datos_stock():
    if not os.path.exists(STOCK_FILE): return pd.DataFrame(columns=["Codigo","Producto","Cantidad","Reservado","Unidad","Precio Costo","Precio Venta","Stock Minimo"])
    df = pd.read_csv(STOCK_FILE)
    # Limpieza de datos
    df["Codigo"] = df["Codigo"].fillna("").astype(str)
    df["Producto"] = df["Producto"].fillna("").astype(str)
    df["Unidad"] = df["Unidad"].fillna("un.").astype(str)
    for col in ["Cantidad", "Reservado", "Precio Costo", "Precio Venta", "Stock Minimo"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df

def cargar_datos_general(archivo, cols):
    if not os.path.exists(archivo): return pd.DataFrame(columns=cols)
    return pd.read_csv(archivo)

# --- CLASE PDF ---
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 170, 8, 30) 
            except: pass
        self.set_font('Arial', 'B', 15)
        self.set_text_color(183, 28, 28) # Rojo oscuro para el título
        self.cell(80)
        self.cell(30, 10, 'PRESUPUESTO', 0, 0, 'C')
        self.ln(20)
        self.set_text_color(0, 0, 0) # Volver a negro

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Alambrados del Carmen S.A. - Haciendo clientes felices', 0, 0, 'C')

def generar_pdf(cliente, items, total, tipo_venta):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    fecha_hora = ahora_arg().strftime("%d/%m/%Y %H:%M")
    
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {fecha_hora} ({tipo_venta})", ln=True)
    pdf.ln(10)
    
    # Encabezado Tabla Rojo
    pdf.set_fill_color(211, 47, 47) 
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(20, 10, "Cod", 1, 0, 'C', True)
    pdf.cell(90, 10, "Producto", 1, 0, 'C', True)
    pdf.cell(20, 10, "Cant", 1, 0, 'C', True)
    pdf.cell(30, 10, "Unit", 1, 0, 'C', True)
    pdf.cell(30, 10, "Total", 1, 1, 'C', True)
    
    # Filas
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=10)
    for item in items:
        pdf.cell(20, 10, str(item['Codigo']), 1)
        pdf.cell(90, 10, str(item['Producto']), 1)
        pdf.cell(20, 10, str(item['Cantidad']), 1)
        pdf.cell(30, 10, f"${item['Precio']:.0f}", 1)
        pdf.cell(30, 10, f"${item['Subtotal']:.0f}", 1)
        pdf.ln()
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(160, 10, "TOTAL FINAL", 0)
    pdf.set_text_color(183, 28, 28)
    pdf.cell(30, 10, f"${total:,.0f}", 0, 1)
    return pdf.output(dest='S').encode('latin-1')

# Inicializar Carrito
if 'carrito' not in st.session_state: st.session_state.carrito = []

# --- BARRA LATERAL ---
with st.sidebar:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    else:
        st.title("AC")
    
    st.write("---")
    st.caption(f"📅 {ahora_arg().strftime('%d/%m/%Y')}")
    st.caption(f"🕒 {ahora_arg().strftime('%H:%M')}")
    st.write("---")

    # Botón de Reseteo (Oculto en expander para seguridad)
    with st.expander("⚙️ Admin"):
        if st.button("♻️ Restaurar Todo"):
             # Borramos archivos para reiniciar
             if os.path.exists(STOCK_FILE): os.remove(STOCK_FILE)
             st.success("Reiniciando sistema...")
             st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("Gestión Comercial")

tab_cot, tab_stock, tab_prod, tab_hist = st.tabs(["📝 Cotizador", "📦 Stock", "🏭 Producción", "📊 Historial"])

# 1. COTIZADOR
with tab_cot:
    df_s = cargar_datos_stock()
    # Si el DF está vacío (primer uso tras reset), creamos columnas
    if df_s.empty and "Cantidad" not in df_s.columns:
         st.info("⚠️ La base de datos está vacía. Cargá productos en la pestaña STOCK.")
    else:
        if "Reservado" not in df_s.columns: df_s["Reservado"] = 0.0
        df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]

        col_izq, col_der = st.columns([1, 1])
        with col_izq:
            st.subheader("Datos del Pedido")
            cliente = st.text_input("Nombre Cliente")
            st.write("") # Espacio
            
            # Buscador
            opciones = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']} (Disp: {x['DISPONIBLE']:.0f})", axis=1)
            sel_prod = st.selectbox("Buscar Producto:", ["Seleccionar..."] + list(opciones))
            
            c_cant, c_add = st.columns([1, 2])
            cant = c_cant.number_input("Cantidad", min_value=1.0, value=1.0)
            
            if c_add.button("➕ AGREGAR ITEM", use_container_width=True) and sel_prod != "Seleccionar...":
                cod = sel_prod.split("]")[0].replace("[", "")
                fila = df_s[df_s["Codigo"] == cod].iloc[0]
                
                item = {
                    "Codigo": fila["Codigo"], "Producto": fila["Producto"],
                    "Cantidad": cant, "Precio": fila["Precio Venta"],
                    "Subtotal": cant * fila["Precio Venta"]
                }
                st.session_state.carrito.append(item)
                st.rerun()

        with col_der:
            st.subheader("Carrito")
            if st.session_state.carrito:
                df_c = pd.DataFrame(st.session_state.carrito)
                st.dataframe(df_c[["Producto", "Cantidad", "Subtotal"]], hide_index=True, use_container_width=True)
                
                total = df_c["Subtotal"].sum()
                st.divider()
                c_tot, c_trash = st.columns([3,1])
                c_tot.metric("TOTAL A COBRAR", f"${total:,.0f}")
                if c_trash.button("🗑️", help="Borrar todo"):
                    st.session_state.carrito = []
                    st.rerun()
                
                st.divider()
                st.write("Confirmación:")
                tipo = st.radio("Destino mercadería:", ["Entrega Inmediata", "Dejar en Acopio"], horizontal=True)
                
                c_pdf, c_ok = st.columns(2)
                
                # PDF
                pdf_bytes = generar_pdf(cliente, st.session_state.carrito, total, tipo)
                c_pdf.download_button("📄 Imprimir Presupuesto", pdf_bytes, f"P_{cliente}.pdf", "application/pdf", use_container_width=True)
                
                if c_ok.button("✅ REGISTRAR VENTA", type="primary", use_container_width=True):
                    # Actualizar Stock
                    for item in st.session_state.carrito:
                        idx = df_s.index[df_s["Codigo"] == item["Codigo"]].tolist()
                        if idx:
                            i = idx[0]
                            if "Acopio" in tipo: df_s.at[i, "Reservado"] += item["Cantidad"]
                            else: df_s.at[i, "Cantidad"] -= item["Cantidad"]
                    df_s.to_csv(STOCK_FILE, index=False)
                    
                    # Guardar Venta
                    nuevo = pd.DataFrame([{
                        "Fecha": ahora_arg().strftime("%d/%m/%Y %H:%M"), 
                        "Cliente": cliente, "Total": total, "Tipo": tipo,
                        "Detalle": str([x["Producto"] for x in st.session_state.carrito])
                    }])
                    hist = cargar_datos_general(VENTAS_FILE, ["Fecha","Cliente","Total","Tipo","Detalle"])
                    pd.concat([hist, nuevo]).to_csv(VENTAS_FILE, index=False)
                    
                    st.session_state.carrito = []
                    st.success("¡Venta Exitosa!")
                    st.rerun()

# 2. STOCK
with tab_stock:
    df_s = cargar_datos_stock()
    if not df_s.empty:
        df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]

    c_head, c_btn = st.columns([4, 1])
    c_head.subheader("Inventario Maestro")
    c_btn.download_button("📥 Excel", generar_excel(df_s), f"Stock_{date.today()}.xlsx")

    # Tabla Editable
    df_edit = st.data_editor(
        df_s, key="editor_stock", num_rows="dynamic", use_container_width=True, hide_index=True,
        column_order=["Codigo", "Producto", "DISPONIBLE", "Cantidad", "Reservado", "Unidad", "Precio Venta"],
        column_config={
            "Codigo": st.column_config.TextColumn("Cód"),
            "DISPONIBLE": st.column_config.NumberColumn("✅ VENDIBLE", disabled=True, format="%.0f"),
            "Cantidad": st.column_config.NumberColumn("Físico", format="%.0f"),
            "Reservado": st.column_config.NumberColumn("Reservado", format="%.0f"),
            "Precio Venta": st.column_config.NumberColumn("Precio", format="$ %d")
        }
    )
    if st.button("💾 GUARDAR CAMBIOS DE STOCK", type="primary"):
        df_edit.to_csv(STOCK_FILE, index=False)
        st.success("Inventario Actualizado")
        st.rerun()

# 3. PRODUCCION
with tab_prod:
    st.subheader("Control de Fraguado")
    df_prod = cargar_datos_general(PRODUCCION_FILE, ["Fecha_Inicio","Producto","Cantidad","Fecha_Lista","Estado"])
    df_stk = cargar_datos_stock()
    
    with st.form("new_prod"):
        c1, c2, c3, c4 = st.columns([2,1,1,1])
        prod = c1.selectbox("Producto", df_stk["Producto"].unique() if not df_stk.empty else [])
        cant = c2.number_input("Cant", 1)
        fecha = c3.date_input("Fecha Elab.", value=ahora_arg().date())
        dias = c4.number_input("Días", 28)
        if st.form_submit_button("Registrar"):
            fin = fecha + timedelta(days=dias)
            estado = "En Proceso" if (fin - ahora_arg().date()).days > 0 else "Listo"
            nuevo = pd.DataFrame([{"Fecha_Inicio": fecha, "Producto": prod, "Cantidad": cant, "Fecha_Lista": fin, "Estado": estado}])
            pd.concat([df_prod, nuevo]).to_csv(PRODUCCION_FILE, index=False)
            st.rerun()
            
    if not df_prod.empty:
        df_prod["Fecha_Lista"] = pd.to_datetime(df_prod["Fecha_Lista"]).dt.date
        activos = df_prod[df_prod["Estado"] != "Finalizado"]
        st.dataframe(activos, use_container_width=True)

# 4. HISTORIAL
with tab_hist:
    st.subheader("Registro de Ventas")
    st.dataframe(cargar_datos_general(VENTAS_FILE, []), use_container_width=True)

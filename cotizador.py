import streamlit as st
import pandas as pd
import os
import io
from datetime import date, timedelta, datetime
import pytz
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE TEMA ROJO Y BLANCO ---
# Esto fuerza a la aplicación a usar letras rojas y fondo blanco desde la configuración
def configurar_tema_alambrados():
    config_dir = ".streamlit"
    config_path = os.path.join(config_dir, "config.toml")
    
    # Configuramos textColor (texto base) en un rojo oscuro legible (#8B0000)
    # primaryColor (botones/selecciones) en rojo brillante (#D32F2F)
    tema_corporativo = """
[theme]
base="light"
primaryColor="#D32F2F"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#FFEBEE"
textColor="#8B0000" 
font="sans serif"
"""
    if not os.path.exists(config_path):
        try:
            os.makedirs(config_dir, exist_ok=True)
            with open(config_path, "w") as f:
                f.write(tema_corporativo)
        except: pass

configurar_tema_alambrados()

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Alambrados del Carmen", layout="wide", page_icon="🏗️")

# --- 3. CSS PARA CORREGIR TABLAS Y COLORES ---
st.markdown("""
    <style>
        /* Forzar fondo blanco y letras rojas/oscuras */
        .stApp {
            background-color: white !important;
            color: #8B0000 !important;
        }
        
        /* Títulos bien rojos */
        h1, h2, h3, h4 {
            color: #D32F2F !important;
        }

        /* CORRECCIÓN DE TABLAS (Edición tipo Excel) */
        /* Asegura que el texto dentro de la tabla sea negro/oscuro para leer bien */
        [data-testid="stDataFrame"] div, [data-testid="stDataEditor"] div {
            color: #333333 !important; 
            background-color: white !important;
        }
        /* Encabezados de tabla en rojo */
        [data-testid="stDataFrame"] thead th, [data-testid="stDataEditor"] thead th {
            color: #D32F2F !important;
        }

        /* Barra lateral con toque rojo suave */
        [data-testid="stSidebar"] {
            background-color: #FFEBEE !important; /* Rojo muy pálido */
            border-right: 1px solid #ffcdd2;
        }
        
        /* Botones rojos sólidos */
        .stButton button {
            background-color: #D32F2F !important;
            color: white !important;
            border-radius: 5px;
            font-weight: bold;
        }
        .stButton button:hover {
            background-color: #B71C1C !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- RUTAS Y ARCHIVOS ---
STOCK_FILE = "stock_del_carmen.csv"
GASTOS_FILE = "gastos_del_carmen.csv"
VENTAS_FILE = "ventas_del_carmen.csv"
PRODUCCION_FILE = "produccion_del_carmen.csv"
LOGO_FILE = "alambrados.jpeg"

# --- LISTA EXACTA DEL EXCEL SUBIDO ---
PRODUCTOS_INICIALES = [
    {'Codigo': '97', 'Producto': 'ADICIONAL PINCHES 20.000', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '6', 'Producto': 'BOYERITO IMPORTADO X 1000', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '3', 'Producto': 'CONCERTINA DOBLE CRUZADA X 45', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '2', 'Producto': 'CONCERTINA SIMPLE', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '11', 'Producto': 'DECO 1.50', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '0', 'Producto': 'DECO 1.80', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '33', 'Producto': 'ESPARRAGOS', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '25', 'Producto': 'ESQUINERO OLIMPICO', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 18000, 'Precio Venta': 39000, 'Stock Minimo': 0},
    {'Codigo': '2', 'Producto': 'ESQUINERO RECTO', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 32000, 'Stock Minimo': 0},
    {'Codigo': '15', 'Producto': 'GALVA 14 X KILO', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'kg', 'Precio Costo': 0, 'Precio Venta': 6800, 'Stock Minimo': 0},
    {'Codigo': '5', 'Producto': 'GALVA 18', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'kg', 'Precio Costo': 0, 'Precio Venta': 11900, 'Stock Minimo': 0},
    {'Codigo': '31', 'Producto': 'GANCHOS ESTIRATEJIDOS 5/16', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 2100, 'Stock Minimo': 0},
    {'Codigo': '15', 'Producto': 'OVALADO X MAYOR X 1000', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 290000, 'Stock Minimo': 0},
    {'Codigo': '32', 'Producto': 'PALOMITAS', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 2100, 'Stock Minimo': 0},
    {'Codigo': '24', 'Producto': 'PINCHES X METRO PINCHOSOS', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'm', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '41', 'Producto': 'PLANCHUELA 1.00', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 4800, 'Stock Minimo': 0},
    {'Codigo': '40', 'Producto': 'PLANCHUELA 1.20', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 5100, 'Stock Minimo': 0},
    {'Codigo': '35', 'Producto': 'PLANCHUELA 1.50', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 5800, 'Stock Minimo': 0},
    {'Codigo': '34', 'Producto': 'PLANCHUELA 2.00', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 7999, 'Stock Minimo': 0},
    {'Codigo': '47', 'Producto': 'PORTON 3.00 X 1.80 BLACK', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 360000, 'Stock Minimo': 0},
    {'Codigo': '9', 'Producto': 'PORTON DE CANO X 4.00', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 3600000, 'Stock Minimo': 0},
    {'Codigo': '10', 'Producto': 'PORTON INDUSTRIAL X 4.00', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 499999, 'Stock Minimo': 0},
    {'Codigo': '51', 'Producto': 'PORTON LIVIANO 1.80 X 3.00 CANO', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 260000, 'Stock Minimo': 0},
    {'Codigo': '53', 'Producto': 'PORTON LIVIANO 1.80X 3.00', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '11', 'Producto': 'PORTON SIMPLE X 3.00', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '54', 'Producto': 'POSTE DE MADERA', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 15000, 'Stock Minimo': 0},
    {'Codigo': '27', 'Producto': 'POSTE OLIMPICO', 'Cantidad': 10, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 17999, 'Stock Minimo': 0},
    {'Codigo': '28', 'Producto': 'POSTE RECTO', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 16999, 'Stock Minimo': 0},
    {'Codigo': '57', 'Producto': 'POSTE REDONDE ECO OBRA', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 15000, 'Stock Minimo': 0},
    {'Codigo': '14', 'Producto': 'PUA X MAYOR X500', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '43', 'Producto': 'PUA X METRO', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'm', 'Precio Costo': 0, 'Precio Venta': 550, 'Stock Minimo': 0},
    {'Codigo': '16', 'Producto': 'PUERTITA CLASICA 1.50', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 1589000, 'Stock Minimo': 0},
    {'Codigo': '12', 'Producto': 'PUERTITA CORAZON 1.5 X 1.00', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 162800, 'Stock Minimo': 0},
    {'Codigo': '13', 'Producto': 'PUERTITA CRUZ REFORZADA 2.00 X 1.00', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 199800, 'Stock Minimo': 0},
    {'Codigo': '7', 'Producto': 'PUERTITA LIVINA 1.00 X 1.80', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 125300, 'Stock Minimo': 0},
    {'Codigo': '26', 'Producto': 'PUNTAL', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 13900, 'Stock Minimo': 0},
    {'Codigo': 'R16', 'Producto': 'RECOCIDO 16', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'kg', 'Precio Costo': 0, 'Precio Venta': 4900, 'Stock Minimo': 0},
    {'Codigo': 'REF', 'Producto': 'REFUERZO', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 39000, 'Stock Minimo': 0},
    {'Codigo': '55', 'Producto': 'TEJIDO 1.50', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'm', 'Precio Costo': 0, 'Precio Venta': 59000, 'Stock Minimo': 0},
    {'Codigo': '19', 'Producto': 'TEJIDO 2.00 X METRO', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'm', 'Precio Costo': 0, 'Precio Venta': 74999, 'Stock Minimo': 0},
    {'Codigo': '59', 'Producto': 'TEJIDO DE OBRA 1.50', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'm', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '63', 'Producto': 'TEJIDO DE OBRA 1.80', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'm', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '50', 'Producto': 'TEJIDO DEL 12 - 2 PULGADAS', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'm', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '18', 'Producto': 'TEJIDO RECU 1.8', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'm', 'Precio Costo': 0, 'Precio Venta': 0, 'Stock Minimo': 0},
    {'Codigo': '39', 'Producto': 'TEJIDO ROMBITO 2 PULGADAS', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'm', 'Precio Costo': 0, 'Precio Venta': 69999, 'Stock Minimo': 0},
    {'Codigo': '29', 'Producto': 'Torniquete', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 1999, 'Precio Venta': 3500, 'Stock Minimo': 0},
    {'Codigo': '1', 'Producto': 'liso', 'Cantidad': 0, 'Reservado': 0, 'Unidad': 'un.', 'Precio Costo': 0, 'Precio Venta': 360, 'Stock Minimo': 0}
]

# --- FUNCIONES ---
def ahora_arg():
    try: return datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
    except: return datetime.now()

def generar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Stock')
    return output.getvalue()

def cargar_datos_stock():
    # Inicialización robusta con la lista del Excel
    if not os.path.exists(STOCK_FILE):
        df_init = pd.DataFrame(PRODUCTOS_INICIALES)
        df_init.to_csv(STOCK_FILE, index=False)
    
    try:
        df = pd.read_csv(STOCK_FILE)
        if df.empty or len(df) < 5:
            df = pd.DataFrame(PRODUCTOS_INICIALES)
            df.to_csv(STOCK_FILE, index=False)
    except:
        df = pd.DataFrame(PRODUCTOS_INICIALES)
        df.to_csv(STOCK_FILE, index=False)

    df["Codigo"] = df["Codigo"].fillna("").astype(str)
    df["Producto"] = df["Producto"].fillna("").astype(str)
    df["Unidad"] = df["Unidad"].fillna("un.").astype(str)
    for col in ["Cantidad", "Reservado", "Precio Costo", "Precio Venta", "Stock Minimo"]:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df

def cargar_datos_general(archivo, cols):
    if not os.path.exists(archivo): return pd.DataFrame(columns=cols)
    return pd.read_csv(archivo)

# --- PDF ---
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 170, 8, 30) 
            except: pass
        self.set_font('Arial', 'B', 15)
        self.set_text_color(183, 28, 28)
        self.cell(80)
        self.cell(30, 10, 'PRESUPUESTO', 0, 0, 'C')
        self.ln(20)
        self.set_text_color(0, 0, 0)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Alambrados del Carmen S.A.', 0, 0, 'C')

def generar_pdf(cliente, items, total, tipo_venta):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    fecha_hora = ahora_arg().strftime("%d/%m/%Y %H:%M")
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {fecha_hora} ({tipo_venta})", ln=True)
    pdf.ln(10)
    pdf.set_fill_color(211, 47, 47) 
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(20, 10, "Cod", 1, 0, 'C', True)
    pdf.cell(90, 10, "Producto", 1, 0, 'C', True)
    pdf.cell(20, 10, "Cant", 1, 0, 'C', True)
    pdf.cell(30, 10, "Unit", 1, 0, 'C', True)
    pdf.cell(30, 10, "Total", 1, 1, 'C', True)
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

if 'carrito' not in st.session_state: st.session_state.carrito = []

# --- BARRA LATERAL ---
with st.sidebar:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, use_container_width=True)
    else: st.title("AC")
    st.write("---")
    st.caption(f"📅 {ahora_arg().strftime('%d/%m/%Y %H:%M')}")
    st.write("---")
    with st.expander("⚙️ Admin"):
        if st.button("♻️ Restaurar Base de Datos"):
             if os.path.exists(STOCK_FILE): os.remove(STOCK_FILE)
             st.success("¡Datos del Excel restaurados! Recargá la página.")
             st.rerun()

# --- INTERFAZ ---
st.title("Gestión Comercial")
tab_cot, tab_stock, tab_prod, tab_hist = st.tabs(["📝 Cotizador", "💰 Stock y Costos", "🏭 Producción", "📊 Historial"])

# 1. COTIZADOR
with tab_cot:
    df_s = cargar_datos_stock()
    if df_s.empty:
         st.error("⚠️ Error cargando stock. Usá el botón Restaurar.")
    else:
        if "Reservado" not in df_s.columns: df_s["Reservado"] = 0.0
        df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]

        col_izq, col_der = st.columns([1, 1])
        with col_izq:
            st.subheader("Datos del Pedido")
            cliente = st.text_input("Nombre Cliente")
            st.write("")
            opciones = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']} (Disp: {x['DISPONIBLE']:.0f})", axis=1)
            sel_prod = st.selectbox("Buscar Producto:", ["Seleccionar..."] + list(opciones))
            c_cant, c_add = st.columns([1, 2])
            cant = c_cant.number_input("Cantidad", min_value=1.0, value=1.0)
            
            if c_add.button("➕ AGREGAR", use_container_width=True) and sel_prod != "Seleccionar...":
                cod = sel_prod.split("]")[0].replace("[", "")
                fila = df_s[df_s["Codigo"] == cod].iloc[0]
                st.session_state.carrito.append({
                    "Codigo": fila["Codigo"], "Producto": fila["Producto"],
                    "Cantidad": cant, "Precio": fila["Precio Venta"],
                    "Subtotal": cant * fila["Precio Venta"]
                })
                st.rerun()

        with col_der:
            st.subheader("Carrito")
            if st.session_state.carrito:
                st.markdown("---")
                # Encabezados manuales
                k1, k2, k3, k4 = st.columns([4, 2, 2, 1])
                k1.markdown("**Producto**")
                k2.markdown("**Cant**")
                k3.markdown("**Subtotal**")
                
                for i, item in enumerate(st.session_state.carrito):
                    c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
                    c1.write(item["Producto"])
                    c2.write(f"{item['Cantidad']:.1f}")
                    c3.write(f"${item['Subtotal']:.0f}")
                    if c4.button("❌", key=f"del_{i}"):
                        st.session_state.carrito.pop(i)
                        st.rerun()
                
                st.markdown("---")
                total = sum(item['Subtotal'] for item in st.session_state.carrito)
                c_tot, c_trash = st.columns([3,1])
                c_tot.metric("TOTAL", f"${total:,.0f}")
                
                if c_trash.button("🗑️ Vaciar"):
                    st.session_state.carrito = []
                    st.rerun()
                
                st.divider()
                tipo = st.radio("Destino:", ["Entrega Inmediata", "Dejar en Acopio"], horizontal=True)
                c_pdf, c_ok = st.columns(2)
                pdf_bytes = generar_pdf(cliente, st.session_state.carrito, total, tipo)
                c_pdf.download_button("📄 Presupuesto", pdf_bytes, f"P_{cliente}.pdf", "application/pdf", use_container_width=True)
                if c_ok.button("✅ VENDER", type="primary", use_container_width=True):
                    for item in st.session_state.carrito:
                        idx = df_s.index[df_s["Codigo"] == item["Codigo"]].tolist()
                        if idx:
                            i = idx[0]
                            if "Acopio" in tipo: df_s.at[i, "Reservado"] += item["Cantidad"]
                            else: df_s.at[i, "Cantidad"] -= item["Cantidad"]
                    df_s.to_csv(STOCK_FILE, index=False)
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
            else:
                st.info("Carrito vacío.")

# 2. STOCK (TABLA EDITABLE TIPO EXCEL)
with tab_stock:
    df_s = cargar_datos_stock()
    if not df_s.empty:
        df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]
        df_s["Ganancia Unitaria"] = df_s["Precio Venta"] - df_s["Precio Costo"]

    st.subheader("Tablero Financiero y Stock")
    st.info("💡 Editá directamente en la tabla como si fuera un Excel. Al terminar, apretá 'GUARDAR CAMBIOS'.")
    
    c_dl, c_save = st.columns([1, 4])
    c_dl.download_button("📥 Bajar Excel", generar_excel(df_s), f"Stock_{date.today()}.xlsx")
    
    # TABLA EDITABLE PRINCIPAL (CONFIGURACIÓN EXCEL)
    df_edit = st.data_editor(
        df_s, 
        key="editor_stock", 
        num_rows="dynamic", # Permite agregar filas abajo
        use_container_width=True, 
        hide_index=True,
        column_order=["Codigo", "Producto", "DISPONIBLE", "Cantidad", "Reservado", "Precio Costo", "Precio Venta", "Ganancia Unitaria"],
        column_config={
            "Codigo": st.column_config.TextColumn("Cód"),
            # DISPONIBLE y GANANCIA son cálculos, mejor no editarlos para evitar confusiones
            "DISPONIBLE": st.column_config.NumberColumn("✅ Disp.", disabled=True, format="%.0f"),
            "Ganancia Unitaria": st.column_config.NumberColumn("Ganancia ($)", disabled=True, format="$ %d"),
            # ESTOS SÍ SE PUEDEN EDITAR:
            "Producto": st.column_config.TextColumn("Producto", required=True),
            "Cantidad": st.column_config.NumberColumn("Físico", format="%.0f"),
            "Reservado": st.column_config.NumberColumn("Reservado", format="%.0f"),
            "Precio Costo": st.column_config.NumberColumn("Costo ($)", format="$ %d"),
            "Precio Venta": st.column_config.NumberColumn("Venta ($)", format="$ %d"),
        }
    )
    
    if c_save.button("💾 GUARDAR CAMBIOS MASIVOS", type="primary"):
        # Guardamos solo las columnas reales, descartamos las calculadas
        cols_to_save = ["Codigo", "Producto", "Cantidad", "Reservado", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
        # Nos aseguramos que las columnas existan en la edición
        for col in cols_to_save:
            if col not in df_edit.columns:
                df_edit[col] = 0
        df_final = df_edit[cols_to_save] 
        df_final.to_csv(STOCK_FILE, index=False)
        st.success("¡Base de Datos Actualizada!")
        st.rerun()

# 3. PRODUCCION
with tab_prod:
    st.subheader("🏭 Control de Producción y Fraguado")
    
    df_prod = cargar_datos_general(PRODUCCION_FILE, ["Fecha_Inicio","Producto","Cantidad","Fecha_Lista","Estado"])
    df_stk = cargar_datos_stock()
    
    with st.form("new_prod"):
        c1, c2 = st.columns(2)
        prod = c1.selectbox("Producto:", df_stk["Producto"].unique() if not df_stk.empty else [])
        cant = c2.number_input("Cantidad Fabricada:", 1)
        c3, c4 = st.columns(2)
        fecha = c3.date_input("Fecha Elaboración:", value=ahora_arg().date())
        dias = c4.number_input("Días Fraguado:", value=28, help="Poné 0 si ya está listo.")
        
        if st.form_submit_button("Registrar Producción"):
            fin = fecha + timedelta(days=dias)
            estado = "En Proceso" if dias > 0 and (fin - ahora_arg().date()).days > 0 else "Listo"
            nuevo = pd.DataFrame([{"Fecha_Inicio": fecha, "Producto": prod, "Cantidad": cant, "Fecha_Lista": fin, "Estado": estado}])
            pd.concat([df_prod, nuevo]).to_csv(PRODUCCION_FILE, index=False)
            st.rerun()
            
    if not df_prod.empty:
        df_prod["Fecha_Lista"] = pd.to_datetime(df_prod["Fecha_Lista"]).dt.date
        activos = df_prod[df_prod["Estado"] != "Finalizado"]
        
        for index, row in activos.iterrows():
            hoy = ahora_arg().date()
            falta = (row["Fecha_Lista"] - hoy).days
            with st.container(border=True):
                c_txt, c_btn = st.columns([4, 1])
                if falta <= 0:
                    c_txt.success(f"✅ **LISTO:** {row['Cantidad']}x {row['Producto']} (Elab: {row['Fecha_Inicio']})")
                    if c_btn.button("📥 A STOCK", key=f"p_{index}"):
                        df_s = cargar_datos_stock()
                        idx = df_s.index[df_s["Producto"] == row['Producto']].tolist()
                        if idx:
                            df_s.at[idx[0], "Cantidad"] += row['Cantidad']
                            df_s.to_csv(STOCK_FILE, index=False)
                            df_prod.at[index, "Estado"] = "Finalizado"
                            df_prod.to_csv(PRODUCCION_FILE, index=False)
                            st.rerun()
                else:
                    c_txt.info(f"⏳ **FRAGUANDO:** {row['Cantidad']}x {row['Producto']} | Faltan {falta} días")

# 4. HISTORIAL
with tab_hist:
    st.subheader("Registro de Ventas")
    st.dataframe(cargar_datos_general(VENTAS_FILE, []), use_container_width=True)

import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta, datetime
import pytz # Librería para Zona Horaria
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Alambrados del Carmen", layout="wide", page_icon="🏗️")

# --- RUTAS Y ARCHIVOS ---
STOCK_FILE = "stock_del_carmen.csv"
GASTOS_FILE = "gastos_del_carmen.csv"
VENTAS_FILE = "ventas_del_carmen.csv"
PRODUCCION_FILE = "produccion_del_carmen.csv"
LOGO_FILE = "alambradoslogo.jpeg"

# --- FUNCIÓN HORA ARGENTINA ---
def ahora_arg():
    # Define la zona horaria de Buenos Aires
    tz = pytz.timezone('America/Argentina/Buenos_Aires')
    return datetime.now(tz)

# --- LISTA EXACTA DE PRODUCTOS ---
PRODUCTOS_INICIALES = [
    {"Codigo": "3", "Producto": "ADICIONAL PINCHES 20.000", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "6", "Producto": "BOYERITO IMPORTADO X 1000", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "3", "Producto": "CONCERTINA DOBLE CRUZADA X 45", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "2", "Producto": "CONCERTINA SIMPLE", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "1", "Producto": "DECO 1.50", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "0", "Producto": "DECO 1.80", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "3", "Producto": "ESPARRAGOS", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "25", "Producto": "ESQUINERO OLIMPICO", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "2", "Producto": "ESQUINERO RECTO", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "15", "Producto": "GALVA 14 X KILO", "Unidad": "kg", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "5", "Producto": "GALVA 18", "Unidad": "kg", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "31", "Producto": "GANCHOS ESTIRATEJIDOS 5/16", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "15", "Producto": "OVALADO X MAYOR X 1000", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "32", "Producto": "PALOMITAS", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "24", "Producto": "PINCHES X METRO PINCHOSOS", "Unidad": "m", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "41", "Producto": "PLANCHUELA 1.00", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "40", "Producto": "PLANCHUELA 1.20", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "35", "Producto": "PLANCHUELA 1.50", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "34", "Producto": "PLANCHUELA 2.00", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "47", "Producto": "PORTON 3.00 X 1.80 BLACK", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "9", "Producto": "PORTON DE CANO X 4.00", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "10", "Producto": "PORTON INDUSTRIAL X 4.00", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "51", "Producto": "PORTON LIVIANO 1.80 X 3.00 CANO", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "53", "Producto": "PORTON LIVIANO 1.80X 3.00", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "11", "Producto": "PORTON SIMPLE X 3.00", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "54", "Producto": "POSTE DE MADERA", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "27", "Producto": "POSTE OLIMPICO", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "28", "Producto": "POSTE RECTO", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "57", "Producto": "POSTE REDONDE ECO OBRA", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "14", "Producto": "PUA X MAYOR X500", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "43", "Producto": "PUA X METRO", "Unidad": "m", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "16", "Producto": "PUERTITA CLASICA 1.50", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "12", "Producto": "PUERTITA CORAZON 1.5 X 1.00", "Unidad": "un.", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "55", "Producto": "TEJIDO 1.50", "Unidad": "m", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "19", "Producto": "TEJIDO 2.00 X METRO", "Unidad": "m", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "59", "Producto": "TEJIDO DE OBRA 1.50", "Unidad": "m", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "63", "Producto": "TEJIDO DE OBRA 1.80", "Unidad": "m", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "50", "Producto": "TEJIDO DEL 12 - 2 PULGADAS", "Unidad": "m", "Precio Venta": 0, "Cantidad": 0},
    {"Codigo": "18", "Producto": "TEJIDO RECU 1.8", "Unidad": "m", "Precio Venta": 0, "Cantidad": 0}
]

# --- INICIALIZACIÓN ---
def inicializar_archivos():
    cols_stock = ["Codigo", "Producto", "Cantidad", "Reservado", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    
    if not os.path.exists(STOCK_FILE):
        df_init = pd.DataFrame(PRODUCTOS_INICIALES)
        for col in cols_stock:
            if col not in df_init.columns: df_init[col] = 0.0
        df_init.to_csv(STOCK_FILE, index=False)
    
    if not os.path.exists(PRODUCCION_FILE):
        pd.DataFrame(columns=["Fecha_Inicio", "Producto", "Cantidad", "Dias_Fraguado", "Fecha_Lista", "Estado"]).to_csv(PRODUCCION_FILE, index=False)
    if not os.path.exists(GASTOS_FILE):
        pd.DataFrame(columns=["Fecha", "Insumo", "Cantidad", "Monto"]).to_csv(GASTOS_FILE, index=False)
    if not os.path.exists(VENTAS_FILE):
        pd.DataFrame(columns=["Fecha", "Cliente", "Total", "Tipo_Entrega", "Detalle"]).to_csv(VENTAS_FILE, index=False)

def cargar_datos_stock():
    df = pd.read_csv(STOCK_FILE)
    df["Codigo"] = df["Codigo"].fillna("").astype(str)
    df["Producto"] = df["Producto"].fillna("").astype(str)
    df["Unidad"] = df["Unidad"].fillna("un.").astype(str)
    cols_num = ["Cantidad", "Reservado", "Precio Costo", "Precio Venta", "Stock Minimo"]
    for col in cols_num:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df

def cargar_datos_general(archivo):
    return pd.read_csv(archivo)

# --- CLASE PDF ---
class PDF(FPDF):
    def header(self):
        # Logo a la DERECHA
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 170, 8, 30) 
            except: pass
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'PRESUPUESTO', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Alambrados del Carmen S.A.', 0, 0, 'C')

    def water_mark(self):
        if os.path.exists(LOGO_FILE):
            try:
                self.set_alpha(0.15)
                self.image(LOGO_FILE, x=55, y=80, w=100)
                self.set_alpha(1)
            except: pass

def generar_pdf(cliente, items, total, tipo_venta):
    pdf = PDF()
    pdf.add_page()
    pdf.water_mark()
    pdf.set_font("Arial", size=12)
    
    # FECHA ARGENTINA EXACTA
    fecha_hora = ahora_arg().strftime("%d/%m/%Y %H:%M")
    
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {fecha_hora} ({tipo_venta})", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(20, 10, "Cod", 1)
    pdf.cell(90, 10, "Producto", 1)
    pdf.cell(20, 10, "Cant", 1)
    pdf.cell(30, 10, "Unit", 1)
    pdf.cell(30, 10, "Total", 1)
    pdf.ln()
    
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
    pdf.cell(160, 10, "TOTAL", 0)
    pdf.cell(30, 10, f"${total:,.0f}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1')

inicializar_archivos()
if 'carrito' not in st.session_state: st.session_state.carrito = []

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1055/1055644.png", width=50)
    st.header("Herramientas")
    
    # Muestra la hora para verificar
    hora_actual = ahora_arg().strftime("%H:%M")
    st.caption(f"🕒 Hora Arg: {hora_actual}")

    st.warning("Zona de Peligro")
    if st.button("♻️ RESTAURAR FABRICA"):
        df_reset = pd.DataFrame(PRODUCTOS_INICIALES)
        cols_stock = ["Codigo", "Producto", "Cantidad", "Reservado", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
        for col in cols_stock:
            if col not in df_reset.columns: df_reset[col] = 0.0
        df_reset.to_csv(STOCK_FILE, index=False)
        st.success("¡Restaurado!")
        st.rerun()

# --- INTERFAZ ---
st.title("🏗️ Alambrados del Carmen S.A.")
tab_cot, tab_stock, tab_prod, tab_hist = st.tabs(["📝 Cotizador", "📦 Stock", "🏭 Producción", "📊 Historial"])

# TAB 1: COTIZADOR
with tab_cot:
    df_s = cargar_datos_stock()
    df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]
    col_izq, col_der = st.columns([1, 1])
    
    with col_izq:
        st.subheader("1. Pedido")
        cliente = st.text_input("Cliente")
        st.write("---")
        opciones = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']} (Disp: {x['DISPONIBLE']:.0f})", axis=1)
        sel_prod = st.selectbox("Producto:", ["Seleccionar..."] + list(opciones))
        c_cant, c_add = st.columns([1, 2])
        cant = c_cant.number_input("Cantidad", min_value=1.0, value=1.0)
        
        if c_add.button("➕ Agregar") and sel_prod != "Seleccionar...":
            cod = sel_prod.split("]")[0].replace("[", "")
            fila = df_s[df_s["Codigo"] == cod].iloc[0]
            if cant > fila["DISPONIBLE"]: st.toast(f"⚠️ Stock bajo: Quedan {fila['DISPONIBLE']}", icon="⚠️")
            
            st.session_state.carrito.append({
                "Codigo": fila["Codigo"], "Producto": fila["Producto"],
                "Cantidad": cant, "Precio": fila["Precio Venta"],
                "Subtotal": cant * fila["Precio Venta"]
            })
            st.rerun()

    with col_der:
        st.subheader("2. Detalle")
        if st.session_state.carrito:
            df_c = pd.DataFrame(st.session_state.carrito)
            st.dataframe(df_c[["Producto", "Cantidad", "Subtotal"]], hide_index=True, use_container_width=True)
            total = df_c["Subtotal"].sum()
            st.metric("Total", f"${total:,.0f}")
            
            if st.button("Vaciar Carrito"):
                st.session_state.carrito = []
                st.rerun()
            
            st.markdown("---")
            tipo = st.radio("Operación:", ["Entrega Inmediata", "Acopio / Reserva"])
            c_p, c_v = st.columns(2)
            pdf = generar_pdf(cliente, st.session_state.carrito, total, tipo)
            c_p.download_button("📄 PDF", pdf, f"P_{cliente}.pdf", "application/pdf")
            
            if c_v.button("✅ Confirmar Venta", type="primary"):
                for item in st.session_state.carrito:
                    idx = df_s.index[df_s["Codigo"] == item["Codigo"]].tolist()
                    if idx:
                        i = idx[0]
                        if "Reserva" in tipo: df_s.at[i, "Reservado"] += item["Cantidad"]
                        else: df_s.at[i, "Cantidad"] -= item["Cantidad"]
                df_s.to_csv(STOCK_FILE, index=False)
                
                # GUARDAR CON FECHA Y HORA EXACTA
                fecha_hora_str = ahora_arg().strftime("%d/%m/%Y %H:%M")
                nuevo = pd.DataFrame([{
                    "Fecha": fecha_hora_str, "Cliente": cliente, "Total": total,
                    "Tipo_Entrega": "Reserva" if "Reserva" in tipo else "Inmediata",
                    "Detalle": str([x["Producto"] for x in st.session_state.carrito])
                }])
                pd.concat([cargar_datos_general(VENTAS_FILE), nuevo]).to_csv(VENTAS_FILE, index=False)
                st.session_state.carrito = []
                st.success("¡Venta Registrada!")
                st.balloons()
                st.rerun()

# TAB 2: STOCK
with tab_stock:
    st.header("📦 Inventario")
    df_s = cargar_datos_stock()
    df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]
    
    with st.expander("✨ Crear Nuevo Producto (Si no está en la lista)", expanded=False):
        c_new1, c_new2, c_new3 = st.columns(3)
        new_cod = c_new1.text_input("Código Nuevo")
        new_nom = c_new2.text_input("Nombre Producto")
        new_uni = c_new3.selectbox("Unidad", ["un.", "m", "kg", "pack"])
        if st.button("Crear Producto"):
            if new_cod and new_nom:
                nuevo_prod = pd.DataFrame([{
                    "Codigo": new_cod, "Producto": new_nom, "Unidad": new_uni,
                    "Cantidad": 0.0, "Reservado": 0.0, "Precio Costo": 0.0,
                    "Precio Venta": 0.0, "Stock Minimo": 0.0
                }])
                df_s = pd.concat([df_s, nuevo_prod], ignore_index=True)
                df_s.to_csv(STOCK_FILE, index=False)
                st.success(f"Creado: {new_nom}")
                st.rerun()
            else: st.error("Falta código o nombre.")
    
    with st.expander("⚡ Cargar Stock (Lo que llega del proveedor)"):
        c1, c2, c3 = st.columns([2, 1, 1])
        opc = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']}", axis=1)
        sel = c1.selectbox("Elegir Producto:", opc)
        num = c2.number_input("Cantidad que llegó:", min_value=1.0)
        if c3.button("📥 Sumar"):
            cod = sel.split("]")[0].replace("[", "")
            idx = df_s.index[df_s["Codigo"] == cod].tolist()
            if idx:
                df_s.at[idx[0], "Cantidad"] += num
                df_s.to_csv(STOCK_FILE, index=False)
                st.rerun()

    st.subheader("Listado Maestro")
    df_edit = st.data_editor(
        df_s, key="stock_editor_final", num_rows="dynamic", use_container_width=True, hide_index=True,
        column_order=["Codigo", "Producto", "DISPONIBLE", "Cantidad", "Reservado", "Unidad", "Precio Venta"],
        column_config={
            "Codigo": st.column_config.TextColumn("Cód"),
            "DISPONIBLE": st.column_config.NumberColumn("✅ Disp.", disabled=True, format="%.0f"),
            "Cantidad": st.column_config.NumberColumn("Físico", format="%.0f"),
            "Reservado": st.column_config.NumberColumn("Reserva", format="%.0f"),
            "Precio Venta": st.column_config.NumberColumn("Precio", format="$ %d")
        }
    )
    if st.button("💾 Guardar Todo"):
        df_edit.to_csv(STOCK_FILE, index=False)
        st.success("Guardado")
        st.rerun()

# TAB 3: PRODUCCIÓN
with tab_prod:
    st.header("🏭 Fraguado Inteligente")
    st.markdown("Si ya fabricaste hace unos días, cambiá la fecha para que el cálculo sea correcto.")
    
    df_p = cargar_datos_general(PRODUCCION_FILE)
    df_s_act = cargar_datos_stock()
    
    with st.form("form_prod"):
        c1, c2 = st.columns(2)
        p_fab = c1.selectbox("Producto Fabricado:", df_s_act["Producto"].unique())
        n_fab = c2.number_input("Cantidad:", min_value=1.0)
        c3, c4 = st.columns(2)
        
        # Fecha Manual: Por defecto HOY (Hora Argentina), pero editable
        fecha_elab = c3.date_input("Fecha de Elaboración", value=ahora_arg().date())
        dias_frag = c4.number_input("Días de Fraguado", value=28, min_value=0)
        
        if st.form_submit_button("🚀 Registrar Producción"):
            fecha_fin = fecha_elab + timedelta(days=dias_frag)
            
            # Cálculo exacto usando la fecha elegida vs fecha actual real
            dias_restantes = (fecha_fin - ahora_arg().date()).days
            
            estado = "En Proceso" if dias_restantes > 0 else "Listo"
            nuevo = pd.DataFrame([{
                "Fecha_Inicio": fecha_elab, "Producto": p_fab, "Cantidad": n_fab,
                "Dias_Fraguado": dias_frag, "Fecha_Lista": fecha_fin, "Estado": estado
            }])
            pd.concat([df_p, nuevo]).to_csv(PRODUCCION_FILE, index=False)
            st.success(f"Registrado. Liberación estimada: {fecha_fin}")
            st.rerun()

    st.markdown("---")
    st.subheader("Estado del Fraguado")
    
    if not df_p.empty:
        df_p["Fecha_Lista"] = pd.to_datetime(df_p["Fecha_Lista"]).dt.date
        df_p = df_p[df_p["Estado"] != "Finalizado"]
        
        for index, row in df_p.iterrows():
            hoy = ahora_arg().date()
            falta = (row["Fecha_Lista"] - hoy).days
            
            with st.container(border=True):
                col_txt, col_act = st.columns([4, 1])
                with col_txt:
                    if falta <= 0:
                        st.success(f"✅ **LISTO PARA STOCK:** {row['Cantidad']}x {row['Producto']} (Elab: {row['Fecha_Inicio']})")
                    else:
                        st.info(f"⏳ **FRAGUANDO:** {row['Cantidad']}x {row['Producto']} | Faltan **{falta} días** (Libera: {row['Fecha_Lista']})")
                with col_act:
                    if falta <= 0:
                        if st.button("📥 A STOCK", key=f"lib_{index}"):
                            df_stk = cargar_datos_stock()
                            idx = df_stk.index[df_stk["Producto"] == row['Producto']].tolist()
                            if idx:
                                df_stk.at[idx[0], "Cantidad"] += row['Cantidad']
                                df_stk.to_csv(STOCK_FILE, index=False)
                                df_p.at[index, "Estado"] = "Finalizado"
                                df_p.to_csv(PRODUCCION_FILE, index=False)
                                st.rerun()
    else:
        st.info("No hay producción en proceso.")

# TAB 4: HISTORIAL
with tab_hist:
    st.header("Historial")
    st.dataframe(cargar_datos_general(VENTAS_FILE), use_container_width=True)

import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Alambrados del Carmen", layout="wide", page_icon="🏗️")

# --- RUTAS Y ARCHIVOS ---
STOCK_FILE = "stock_del_carmen.csv"
GASTOS_FILE = "gastos_del_carmen.csv"
VENTAS_FILE = "ventas_del_carmen.csv"
PRODUCCION_FILE = "produccion_del_carmen.csv"
LOGO_FILE = "alambradoslogo.jpeg"

# --- LISTA DE PRODUCTOS INICIAL (Tu lista real) ---
PRODUCTOS_INICIALES = [
    {"Codigo": "3", "Producto": "ADICIONAL PINCHES 20.000", "Unidad": "un."},
    {"Codigo": "6", "Producto": "BOYERITO IMPORTADO X 1000", "Unidad": "un."},
    {"Codigo": "3", "Producto": "CONCERTINA DOBLE CRUZADA X 45", "Unidad": "un."},
    {"Codigo": "2", "Producto": "CONCERTINA SIMPLE", "Unidad": "un."},
    {"Codigo": "1", "Producto": "DECO 1.50", "Unidad": "un."},
    {"Codigo": "0", "Producto": "DECO 1.80", "Unidad": "un."},
    {"Codigo": "25", "Producto": "ESQUINERO OLIMPICO", "Unidad": "un."},
    {"Codigo": "2", "Producto": "ESQUINERO RECTO", "Unidad": "un."},
    {"Codigo": "15", "Producto": "GALVA 14 X KILO", "Unidad": "kg"},
    {"Codigo": "41", "Producto": "PLANCHUELA 1.00", "Unidad": "un."},
    {"Codigo": "40", "Producto": "PLANCHUELA 1.20", "Unidad": "un."},
    {"Codigo": "35", "Producto": "PLANCHUELA 1.50", "Unidad": "un."},
    {"Codigo": "47", "Producto": "PORTON 3.00 X 1.80 BLACK", "Unidad": "un."},
    {"Codigo": "9", "Producto": "PORTON DE CANO X 4.00", "Unidad": "un."},
    {"Codigo": "54", "Producto": "POSTE DE MADERA", "Unidad": "un."},
    {"Codigo": "27", "Producto": "POSTE OLIMPICO", "Unidad": "un."},
    {"Codigo": "28", "Producto": "POSTE RECTO", "Unidad": "un."},
    {"Codigo": "57", "Producto": "POSTE REDONDE ECO OBRA", "Unidad": "un."},
    {"Codigo": "14", "Producto": "PUA X MAYOR X500", "Unidad": "un."},
    {"Codigo": "43", "Producto": "PUA X METRO", "Unidad": "m"},
    {"Codigo": "16", "Producto": "PUERTITA CLASICA 1.50", "Unidad": "un."},
    {"Codigo": "55", "Producto": "TEJIDO 1.50", "Unidad": "m"},
    {"Codigo": "19", "Producto": "TEJIDO 2.00 X METRO", "Unidad": "m"},
    {"Codigo": "59", "Producto": "TEJIDO DE OBRA 1.50", "Unidad": "m"},
    {"Codigo": "63", "Producto": "TEJIDO DE OBRA 1.80", "Unidad": "m"},
    {"Codigo": "50", "Producto": "TEJIDO DEL 12 - 2 PULGADAS", "Unidad": "m"},
    {"Codigo": "18", "Producto": "TEJIDO RECU 1.8", "Unidad": "m"},
    {"Codigo": "TOR", "Producto": "TORNIMETAL (TOR 5)", "Unidad": "un."}
]

# --- INICIALIZACIÓN ---
def inicializar_archivos():
    cols_stock = ["Codigo", "Producto", "Cantidad", "Reservado", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    
    # Si no existe el archivo, lo creamos con la lista de productos
    if not os.path.exists(STOCK_FILE):
        df_init = pd.DataFrame(PRODUCTOS_INICIALES)
        # Completar columnas faltantes con 0.0 (NUMEROS, NO TEXTO)
        for col in cols_stock:
            if col not in df_init.columns:
                df_init[col] = 0.0
        df_init.to_csv(STOCK_FILE, index=False)
    else:
        # Si existe, chequeamos estructura
        try:
            df = pd.read_csv(STOCK_FILE)
            guardar = False
            if "Reservado" not in df.columns:
                df["Reservado"] = 0.0
                guardar = True
            if "Codigo" not in df.columns:
                df.insert(0, "Codigo", "")
                guardar = True
            if guardar:
                df.to_csv(STOCK_FILE, index=False)
        except:
            pass
    
    # Otros archivos
    if not os.path.exists(PRODUCCION_FILE):
        pd.DataFrame(columns=["Fecha_Inicio", "Producto", "Cantidad", "Dias_Fraguado", "Fecha_Lista", "Estado"]).to_csv(PRODUCCION_FILE, index=False)
    if not os.path.exists(GASTOS_FILE):
        pd.DataFrame(columns=["Fecha", "Insumo", "Cantidad", "Monto"]).to_csv(GASTOS_FILE, index=False)
    if not os.path.exists(VENTAS_FILE):
        pd.DataFrame(columns=["Fecha", "Cliente", "Total", "Tipo_Entrega", "Detalle"]).to_csv(VENTAS_FILE, index=False)

# Función de Limpieza de Tipos (LA SOLUCIÓN AL ERROR)
def cargar_datos_stock():
    df = pd.read_csv(STOCK_FILE)
    
    # Forzar que Codigo y Producto sean Texto
    df["Codigo"] = df["Codigo"].fillna("").astype(str)
    df["Producto"] = df["Producto"].fillna("").astype(str)
    df["Unidad"] = df["Unidad"].fillna("un.").astype(str)
    
    # Forzar que los números sean REALMENTE números (Float)
    cols_numericas = ["Cantidad", "Reservado", "Precio Costo", "Precio Venta", "Stock Minimo"]
    for col in cols_numericas:
        # Convertir a número, si falla pone 0.0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    return df

def cargar_datos_general(archivo):
    return pd.read_csv(archivo)

# --- CLASE PDF ---
class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_FILE):
            try: self.image(LOGO_FILE, 10, 8, 30) 
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
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {date.today()} ({tipo_venta})", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Cod", 1)
    pdf.cell(90, 10, "Producto", 1)
    pdf.cell(20, 10, "Cant", 1)
    pdf.cell(25, 10, "Unit", 1)
    pdf.cell(25, 10, "Total", 1)
    pdf.ln()
    pdf.set_font("Arial", size=10)
    for item in items:
        pdf.cell(30, 10, str(item['Codigo']), 1)
        pdf.cell(90, 10, str(item['Producto']), 1)
        pdf.cell(20, 10, str(item['Cantidad']), 1)
        pdf.cell(25, 10, f"${item['Precio']:.0f}", 1)
        pdf.cell(25, 10, f"${item['Subtotal']:.0f}", 1)
        pdf.ln()
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(165, 10, "TOTAL", 0)
    pdf.cell(25, 10, f"${total:,.0f}", 0, 1)
    return pdf.output(dest='S').encode('latin-1')

inicializar_archivos()

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- INTERFAZ ---
st.title("🏗️ Alambrados del Carmen S.A.")
tab_cot, tab_stock, tab_prod, tab_hist = st.tabs(["📝 Cotizador", "📦 Stock", "🏭 Producción", "📊 Historial"])

# TAB 1: COTIZADOR
with tab_cot:
    df_s = cargar_datos_stock() # Usamos la función blindada
    
    # Calcular Disponible en el momento
    df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]

    col_izq, col_der = st.columns([1, 1])
    with col_izq:
        st.subheader("1. Pedido")
        cliente = st.text_input("Cliente")
        st.write("---")
        
        # Selectbox con info de stock
        opciones = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']} (Disp: {x['DISPONIBLE']:.0f})", axis=1)
        sel_prod = st.selectbox("Producto:", ["Seleccionar..."] + list(opciones))
        
        c_cant, c_add = st.columns([1, 2])
        cant = c_cant.number_input("Cantidad", min_value=1.0, value=1.0)
        
        if c_add.button("➕ Agregar") and sel_prod != "Seleccionar...":
            cod = sel_prod.split("]")[0].replace("[", "")
            # Buscar en dataframe limpio
            fila = df_s[df_s["Codigo"] == cod].iloc[0]
            
            if cant > fila["DISPONIBLE"]:
                st.toast(f"⚠️ Atención: Stock bajo ({fila['DISPONIBLE']})", icon="⚠️")
            
            st.session_state.carrito.append({
                "Codigo": fila["Codigo"],
                "Producto": fila["Producto"],
                "Cantidad": cant,
                "Precio": fila["Precio Venta"],
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
            
            if st.button("Vaciar"):
                st.session_state.carrito = []
                st.rerun()
            
            st.markdown("---")
            tipo = st.radio("Operación:", ["Entrega Inmediata", "Acopio / Reserva"])
            
            c_p, c_v = st.columns(2)
            pdf = generar_pdf(cliente, st.session_state.carrito, total, tipo)
            c_p.download_button("📄 PDF", pdf, f"P_{cliente}.pdf", "application/pdf")
            
            if c_v.button("✅ Confirmar", type="primary"):
                for item in st.session_state.carrito:
                    # Buscar índice exacto
                    idx = df_s.index[df_s["Codigo"] == item["Codigo"]].tolist()
                    if idx:
                        i = idx[0]
                        if "Reserva" in tipo:
                            df_s.at[i, "Reservado"] += item["Cantidad"]
                        else:
                            df_s.at[i, "Cantidad"] -= item["Cantidad"]
                
                df_s.to_csv(STOCK_FILE, index=False)
                
                # Guardar Venta
                nuevo = pd.DataFrame([{
                    "Fecha": date.today(),
                    "Cliente": cliente,
                    "Total": total,
                    "Tipo_Entrega": "Reserva" if "Reserva" in tipo else "Inmediata",
                    "Detalle": str([x["Producto"] for x in st.session_state.carrito])
                }])
                pd.concat([cargar_datos_general(VENTAS_FILE), nuevo]).to_csv(VENTAS_FILE, index=False)
                
                st.session_state.carrito = []
                st.success("¡Listo!")
                st.balloons()
                st.rerun()

# TAB 2: STOCK (CON LIMPIEZA)
with tab_stock:
    st.header("📦 Inventario")
    df_s = cargar_datos_stock() # Carga limpia
    
    # Recalcular disponible visual
    df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]
    
    # Ingreso Rápido
    with st.expander("⚡ Ingreso Rápido"):
        c1, c2, c3 = st.columns([2, 1, 1])
        opc = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']}", axis=1)
        sel = c1.selectbox("Prod:", opc)
        num = c2.number_input("Cant:", min_value=1.0)
        if c3.button("📥 Sumar"):
            cod = sel.split("]")[0].replace("[", "")
            idx = df_s.index[df_s["Codigo"] == cod].tolist()
            if idx:
                df_s.at[idx[0], "Cantidad"] += num
                df_s.to_csv(STOCK_FILE, index=False)
                st.rerun()

    # Edición
    st.subheader("Listado Maestro")
    
    # Definimos la configuración SOLO para columnas que sabemos que existen y son numéricas
    df_edit = st.data_editor(
        df_s,
        key="stock_editor_final",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
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
    st.header("🏭 Fraguado")
    df_p = cargar_datos_general(PRODUCCION_FILE)
    df_s_act = cargar_datos_stock()
    
    c1, c2, c3 = st.columns([2, 1, 1])
    p_fab = c1.selectbox("Producto:", df_s_act["Producto"].unique())
    n_fab = c2.number_input("Cantidad:", min_value=1.0)
    if c3.button("Registrar Producción"):
        hoy = date.today()
        # Asumimos 28 días siempre para hormigón
        fin = hoy + timedelta(days=28)
        nuevo = pd.DataFrame([{
            "Fecha_Inicio": hoy, "Producto": p_fab, "Cantidad": n_fab,
            "Dias_Fraguado": 28, "Fecha_Lista": fin, "Estado": "En Proceso"
        }])
        pd.concat([df_p, nuevo]).to_csv(PRODUCCION_FILE, index=False)
        st.success("En proceso de fraguado.")
        st.rerun()
        
    st.subheader("Estado")
    if not df_p.empty:
        # Lógica simple de visualización
        st.dataframe(df_p)
        if st.button("Limpiar Finalizados"):
             # Aquí iría lógica más compleja, por ahora limpieza simple
             df_p = df_p[df_p["Estado"] != "Finalizado"]
             df_p.to_csv(PRODUCCION_FILE, index=False)
             st.rerun()

# TAB 4: HISTORIAL
with tab_hist:
    st.header("Historial")
    df_v = cargar_datos_general(VENTAS_FILE)
    st.dataframe(df_v, use_container_width=True)

import streamlit as st
import pandas as pd
import os
import io
import ast 
from datetime import date, timedelta, datetime
import pytz
from fpdf import FPDF

# AUTO-CONFIGURACIÓN DE TEMA
def configurar_tema_alambrados():
    config_dir = ".streamlit"
    config_path = os.path.join(config_dir, "config.toml")
    tema_corporativo = """
[theme]
base="light"
primaryColor="#D32F2F"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#31333F"
font="sans serif"
"""
    if not os.path.exists(config_path):
        try:
            os.makedirs(config_dir, exist_ok=True)
            with open(config_path, "w") as f:
                f.write(tema_corporativo)
            return True
        except: pass
    return False

if configurar_tema_alambrados():
    st.warning("🎨 Tema instalado. Reiniciá la app para ver los cambios.")
    st.stop()

# ESTILOS CSS
st.markdown("""
    <style>
        [data-testid="stSidebar"] img { margin-top: 20px; border-radius: 5px; border: 2px solid #D32F2F; }
        h1, h2, h3 { color: #B71C1C !important; }
        [data-testid="stMetricValue"] { color: #D32F2F; }
        /* Botones de borrar pequeños */
        div[data-testid="column"] button {
            padding: 0px 10px;
            font-size: 12px;
            line-height: 1.5;
        }
    </style>
""", unsafe_allow_html=True)

# RUTAS Y ARCHIVOS
STOCK_FILE = "stock_del_carmen.csv"
GASTOS_FILE = "gastos_del_carmen.csv"
VENTAS_FILE = "ventas_del_carmen.csv"
PRODUCCION_FILE = "produccion_del_carmen.csv"
LOGO_FILE = "alambrados.jpeg"

# LISTA COMPLETA DE PRODUCTOS
PRODUCTOS_INICIALES = [
    {"Codigo": "3", "Producto": "ADICIONAL PINCHES 20.000", "Unidad": "un."},
    {"Codigo": "6", "Producto": "BOYERITO IMPORTADO X 1000", "Unidad": "un."},
    {"Codigo": "3", "Producto": "CONCERTINA DOBLE CRUZADA X 45", "Unidad": "un."},
    {"Codigo": "2", "Producto": "CONCERTINA SIMPLE", "Unidad": "un."},
    {"Codigo": "1", "Producto": "DECO 1.50", "Unidad": "un."},
    {"Codigo": "0", "Producto": "DECO 1.80", "Unidad": "un."},
    {"Codigo": "3", "Producto": "ESPARRAGOS", "Unidad": "un."},
    {"Codigo": "25", "Producto": "ESQUINERO OLIMPICO", "Unidad": "un."},
    {"Codigo": "2", "Producto": "ESQUINERO RECTO", "Unidad": "un."},
    {"Codigo": "15", "Producto": "GALVA 14 X KILO", "Unidad": "kg"},
    {"Codigo": "5", "Producto": "GALVA 18", "Unidad": "kg"},
    {"Codigo": "31", "Producto": "GANCHOS ESTIRATEJIDOS 5/16", "Unidad": "un."},
    {"Codigo": "15", "Producto": "OVALADO X MAYOR X 1000", "Unidad": "un."},
    {"Codigo": "32", "Producto": "PALOMITAS", "Unidad": "un."},
    {"Codigo": "24", "Producto": "PINCHES X METRO PINCHOSOS", "Unidad": "m"},
    {"Codigo": "41", "Producto": "PLANCHUELA 1.00", "Unidad": "un."},
    {"Codigo": "40", "Producto": "PLANCHUELA 1.20", "Unidad": "un."},
    {"Codigo": "35", "Producto": "PLANCHUELA 1.50", "Unidad": "un."},
    {"Codigo": "34", "Producto": "PLANCHUELA 2.00", "Unidad": "un."},
    {"Codigo": "47", "Producto": "PORTON 3.00 X 1.80 BLACK", "Unidad": "un."},
    {"Codigo": "9", "Producto": "PORTON DE CANO X 4.00", "Unidad": "un."},
    {"Codigo": "10", "Producto": "PORTON INDUSTRIAL X 4.00", "Unidad": "un."},
    {"Codigo": "51", "Producto": "PORTON LIVIANO 1.80 X 3.00 CANO", "Unidad": "un."},
    {"Codigo": "53", "Producto": "PORTON LIVIANO 1.80X 3.00", "Unidad": "un."},
    {"Codigo": "11", "Producto": "PORTON SIMPLE X 3.00", "Unidad": "un."},
    {"Codigo": "54", "Producto": "POSTE DE MADERA", "Unidad": "un."},
    {"Codigo": "27", "Producto": "POSTE OLIMPICO", "Unidad": "un."},
    {"Codigo": "28", "Producto": "POSTE RECTO", "Unidad": "un."},
    {"Codigo": "57", "Producto": "POSTE REDONDE ECO OBRA", "Unidad": "un."},
    {"Codigo": "14", "Producto": "PUA X MAYOR X500", "Unidad": "un."},
    {"Codigo": "43", "Producto": "PUA X METRO", "Unidad": "m"},
    {"Codigo": "16", "Producto": "PUERTITA CLASICA 1.50", "Unidad": "un."},
    {"Codigo": "12", "Producto": "PUERTITA CORAZON 1.5 X 1.00", "Unidad": "un."},
    {"Codigo": "13", "Producto": "PUERTITA CRUZ REFORZADA 2.00 X 1.00", "Unidad": "un."},
    {"Codigo": "7", "Producto": "PUERTITA LIVINA 1.00 X 1.80", "Unidad": "un."},
    {"Codigo": "P", "Producto": "PUNTAL", "Unidad": "un."},
    {"Codigo": "R16", "Producto": "RECOCIDO 16", "Unidad": "kg"},
    {"Codigo": "REF", "Producto": "REFUERZO", "Unidad": "un."},
    {"Codigo": "55", "Producto": "TEJIDO 1.50", "Unidad": "m"},
    {"Codigo": "19", "Producto": "TEJIDO 2.00 X METRO", "Unidad": "m"},
    {"Codigo": "59", "Producto": "TEJIDO DE OBRA 1.50", "Unidad": "m"},
    {"Codigo": "63", "Producto": "TEJIDO DE OBRA 1.80", "Unidad": "m"},
    {"Codigo": "50", "Producto": "TEJIDO DEL 12 - 2 PULGADAS", "Unidad": "m"},
    {"Codigo": "18", "Producto": "TEJIDO RECU 1.8", "Unidad": "m"},
    {"Codigo": "TR", "Producto": "TEJIDO ROMBITO 2 PULGADAS", "Unidad": "m"}
]

# FUNCIONES
def ahora_arg():
    try: return datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))
    except: return datetime.now()

def generar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Stock')
    return output.getvalue()

def cargar_datos_stock():
    crear_nuevo = False
    if not os.path.exists(STOCK_FILE):
        crear_nuevo = True
    else:
        try:
            df_check = pd.read_csv(STOCK_FILE)
            if df_check.empty or len(df_check) < 2:
                crear_nuevo = True
        except: crear_nuevo = True

    if crear_nuevo:
        df_init = pd.DataFrame(PRODUCTOS_INICIALES)
        for col in ["Cantidad", "Reservado", "Precio Costo", "Precio Venta", "Stock Minimo"]:
            if col not in df_init.columns: df_init[col] = 0.0
        df_init.to_csv(STOCK_FILE, index=False)
    
    df = pd.read_csv(STOCK_FILE)
    df["Codigo"] = df["Codigo"].fillna("").astype(str)
    df["Producto"] = df["Producto"].fillna("").astype(str)
    df["Unidad"] = df["Unidad"].fillna("un.").astype(str)
    for col in ["Cantidad", "Reservado", "Precio Costo", "Precio Venta", "Stock Minimo"]:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df

def cargar_datos_general(archivo, cols):
    if not os.path.exists(archivo): return pd.DataFrame(columns=cols)
    return pd.read_csv(archivo)

# PDF
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

def generar_pdf(cliente, items, total, tipo_venta=""):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Si viene con hora, usarla, sino usar ahora
    fecha_impresion = ahora_arg().strftime("%d/%m/%Y %H:%M")
    
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha Impresion: {fecha_impresion}", ln=True)
    if tipo_venta: 
        pass 
        
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
        # Asegurar que los datos existan para evitar error en historial viejo
        cod = str(item.get('Codigo', ''))
        prod = str(item.get('Producto', ''))
        cant = item.get('Cantidad', 0)
        prec = item.get('Precio', 0)
        sub = item.get('Subtotal', 0)
        
        pdf.cell(20, 10, cod, 1)
        pdf.cell(90, 10, prod, 1)
        pdf.cell(20, 10, f"{cant:.1f}", 1)
        pdf.cell(30, 10, f"${prec:.0f}", 1)
        pdf.cell(30, 10, f"${sub:.0f}", 1)
        pdf.ln()
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(160, 10, "TOTAL FINAL", 0)
    pdf.set_text_color(183, 28, 28)
    pdf.cell(30, 10, f"${total:,.0f}", 0, 1)
    
    # DISCLAIMER LEGAL
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(80, 80, 80)
    texto_legal = "Presupuesto sujeto a disponibilidad de stock al momento de la compra. Los precios pueden sufrir modificaciones sin previo aviso hasta la confirmación del pago."
    pdf.multi_cell(0, 5, texto_legal)
    
    return pdf.output(dest='S').encode('latin-1')

if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'input_key' not in st.session_state: st.session_state.input_key = 0

# BARRA LATERAL
with st.sidebar:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, use_container_width=True)
    else: st.title("AC")
    st.write("---")
    st.caption(f"📅 {ahora_arg().strftime('%d/%m/%Y %H:%M')}")
    st.write("---")
    with st.expander("⚙️ Admin"):
        if st.button("♻️ Reiniciar Base de Datos"):
             if os.path.exists(STOCK_FILE): os.remove(STOCK_FILE)
             st.success("Reiniciando...")
             st.rerun()

# INTERFAZ
st.title("Gestión Comercial")
tab_cot, tab_stock, tab_prod, tab_hist = st.tabs(["📝 Cotizador", "💰 Stock y Costos", "🏭 Producción", "📊 Historial"])

# 1. COTIZADOR
with tab_cot:
    df_s = cargar_datos_stock()
    if df_s.empty: st.error("⚠️ Base vacía.")
    else:
        if "Reservado" not in df_s.columns: df_s["Reservado"] = 0.0
        df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]

        col_izq, col_der = st.columns([1, 1])
        with col_izq:
            st.subheader("1. Carga de Productos")
            cliente = st.text_input("Nombre del Cliente")
            st.write("---")
            
            modo_carga = st.radio("Método de Carga:", ["⚡ Carga Rápida (Por Código)", "🔍 Buscador (Por Nombre)"], horizontal=True)
            
            if modo_carga == "⚡ Carga Rápida (Por Código)":
                st.info("Ingresá los códigos. Tabla de 12 filas fija.")
                # Tabla fija de 12 filas vacías
                df_input_template = pd.DataFrame([{"Codigo": "", "Cantidad": 1.0}] * 12)
                
                edited_input = st.data_editor(
                    df_input_template, 
                    num_rows="dynamic", 
                    key=f"grid_input_{st.session_state.input_key}", 
                    column_config={
                        "Codigo": st.column_config.TextColumn("Código"),
                        "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=0.1, step=1.0)
                    },
                    hide_index=True
                )
                
                if st.button("🔄 Procesar Lista", type="primary"):
                    items_agregados = 0
                    items_no_encontrados = []
                    for index, row in edited_input.iterrows():
                        cod_ingresado = str(row["Codigo"]).strip()
                        cant_ingresada = float(row["Cantidad"])
                        if cod_ingresado:
                            filtro = df_s[df_s["Codigo"] == cod_ingresado]
                            if not filtro.empty:
                                fila = filtro.iloc[0]
                                st.session_state.carrito.append({
                                    "Codigo": fila["Codigo"], "Producto": fila["Producto"],
                                    "Cantidad": cant_ingresada, "Precio": fila["Precio Venta"],
                                    "Subtotal": cant_ingresada * fila["Precio Venta"]
                                })
                                items_agregados += 1
                            else: items_no_encontrados.append(cod_ingresado)
                    
                    if items_agregados > 0:
                        st.success(f"Agregados: {items_agregados}")
                        st.session_state.input_key += 1 
                        st.rerun()
                    if items_no_encontrados: st.error(f"No encontrado: {', '.join(items_no_encontrados)}")

            else:
                opciones = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']} (Disp: {x['DISPONIBLE']:.0f})", axis=1)
                sel_prod = st.selectbox("Buscar:", ["Seleccionar..."] + list(opciones))
                c_cant, c_add = st.columns([1, 2])
                cant = c_cant.number_input("Cantidad", min_value=1.0)
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
            st.subheader("2. Detalle del Pedido")
            if st.session_state.carrito:
                st.markdown("---")
                k1, k2, k3, k4 = st.columns([4, 2, 2, 1])
                k1.markdown("**Producto**")
                k2.markdown("**Cant.**")
                k3.markdown("**Total**")
                for i, item in enumerate(st.session_state.carrito):
                    c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
                    c1.write(item["Producto"])
                    c2.write(f"{item['Cantidad']:.1f}")
                    c3.write(f"${item['Subtotal']:,.0f}")
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
                st.caption("Opciones:")
                tipo = st.radio("Destino:", ["Entrega Inmediata", "Dejar en Acopio"], horizontal=True, label_visibility="collapsed")
                
                c_pdf, c_ok = st.columns(2)
                pdf_bytes = generar_pdf(cliente, st.session_state.carrito, total)
                c_pdf.download_button("📄 Presupuesto", pdf_bytes, f"P_{cliente}.pdf", "application/pdf", use_container_width=True)
                
                if c_ok.button("✅ CONFIRMAR VENTA", type="primary", use_container_width=True):
                    for item in st.session_state.carrito:
                        idx = df_s.index[df_s["Codigo"] == item["Codigo"]].tolist()
                        if idx:
                            i = idx[0]
                            if "Acopio" in tipo: df_s.at[i, "Reservado"] += item["Cantidad"]
                            else: df_s.at[i, "Cantidad"] -= item["Cantidad"]
                    df_s.to_csv(STOCK_FILE, index=False)
                    
                    # GUARDADO INTELIGENTE (JSON) PARA REIMPRIMIR
                    # Guardamos la lista de objetos completa como string
                    detalle_completo = str(st.session_state.carrito)
                    
                    nuevo = pd.DataFrame([{
                        "Fecha": ahora_arg().strftime("%d/%m/%Y %H:%M"), 
                        "Cliente": cliente, "Total": total, "Tipo": tipo,
                        "Detalle": detalle_completo # Guardamos TODO el detalle
                    }])
                    hist = cargar_datos_general(VENTAS_FILE, ["Fecha","Cliente","Total","Tipo","Detalle"])
                    pd.concat([hist, nuevo]).to_csv(VENTAS_FILE, index=False)
                    st.session_state.carrito = []
                    st.success("¡Venta Exitosa!")
                    st.balloons()
                    st.rerun()
            else: st.info("Carrito vacío.")

# 2. STOCK
with tab_stock:
    df_s = cargar_datos_stock()
    if not df_s.empty:
        df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]
        df_s["Ganancia Unitaria"] = df_s["Precio Venta"] - df_s["Precio Costo"]

    st.subheader("Tablero Financiero y Stock")
    with st.expander("🛒 Registrar COMPRA o INGRESO", expanded=False):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        opc = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']}", axis=1)
        sel = c1.selectbox("Producto:", opc)
        num = c2.number_input("Cant:", min_value=1.0)
        nuevo_costo = c3.number_input("Nuevo Costo?", min_value=0.0)
        if c4.button("📥 Ingresar"):
            cod = sel.split("]")[0].replace("[", "")
            idx = df_s.index[df_s["Codigo"] == cod].tolist()
            if idx:
                i = idx[0]
                df_s.at[i, "Cantidad"] += num
                if nuevo_costo > 0: df_s.at[i, "Precio Costo"] = nuevo_costo
                df_s.to_csv(STOCK_FILE, index=False)
                st.success("¡Actualizado!")
                st.rerun()
    
    with st.expander("✨ Crear Nuevo Producto"):
        c_new1, c_new2, c_new3 = st.columns(3)
        n_cod = c_new1.text_input("Código")
        n_nom = c_new2.text_input("Nombre")
        n_uni = c_new3.selectbox("Unidad", ["un.", "m", "kg", "pack"])
        c_cost, c_price = st.columns(2)
        n_costo = c_cost.number_input("Costo", min_value=0.0)
        n_venta = c_price.number_input("Venta", min_value=0.0)
        if st.button("Crear"):
            if n_cod and n_nom:
                nuevo = pd.DataFrame([{
                    "Codigo": n_cod, "Producto": n_nom, "Unidad": n_uni,
                    "Cantidad": 0.0, "Reservado": 0.0, 
                    "Precio Costo": n_costo, "Precio Venta": n_venta, "Stock Minimo": 0.0
                }])
                df_s = pd.concat([df_s, nuevo], ignore_index=True)
                df_s.to_csv(STOCK_FILE, index=False)
                st.rerun()

    st.write("---")
    c_dl, c_save = st.columns([1, 4])
    c_dl.download_button("📥 Excel", generar_excel(df_s), f"Stock_{date.today()}.xlsx")
    
    df_edit = st.data_editor(
        df_s, key="editor_stock", num_rows="dynamic", use_container_width=True, hide_index=True,
        column_order=["Codigo", "Producto", "DISPONIBLE", "Cantidad", "Reservado", "Precio Costo", "Precio Venta", "Ganancia Unitaria"],
        column_config={
            "Codigo": st.column_config.TextColumn("Cód"),
            "DISPONIBLE": st.column_config.NumberColumn("✅ Disp.", disabled=True, format="%.0f"),
            "Cantidad": st.column_config.NumberColumn("Físico", format="%.0f"),
            "Reservado": st.column_config.NumberColumn("Reservado", format="%.0f"),
            "Precio Costo": st.column_config.NumberColumn("Costo ($)", format="$ %d"),
            "Precio Venta": st.column_config.NumberColumn("Venta ($)", format="$ %d"),
            "Ganancia Unitaria": st.column_config.NumberColumn("Ganancia ($)", disabled=True, format="$ %d"),
        }
    )
    if c_save.button("💾 GUARDAR CAMBIOS MASIVOS", type="primary"):
        cols_to_save = ["Codigo", "Producto", "Cantidad", "Reservado", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
        df_final = df_edit[cols_to_save] 
        df_final.to_csv(STOCK_FILE, index=False)
        st.success("Guardado.")
        st.rerun()

# 3. PRODUCCION
with tab_prod:
    st.subheader("🏭 Producción")
    df_prod = cargar_datos_general(PRODUCCION_FILE, ["Fecha_Inicio","Producto","Cantidad","Fecha_Lista","Estado"])
    df_stk = cargar_datos_stock()
    
    with st.form("new_prod"):
        c1, c2 = st.columns(2)
        prod = c1.selectbox("Producto:", df_stk["Producto"].unique() if not df_stk.empty else [])
        cant = c2.number_input("Cant:", 1)
        c3, c4 = st.columns(2)
        fecha = c3.date_input("Fecha:", value=ahora_arg().date())
        dias = c4.number_input("Días (0=Listo):", value=28)
        if st.form_submit_button("Registrar"):
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
                    c_txt.success(f"✅ **LISTO:** {row['Cantidad']}x {row['Producto']}")
                    if c_btn.button("📥 A STOCK", key=f"p_{index}"):
                        df_s = cargar_datos_stock()
                        idx = df_s.index[df_s["Producto"] == row['Producto']].tolist()
                        if idx:
                            df_s.at[idx[0], "Cantidad"] += row['Cantidad']
                            df_s.to_csv(STOCK_FILE, index=False)
                            df_prod.at[index, "Estado"] = "Finalizado"
                            df_prod.to_csv(PRODUCCION_FILE, index=False)
                            st.rerun()
                else: c_txt.info(f"⏳ Faltan {falta} días para {row['Producto']}")

# 4. HISTORIAL 
with tab_hist:
    st.subheader("Registro de Ventas y Reimpresión")
    df_v = cargar_datos_general(VENTAS_FILE, ["Fecha","Cliente","Total","Tipo","Detalle"])
    
    if not df_v.empty:
        # Ordenar por fecha reciente
        df_v = df_v.sort_index(ascending=False)
        
        # SECTOR DE REIMPRESIÓN 
        st.write("🖨️ **Reimprimir Comprobante**")
        # Crea una lista amigable para seleccionar
        opciones_venta = df_v.apply(lambda x: f"{x['Fecha']} | {x['Cliente']} | Total: ${x['Total']:,.0f}", axis=1)
        venta_seleccionada = st.selectbox("Seleccionar Venta:", opciones_venta)
        
        if venta_seleccionada:
            # Encontrar la fila original
            idx_sel = opciones_venta[opciones_venta == venta_seleccionada].index[0]
            fila_venta = df_v.loc[idx_sel]
            
            # Reconstruir datos para el PDF
            try:
                # MAGIA: Convierte el texto guardado 
                items_recuperados = ast.literal_eval(fila_venta["Detalle"])
                
                # Generar PDF
                pdf_reimpresion = generar_pdf(fila_venta["Cliente"], items_recuperados, fila_venta["Total"])
                
                st.download_button(
                    label="📄 Descargar PDF de esta venta",
                    data=pdf_reimpresion,
                    file_name=f"Reimpresion_{fila_venta['Cliente']}.pdf",
                    mime="application/pdf"
                )
            except:
                st.error("No se pudo reconstruir el detalle de esta venta (Formato antiguo).")

        st.divider()
        st.write("📊 **Tabla de Datos**")
        st.dataframe(df_v, use_container_width=True)
    else:
        st.info("No hay ventas registradas aún.")

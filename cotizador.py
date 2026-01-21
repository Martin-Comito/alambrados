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
PRODUCCION_FILE = "produccion_del_carmen.csv" # Nuevo para fraguado
LOGO_FILE = "alambradoslogo.jpeg"

# --- LISTA DE PRODUCTOS INICIAL (Desde la Foto) ---
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
    # Estructura Stock: Agregamos 'Reservado'
    cols_stock = ["Codigo", "Producto", "Cantidad", "Reservado", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    
    if not os.path.exists(STOCK_FILE):
        # Crear con datos de la foto
        df_init = pd.DataFrame(PRODUCTOS_INICIALES)
        # Completar columnas faltantes con 0
        for col in cols_stock:
            if col not in df_init.columns:
                df_init[col] = 0.0
        df_init.to_csv(STOCK_FILE, index=False)
    else:
        # Actualización de estructura para archivos viejos
        try:
            df = pd.read_csv(STOCK_FILE)
            guardar = False
            # Agregar columna Reservado si no existe
            if "Reservado" not in df.columns:
                df["Reservado"] = 0.0
                guardar = True
            if "Codigo" not in df.columns:
                df.insert(0, "Codigo", "")
                guardar = True
            
            if guardar:
                df.to_csv(STOCK_FILE, index=False)
        except:
            pass # Si falla, no rompemos nada
    
    # Archivo de Producción (Fraguado)
    if not os.path.exists(PRODUCCION_FILE):
        pd.DataFrame(columns=["Fecha_Inicio", "Producto", "Cantidad", "Dias_Fraguado", "Fecha_Lista", "Estado"]).to_csv(PRODUCCION_FILE, index=False)

    if not os.path.exists(GASTOS_FILE):
        pd.DataFrame(columns=["Fecha", "Insumo", "Cantidad", "Monto"]).to_csv(GASTOS_FILE, index=False)
    if not os.path.exists(VENTAS_FILE):
        pd.DataFrame(columns=["Fecha", "Cliente", "Total", "Tipo_Entrega", "Detalle"]).to_csv(VENTAS_FILE, index=False)

def cargar_datos(archivo):
    return pd.read_csv(archivo)

# --- CLASE PDF MEJORADA ---
class PDF(FPDF):
    def header(self):
        # Logo normal arriba a la izquierda
        if os.path.exists(LOGO_FILE):
            try:
                self.image(LOGO_FILE, 10, 8, 30) 
            except: pass
            
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'PRESUPUESTO', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Alambrados del Carmen S.A. - Haciendo clientes felices', 0, 0, 'C')

    def water_mark(self):
        # Marca de agua en el centro
        if os.path.exists(LOGO_FILE):
            try:
                self.set_alpha(0.15) # 15% de opacidad
                # Centrado en página A4 (210mm ancho) -> x aprox 50, w=100
                self.image(LOGO_FILE, x=55, y=80, w=100)
                self.set_alpha(1) # Restaurar
            except: pass

def generar_pdf(cliente, items, total, tipo_venta):
    pdf = PDF()
    pdf.add_page()
    pdf.water_mark()
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {date.today()}", ln=True)
    pdf.cell(200, 10, txt=f"Condición: {tipo_venta}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Código", 1)
    pdf.cell(90, 10, "Descripción", 1)
    pdf.cell(20, 10, "Cant.", 1)
    pdf.cell(25, 10, "Unitario", 1)
    pdf.cell(25, 10, "Subtotal", 1)
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
    pdf.cell(165, 10, "TOTAL FINAL", 0)
    pdf.cell(25, 10, f"${total:,.0f}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1')

inicializar_archivos()

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- INTERFAZ ---
st.title("🏗️ Alambrados del Carmen S.A.")

tab_cot, tab_stock, tab_prod, tab_hist = st.tabs(["📝 Cotizador & Ventas", "📦 Stock & Precios", "🏭 Producción (Fraguado)", "📊 Historial"])

# ==============================================================================
# TAB 1: COTIZADOR CON RESERVAS
# ==============================================================================
with tab_cot:
    df_s = cargar_datos(STOCK_FILE)
    
    # Limpieza de tipos
    df_s["Codigo"] = df_s["Codigo"].fillna("").astype(str)
    df_s["Cantidad"] = pd.to_numeric(df_s["Cantidad"], errors='coerce').fillna(0.0)
    df_s["Reservado"] = pd.to_numeric(df_s["Reservado"], errors='coerce').fillna(0.0)
    
    # Calculamos DISPONIBLE REAL
    df_s["Disponible"] = df_s["Cantidad"] - df_s["Reservado"]

    col_izq, col_der = st.columns([1, 1])
    
    with col_izq:
        st.subheader("1. Armar Pedido")
        cliente = st.text_input("Nombre del Cliente")
        
        st.write("---")
        # Mostrar Disp (Disponible) en el select
        opciones_prod = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']} | Disp: {x['Disponible']:.0f} {x['Unidad']}", axis=1)
        seleccion_str = st.selectbox("Buscar Producto:", options=["Seleccionar..."] + list(opciones_prod))
        
        c_cant, c_boton = st.columns([1, 2])
        cantidad = c_cant.number_input("Cantidad", min_value=1.0, value=1.0)
        
        if c_boton.button("➕ Agregar al Carrito") and seleccion_str != "Seleccionar...":
            cod_prod = seleccion_str.split("]")[0].replace("[", "")
            fila = df_s[df_s["Codigo"] == cod_prod].iloc[0]
            
            # Chequeo de stock básico (aviso)
            if cantidad > fila["Disponible"]:
                st.warning(f"⚠️ Ojo: Solo tenés {fila['Disponible']} disponibles. Estás vendiendo más de lo que hay libre.")
            
            item = {
                "Codigo": fila["Codigo"],
                "Producto": fila["Producto"],
                "Cantidad": cantidad,
                "Precio": float(fila["Precio Venta"]),
                "Subtotal": cantidad * float(fila["Precio Venta"])
            }
            st.session_state.carrito.append(item)
            st.rerun()

    with col_der:
        st.subheader("2. Detalle del Pedido")
        if len(st.session_state.carrito) > 0:
            df_carrito = pd.DataFrame(st.session_state.carrito)
            st.dataframe(df_carrito[["Producto", "Cantidad", "Subtotal"]], hide_index=True, use_container_width=True)
            
            total_presupuesto = df_carrito["Subtotal"].sum()
            st.metric("TOTAL", f"$ {total_presupuesto:,.0f}")
            
            if st.button("🗑️ Vaciar Carrito"):
                st.session_state.carrito = []
                st.rerun()
                
            st.markdown("### 3. Finalizar")
            tipo_venta = st.radio("Tipo de Operación:", ["Entrega Inmediata (Baja Stock)", "Acopio / Reserva (Guarda Stock)"])
            
            c_pdf, c_accion = st.columns(2)
            
            # PDF
            pdf_bytes = generar_pdf(cliente if cliente else "Consumidor", st.session_state.carrito, total_presupuesto, tipo_venta)
            c_pdf.download_button("📄 Imprimir Presupuesto", pdf_bytes, f"P_{cliente}.pdf", "application/pdf")
            
            # ACCIÓN DE VENTA
            if c_accion.button("✅ Confirmar Operación", type="primary"):
                for item in st.session_state.carrito:
                    idx = df_s.index[df_s["Codigo"] == item["Codigo"]].tolist()
                    if idx:
                        i = idx[0]
                        if "Reserva" in tipo_venta:
                            # Sumamos a Reservado, NO restamos de Cantidad Total todavía
                            df_s.at[i, "Reservado"] += item["Cantidad"]
                        else:
                            # Entrega Inmediata: Se va del galpón
                            df_s.at[i, "Cantidad"] -= item["Cantidad"]
                
                df_s.to_csv(STOCK_FILE, index=False)
                
                # Guardar en Historial
                nuevo = pd.DataFrame([{
                    "Fecha": date.today(),
                    "Cliente": cliente,
                    "Total": total_presupuesto,
                    "Tipo_Entrega": "Reserva" if "Reserva" in tipo_venta else "Inmediata",
                    "Detalle": str([f"{x['Cantidad']}x {x['Producto']}" for x in st.session_state.carrito])
                }])
                pd.concat([cargar_datos(VENTAS_FILE), nuevo]).to_csv(VENTAS_FILE, index=False)
                
                st.session_state.carrito = []
                st.success(f"Operación Exitosa: {tipo_venta}")
                st.balloons()
                st.rerun()

# ==============================================================================
# TAB 2: STOCK (CON LOS PRODUCTOS NUEVOS)
# ==============================================================================
with tab_stock:
    st.header("📦 Inventario")
    df_s = cargar_datos(STOCK_FILE)
    
    # Limpieza
    cols_num = ["Cantidad", "Reservado", "Precio Costo", "Precio Venta", "Stock Minimo"]
    for col in cols_num:
        df_s[col] = pd.to_numeric(df_s[col], errors='coerce').fillna(0.0)
    
    # Calcular Disponible Visualmente
    df_s["DISPONIBLE"] = df_s["Cantidad"] - df_s["Reservado"]
    
    st.info("💡 'Cantidad' es lo que hay en el galpón. 'Reservado' es lo vendido pero no entregado. 'DISPONIBLE' es lo que podés vender hoy.")

    # Ingreso Rápido
    with st.expander("⚡ Ingreso de Mercadería"):
        c1, c2, c3 = st.columns([2, 1, 1])
        opc = df_s.apply(lambda x: f"[{x['Codigo']}] {x['Producto']}", axis=1)
        p_ing = c1.selectbox("Producto:", options=opc)
        c_ing = c2.number_input("Cantidad que llegó:", min_value=1.0)
        if c3.button("📥 Sumar Stock"):
            cod = p_ing.split("]")[0].replace("[", "")
            idx = df_s.index[df_s["Codigo"] == cod].tolist()
            if idx:
                df_s.at[idx[0], "Cantidad"] += c_ing
                df_s.to_csv(STOCK_FILE, index=False)
                st.success("Stock actualizado.")
                st.rerun()

    # Edición
    st.subheader("Listado Maestro")
    columnas_ordenadas = ["Codigo", "Producto", "DISPONIBLE", "Cantidad", "Reservado", "Unidad", "Precio Costo", "Precio Venta"]
    
    df_edit = st.data_editor(
        df_s,
        column_order=columnas_ordenadas,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_stock_v4",
        column_config={
            "Codigo": st.column_config.TextColumn("Cód"),
            "DISPONIBLE": st.column_config.NumberColumn("✅ VENDIBLE", format="%.0f", disabled=True), # Calculado, no editar
            "Cantidad": st.column_config.NumberColumn("Físico Total", format="%.0f"),
            "Reservado": st.column_config.NumberColumn("✋ Acopio", format="%.0f"),
            "Precio Venta": st.column_config.NumberColumn("Precio", format="$ %d"),
        }
    )
    
    if st.button("💾 Guardar Cambios Inventario"):
        df_edit.to_csv(STOCK_FILE, index=False)
        st.success("Guardado.")
        st.rerun()

# ==============================================================================
# TAB 3: PRODUCCIÓN (FRAGUADO DE POSTES)
# ==============================================================================
with tab_prod:
    st.header("🏭 Producción y Fraguado (28 Días)")
    st.markdown("Acá registrás lo que fabricás. Si requiere curado (como los postes), el sistema te avisa cuándo están listos.")
    
    df_p = cargar_datos(PRODUCCION_FILE)
    df_s_act = cargar_datos(STOCK_FILE)
    
    c_fab1, c_fab2, c_fab3, c_fab4 = st.columns([2, 1, 1, 1])
    
    lista_prod_fab = df_s_act["Producto"].tolist()
    prod_fab = c_fab1.selectbox("¿Qué fabricaste?", options=lista_prod_fab)
    cant_fab = c_fab2.number_input("Cantidad", min_value=1, key="cant_fab")
    es_cemento = c_fab3.checkbox("Requiere Fraguado?", value=True)
    
    if c_fab4.button("🚀 Registrar"):
        fecha_hoy = date.today()
        dias = 28 if es_cemento else 0
        fecha_fin = fecha_hoy + timedelta(days=dias)
        
        nuevo_p = pd.DataFrame([{
            "Fecha_Inicio": fecha_hoy,
            "Producto": prod_fab,
            "Cantidad": cant_fab,
            "Dias_Fraguado": dias,
            "Fecha_Lista": fecha_fin,
            "Estado": "En Proceso" if dias > 0 else "Listo"
        }])
        
        # Si no requiere fraguado, va directo a stock
        if dias == 0:
            idx = df_s_act.index[df_s_act["Producto"] == prod_fab].tolist()
            if idx:
                df_s_act.at[idx[0], "Cantidad"] += cant_fab
                df_s_act.to_csv(STOCK_FILE, index=False)
                st.success(f"Agregados {cant_fab} {prod_fab} al stock inmediatamente.")
        else:
            # Si requiere, va a la lista de espera
            df_p = pd.concat([df_p, nuevo_p], ignore_index=True)
            df_p.to_csv(PRODUCCION_FILE, index=False)
            st.info(f"Registrado. Estará listo el {fecha_fin}.")
            st.rerun()

    st.markdown("---")
    st.subheader("📅 Calendario de Fraguado")
    
    if not df_p.empty:
        # Convertir fecha
        df_p["Fecha_Lista"] = pd.to_datetime(df_p["Fecha_Lista"]).dt.date
        
        # Mostrar tabla
        for index, row in df_p.iterrows():
            if row["Estado"] == "En Proceso":
                hoy = date.today()
                falta = (row["Fecha_Lista"] - hoy).days
                
                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    if falta <= 0:
                        st.success(f"✅ **LISTO:** {row['Cantidad']}x {row['Producto']} (Terminó el {row['Fecha_Lista']})")
                    else:
                        st.warning(f"⏳ **FRAGUANDO:** {row['Cantidad']}x {row['Producto']} | Faltan {falta} días (Hasta {row['Fecha_Lista']})")
                
                with col_btn:
                    if falta <= 0:
                        if st.button(f"📥 Pasar a Stock", key=f"lib_{index}"):
                            # Mover a stock principal
                            df_stk = cargar_datos(STOCK_FILE)
                            idx = df_stk.index[df_stk["Producto"] == row['Producto']].tolist()
                            if idx:
                                df_stk.at[idx[0], "Cantidad"] += row['Cantidad']
                                df_stk.to_csv(STOCK_FILE, index=False)
                                
                                # Borrar de producción o marcar finalizado
                                df_p.at[index, "Estado"] = "Finalizado"
                                df_p.to_csv(PRODUCCION_FILE, index=False)
                                st.rerun()
    else:
        st.info("No hay producción pendiente.")

# TAB 4: HISTORIAL
with tab_hist:
    st.header("Historial de Operaciones")
    df_v = cargar_datos(VENTAS_FILE)
    st.dataframe(df_v.sort_values(by="Fecha", ascending=False), use_container_width=True)

import streamlit as st
import pandas as pd
import math
import os
import io
import urllib.parse
from datetime import date

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Gestión Del Carmen - Sistema Integral", layout="wide")
# Ocultar menú de hamburguesa y pie de página de Streamlit
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Rutas de archivos
STOCK_FILE = "stock_del_carmen.csv"
GASTOS_FILE = "gastos_del_carmen.csv"
RECETAS_FILE = "recetas_del_carmen.csv"
VENTAS_FILE = "ventas_del_carmen.csv"
ENTREGAS_FILE = "entregas_del_carmen.csv"

# INICIALIZACIÓN
def inicializar_archivos():
    cols_stock = ["Producto", "Cantidad", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    
    # 1. Stock
    if not os.path.exists(STOCK_FILE):
        pd.DataFrame(columns=cols_stock).to_csv(STOCK_FILE, index=False)
    else:
        df_temp = pd.read_csv(STOCK_FILE)
        guardar = False
        for col in cols_stock:
            if col not in df_temp.columns:
                df_temp[col] = 0.0
                guardar = True
        if guardar:
            df_temp.to_csv(STOCK_FILE, index=False)

    # 2. Otros archivos
    if not os.path.exists(GASTOS_FILE):
        pd.DataFrame(columns=["Fecha", "Insumo", "Cantidad", "Monto"]).to_csv(GASTOS_FILE, index=False)
    if not os.path.exists(VENTAS_FILE):
        pd.DataFrame(columns=["Fecha", "Cliente", "Monto Total", "Ganancia"]).to_csv(VENTAS_FILE, index=False)
    if not os.path.exists(RECETAS_FILE):
        pd.DataFrame(columns=["Producto Final", "Insumo", "Cantidad"]).to_csv(RECETAS_FILE, index=False)
    if not os.path.exists(ENTREGAS_FILE):
        pd.DataFrame(columns=["Fecha", "Cliente", "Direccion", "Carga", "Estado"]).to_csv(ENTREGAS_FILE, index=False)

def cargar_datos(archivo):
    df = pd.read_csv(archivo)
    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
    return df

def descargar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

inicializar_archivos()

# INTERFAZ
st.title("🏗️ Alambrados del Carmen S.A.")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Cotizador", "📦 Inventario", "📊 Análisis", "💰 Gastos", "⚒️ Fábrica", "🚚 Logística"])

# TAB 1: COTIZADOR
with tab1:
    st.header("Presupuesto y Venta")
    df_s = cargar_datos(STOCK_FILE)
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", "Consumidor Final")
        direccion = c1.text_input("Dirección de Entrega (Para el mapa)", "Retira por local")
        
        altura = c1.number_input("Altura (m)", min_value=0.1, value=1.5, step=0.1)
        hilos = c1.number_input("Hilos Alambre", min_value=1, value=3 if altura <= 1.5 else 4)
        
        tipo = c2.radio("Obra:", ["Lineal", "Perímetro"], horizontal=True)
        largo = c2.number_input("Largo (m)", min_value=1.0, value=20.0)
        ancho = c2.number_input("Fondo (m)", min_value=0.0) if tipo == "Perímetro" else 0.0
        
        manual = st.toggle("🔓 Editar Manual")

    # Cálculos
    total_m = (largo + ancho) * 2 if tipo == "Perímetro" else largo
    s_pi = math.ceil(total_m / 3) + (1 if tipo == "Lineal" else 0)
    s_pr = math.floor(total_m / 25) + (4 if tipo == "Perímetro" else 2)
    s_tj = round(total_m * 1.05, 1)
    total_alambre_hilos = total_m * hilos

    if manual:
        cm1, cm2, cm3 = st.columns(3)
        p_int = cm1.number_input("Postes Int.", value=int(s_pi))
        p_ref = cm2.number_input("Postes Ref.", value=int(s_pr))
        m_tej = cm3.number_input("Metros Tejido", value=float(s_tj))
    else:
        p_int, p_ref, m_tej = s_pi, s_pr, s_tj

    def get_p(n, col):
        try: return float(df_s.loc[df_s["Producto"].str.contains(n, case=False, na=False), col].values[0])
        except: return 0.0

    costo_hilos = (total_alambre_hilos / 20) * get_p("Alambre", "Precio Venta") 
    venta_t = (p_int * get_p("Intermedio", "Precio Venta")) + (p_ref * get_p("Refuerzo", "Precio Venta")) + (m_tej * get_p("Tejido", "Precio Venta")) + costo_hilos

    st.divider()
    res1, res2 = st.columns([2, 1])
    detalle_carga = f"{p_int} Postes Int, {p_ref} Postes Ref, {m_tej}m Tejido, {hilos} Hilos ({total_alambre_hilos}m)"
    
    with res1:
        st.subheader("Resumen Materiales")
        st.write(f"• {p_int} Postes Int. | {p_ref} Postes Ref.")
        st.write(f"• {m_tej}m Tejido | {hilos} Hilos")
        st.caption(f"📍 Destino: {direccion}")
    
    with res2:
        st.metric("TOTAL", f"$ {venta_t:,.2f}")
        if st.button("🏁 CONFIRMAR VENTA"):
            # 1. Descuento Stock
            df_s.loc[df_s["Producto"].str.contains("Intermedio", case=False), "Cantidad"] -= p_int
            df_s.loc[df_s["Producto"].str.contains("Refuerzo", case=False), "Cantidad"] -= p_ref
            df_s.loc[df_s["Producto"].str.contains("Tejido", case=False), "Cantidad"] -= m_tej
            df_s.loc[df_s["Producto"].str.contains("Alambre", case=False), "Cantidad"] -= (total_alambre_hilos / 20)
            df_s.to_csv(STOCK_FILE, index=False)
            
            # 2. Guardar Venta
            pd.concat([cargar_datos(VENTAS_FILE), pd.DataFrame([{"Fecha": date.today(), "Cliente": cliente, "Monto Total": venta_t, "Ganancia": 0.0}])]).to_csv(VENTAS_FILE, index=False)
            
            # 3. Guardar Logística
            if direccion.lower() != "retira por local":
                nuevo_envio = pd.DataFrame([{
                    "Fecha": date.today(), "Cliente": cliente, "Direccion": direccion, 
                    "Carga": detalle_carga, "Estado": "Pendiente"
                }])
                pd.concat([cargar_datos(ENTREGAS_FILE), nuevo_envio]).to_csv(ENTREGAS_FILE, index=False)
                st.success("Venta guardada y enviada a Logística 🚚")
            else:
                st.success("Venta guardada (Retira cliente).")
            
            st.rerun()

    st.text_area("WhatsApp:", f"*Alambrados del Carmen*\nCliente: {cliente}\nObra: {total_m}m x {altura}m\nTotal: ${venta_t:,.2f}", height=80)

# TAB 2: INVENTARIO
with tab2:
    st.header("Inventario y Precios")
    df_s = cargar_datos(STOCK_FILE)
    
    # Botones de herramientas
    col_tools1, col_tools2 = st.columns([1, 3])
    with col_tools1:
        st.download_button("📥 Bajar Excel", descargar_excel(df_s), f"stock_{date.today()}.xlsx")
    with col_tools2:
        with st.expander("📈 Ajuste por Inflación (Masivo)"):
            porc = st.number_input("% Aumento", value=10.0)
            if st.button("Aplicar Aumento"):
                df_s["Precio Venta"] *= (1 + porc/100)
                df_s.to_csv(STOCK_FILE, index=False)
                st.success("Precios actualizados.")
                st.rerun()

    st.info("💡 Hacé doble clic en cualquier celda para editarla. Los cambios se guardan al apretar el botón de abajo.")

    # TABLA ÚNICA Y PODEROSA (Data Editor con Formato)
    df_edit = st.data_editor(
        df_s,
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True,
        key="editor_stock_final",
        column_config={
            "Producto": st.column_config.TextColumn("Nombre del Producto", required=True),
            "Cantidad": st.column_config.NumberColumn("Stock Real", help="Cantidad actual en galpón", format="%.1f"), # 1 decimal
            "Unidad": st.column_config.SelectboxColumn("Unidad", options=["un.", "kg", "m", "bolsas", "m3", "litros"], required=True),
            "Precio Costo": st.column_config.NumberColumn("Costo", format="$ %d"), # Sin decimales, con signo $
            "Precio Venta": st.column_config.NumberColumn("Precio Venta", format="$ %d"), # Sin decimales, con signo $
            "Stock Minimo": st.column_config.NumberColumn("Alerta Mínimo", help="Avísame cuando baje de este número", format="%d") # Entero puro
        }
    )

    # Semáforo simple (Texto abajo) para no bloquear la tabla
    criticos = df_edit[df_edit["Cantidad"] <= df_edit["Stock Minimo"]]
    if not criticos.empty:
        st.error(f"⚠️ ATENCIÓN: Tenés {len(criticos)} productos con stock bajo o crítico.")
        with st.expander("Ver lista de faltantes"):
            st.dataframe(criticos[["Producto", "Cantidad", "Stock Minimo"]])

    if st.button("💾 GUARDAR CAMBIOS DE STOCK", type="primary"):
        df_edit.to_csv(STOCK_FILE, index=False)
        st.success("¡Inventario actualizado correctamente!")
        st.rerun()

# TAB 3: ANÁLISIS 
with tab3:
    st.header("Estadísticas")
    df_v = cargar_datos(VENTAS_FILE)
    if not df_v.empty:
        st.metric("Ventas Totales", f"$ {df_v['Monto Total'].sum():,.2f}")
        st.bar_chart(df_v.set_index("Fecha")["Monto Total"])
    else: st.info("Sin datos.")

# TAB 4: GASTOS 
with tab4:
    st.header("Compras")
    df_g = cargar_datos(GASTOS_FILE)
    df_s = cargar_datos(STOCK_FILE)
    lista = ["---"] + df_s["Producto"].tolist() + ["+ NUEVO"]
    sel = st.selectbox("Insumo:", options=lista)

    with st.form("gasto"):
        nom, uni = "", "un."
        if sel == "+ NUEVO":
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nombre")
            uni = c2.selectbox("Unidad", ["un.", "kg", "m", "bolsas"])
        
        cant = st.number_input("Cantidad", min_value=0.1)
        monto = st.number_input("Monto ($)", min_value=0)
        
        if st.form_submit_button("Registrar"):
            item = nom if sel == "+ NUEVO" else sel
            if sel == "+ NUEVO":
                df_s = pd.concat([df_s, pd.DataFrame([{"Producto": nom, "Cantidad": cant, "Unidad": uni, "Precio Costo": monto/cant, "Precio Venta": 0.0, "Stock Minimo": 5.0}])], ignore_index=True)
            else:
                df_s.loc[df_s["Producto"] == item, "Cantidad"] += cant
            pd.concat([df_g, pd.DataFrame([{"Fecha": date.today(), "Insumo": item, "Cantidad": cant, "Monto": monto}])]).to_csv(GASTOS_FILE, index=False)
            df_s.to_csv(STOCK_FILE, index=False)
            st.rerun()

# --- TAB 5: FABRICACIÓN (ERROR CORREGIDO) ---
with tab5:
    st.header("⚒️ Fábrica")
    df_r = cargar_datos(RECETAS_FILE)
    df_s_act = cargar_datos(STOCK_FILE)

    st.subheader("1. Recetas")
    # ACÁ ESTABA EL ERROR: Agregué .tolist() al final para que Streamlit no se queje
    df_r_ed = st.data_editor(
        df_r, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=True, 
        column_config={
            "Insumo": st.column_config.SelectboxColumn(options=df_s_act["Producto"].unique().tolist())
        }
    )
    if st.button("💾 Guardar Receta"):
        df_r_ed.to_csv(RECETAS_FILE, index=False)
        st.rerun()

    st.divider()
    st.subheader("2. Producción")
    prods = df_r["Producto Final"].unique().tolist()
    if prods:
        with st.form("fab"):
            p = st.selectbox("Producto:", prods)
            c = st.number_input("Cantidad:", min_value=1)
            
            # Vista previa
            st.write("Se descontará:")
            rec = df_r[df_r["Producto Final"] == p]
            for _, r in rec.iterrows():
                st.write(f"- {r['Insumo']}: {r['Cantidad'] * c:.2f}")

            if st.form_submit_button("🚀 Fabricar"):
                df_stk = cargar_datos(STOCK_FILE)
                
                # Sumar Prod
                if p not in df_stk["Producto"].values:
                    df_stk = pd.concat([df_stk, pd.DataFrame([{"Producto": p, "Cantidad": c, "Unidad": "un.", "Precio Venta": 0.0, "Stock Minimo": 0.0}])], ignore_index=True)
                else: df_stk.loc[df_stk["Producto"] == p, "Cantidad"] += c
                
                # Restar Insumos
                for _, r in rec.iterrows():
                    if r['Insumo'] in df_stk["Producto"].values:
                        df_stk.loc[df_stk["Producto"] == r['Insumo'], "Cantidad"] -= (r['Cantidad'] * c)
                
                df_stk.to_csv(STOCK_FILE, index=False)
                st.success("Hecho.")
                st.rerun()

# --- TAB 6: LOGÍSTICA ---
with tab6:
    st.header("🚚 Hoja de Ruta")
    df_e = cargar_datos(ENTREGAS_FILE)
    pendientes = df_e[df_e["Estado"] == "Pendiente"]
    
    if pendientes.empty:
        st.info("✅ Todo entregado.")
    else:
        st.write(f"Pendientes: {len(pendientes)}")
        for index, row in pendientes.iterrows():
            with st.container(border=True):
                c_info, c_mapa, c_accion = st.columns([3, 1, 1])
                with c_info:
                    st.subheader(f"👤 {row['Cliente']}")
                    st.write(f"📍 {row['Direccion']}")
                    st.write(f"📦 {row['Carga']}")
                with c_mapa:
                    url_mapa = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(row['Direccion'])}"
                    st.link_button("📍 GPS", url_mapa)
                with c_accion:
                    if st.button("✅ Listo", key=f"ent_{index}"):
                        df_e.at[index, "Estado"] = "Entregado"
                        df_e.to_csv(ENTREGAS_FILE, index=False)
                        st.rerun()



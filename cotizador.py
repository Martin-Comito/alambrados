import streamlit as st
import pandas as pd
import math
import os
import io
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Del Carmen - Sistema Pro", layout="wide")

# Rutas de archivos
STOCK_FILE = "stock_del_carmen.csv"
GASTOS_FILE = "gastos_del_carmen.csv"
RECETAS_FILE = "recetas_del_carmen.csv"
VENTAS_FILE = "ventas_del_carmen.csv"

# --- INICIALIZACIÓN Y REPARACIÓN DE ARCHIVOS ---
def inicializar_archivos():
    # Columnas obligatorias
    cols_stock = ["Producto", "Cantidad", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    
    # 1. Chequeo de Stock
    if not os.path.exists(STOCK_FILE):
        pd.DataFrame(columns=cols_stock).to_csv(STOCK_FILE, index=False)
    else:
        # PARCHE DE SEGURIDAD: Agrega columnas faltantes si el archivo es viejo
        df_temp = pd.read_csv(STOCK_FILE)
        guardar = False
        for col in cols_stock:
            if col not in df_temp.columns:
                df_temp[col] = 0.0
                guardar = True
        if guardar:
            df_temp.to_csv(STOCK_FILE, index=False)

    # 2. Chequeo de otros archivos
    if not os.path.exists(GASTOS_FILE):
        pd.DataFrame(columns=["Fecha", "Insumo", "Cantidad", "Monto"]).to_csv(GASTOS_FILE, index=False)
    if not os.path.exists(VENTAS_FILE):
        pd.DataFrame(columns=["Fecha", "Cliente", "Monto Total", "Ganancia"]).to_csv(VENTAS_FILE, index=False)
    if not os.path.exists(RECETAS_FILE):
        pd.DataFrame(columns=["Producto Final", "Insumo", "Cantidad"]).to_csv(RECETAS_FILE, index=False)

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

# --- INTERFAZ PRINCIPAL ---
st.title("🏗️ Alambrados del Carmen S.A.")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Cotizador", "📦 Inventario", "📊 Análisis", "💰 Gastos", "⚒️ Fabricación"])

# --- TAB 1: COTIZADOR ---
with tab1:
    st.header("Presupuesto de Obra")
    df_s = cargar_datos(STOCK_FILE)
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Nombre del Cliente", "Venta Particular")
        
        # 1. Altura editable
        altura = c1.number_input("Altura del Cerco (m)", min_value=0.1, value=1.5, step=0.1)
        
        # 2. Hilos automáticos pero editables
        hilos_sug = 3 if altura <= 1.5 else 4
        hilos = c1.number_input("Cantidad de Hilos de Alambre", min_value=1, value=hilos_sug)
        
        tipo = c2.radio("Tipo de Obra:", ["Tramo Lineal", "Perímetro Completo"], horizontal=True)
        largo = c2.number_input("Metros Largo", min_value=1.0, value=20.0)
        ancho = c2.number_input("Metros Fondo", min_value=0.0) if tipo == "Perímetro Completo" else 0.0
        
        manual = st.toggle("🔓 EDITAR CANTIDADES MANUALMENTE")

    # Cálculos
    total_m = (largo + ancho) * 2 if tipo == "Perímetro Completo" else largo
    s_pi = math.ceil(total_m / 3) + (1 if tipo == "Tramo Lineal" else 0)
    s_pr = math.floor(total_m / 25) + (4 if tipo == "Perímetro Completo" else 2)
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

    # Precio Alambre (Estimado: stock en kg, rendimiento 20m/kg)
    precio_alambre_stock = get_p("Alambre", "Precio Venta") 
    costo_hilos = (total_alambre_hilos / 20) * precio_alambre_stock 

    venta_t = (p_int * get_p("Intermedio", "Precio Venta")) + \
              (p_ref * get_p("Refuerzo", "Precio Venta")) + \
              (m_tej * get_p("Tejido", "Precio Venta")) + \
              costo_hilos

    st.divider()
    res1, res2 = st.columns([2, 1])
    with res1:
        st.subheader("📋 Resumen de Materiales")
        st.write(f"• **{p_int}** Postes Intermedios")
        st.write(f"• **{p_ref}** Postes Refuerzo")
        st.write(f"• **{m_tej}m** Tejido Romboidal")
        st.write(f"• **{hilos}** Hilos ({total_alambre_hilos}m)")
    
    with res2:
        st.metric("PRECIO TOTAL", f"$ {venta_t:,.2f}")
        if st.button("🏁 CONFIRMAR VENTA"):
            # Descuento de stock
            df_s.loc[df_s["Producto"].str.contains("Intermedio", case=False), "Cantidad"] -= p_int
            df_s.loc[df_s["Producto"].str.contains("Refuerzo", case=False), "Cantidad"] -= p_ref
            df_s.loc[df_s["Producto"].str.contains("Tejido", case=False), "Cantidad"] -= m_tej
            df_s.loc[df_s["Producto"].str.contains("Alambre", case=False), "Cantidad"] -= (total_alambre_hilos / 20)
            
            df_s.to_csv(STOCK_FILE, index=False)
            pd.concat([cargar_datos(VENTAS_FILE), pd.DataFrame([{"Fecha": date.today(), "Cliente": cliente, "Monto Total": venta_t, "Ganancia": 0.0}])]).to_csv(VENTAS_FILE, index=False)
            st.success("Venta guardada.")
            st.rerun()

    wa_text = f"*Alambrados del Carmen*\nCliente: {cliente}\nObra: {total_m}m x {altura}m\nMateriales:\n- {p_int} Postes Int.\n- {p_ref} Postes Ref.\n- {m_tej}m Tejido\n- {hilos} Hilos Alambre\n💰 *Total: ${venta_t:,.2f}*"
    st.text_area("WhatsApp:", wa_text, height=100)

# --- TAB 2: INVENTARIO ---
with tab2:
    st.header("Inventario")
    df_s = cargar_datos(STOCK_FILE)
    
    # Botón Excel
    st.download_button(
        label="📥 Descargar Excel",
        data=descargar_excel(df_s),
        file_name=f"stock_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Aumento Masivo
    with st.expander("📈 Aumento Masivo (Inflación)"):
        porc = st.number_input("Porcentaje %", value=10.0)
        if st.button("Aplicar Aumento"):
            df_s["Precio Venta"] *= (1 + porc/100)
            df_s.to_csv(STOCK_FILE, index=False)
            st.success("Precios actualizados.")
            st.rerun()

    def color_stock(row):
        return ['background-color: #ff4b4b; color: white' if row['Cantidad'] <= row['Stock Minimo'] else '' for _ in row]

    st.dataframe(
        df_s.style.apply(color_stock, axis=1).format({"Cantidad": "{:.1f}", "Precio Costo": "${:.0f}", "Precio Venta": "${:.0f}", "Stock Minimo": "{:.0f}"}),
        use_container_width=True, hide_index=True
    )
    
    df_edit = st.data_editor(df_s, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_stock")
    if st.button("💾 Guardar Cambios"):
        df_edit.to_csv(STOCK_FILE, index=False)
        st.rerun()

# --- TAB 3: ANÁLISIS ---
with tab3:
    st.header("Estadísticas")
    df_v = cargar_datos(VENTAS_FILE)
    if not df_v.empty:
        st.bar_chart(df_v.set_index("Fecha")["Monto Total"])
        st.metric("Total Vendido", f"$ {df_v['Monto Total'].sum():,.2f}")
    else:
        st.info("No hay ventas registradas.")

# --- TAB 4: GASTOS ---
with tab4:
    st.header("Compras")
    df_g = cargar_datos(GASTOS_FILE)
    df_s = cargar_datos(STOCK_FILE)
    
    lista = ["---"] + df_s["Producto"].tolist() + ["+ NUEVO PRODUCTO"]
    sel = st.selectbox("Insumo:", options=lista)

    with st.form("gasto"):
        nom, uni = "", "un."
        if sel == "+ NUEVO PRODUCTO":
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nombre")
            uni = c2.selectbox("Unidad", ["un.", "kg", "m", "bolsas"])
        
        cant = st.number_input("Cantidad", min_value=0.1)
        monto = st.number_input("Monto Total ($)", min_value=0)
        
        if st.form_submit_button("Registrar"):
            item = nom if sel == "+ NUEVO PRODUCTO" else sel
            if sel == "+ NUEVO PRODUCTO":
                df_s = pd.concat([df_s, pd.DataFrame([{"Producto": nom, "Cantidad": cant, "Unidad": uni, "Precio Costo": monto/cant, "Precio Venta": 0.0, "Stock Minimo": 5.0}])], ignore_index=True)
            else:
                df_s.loc[df_s["Producto"] == item, "Cantidad"] += cant
            
            pd.concat([df_g, pd.DataFrame([{"Fecha": date.today(), "Insumo": item, "Cantidad": cant, "Monto": monto}])]).to_csv(GASTOS_FILE, index=False)
            df_s.to_csv(STOCK_FILE, index=False)
            st.rerun()

# --- TAB 5: FABRICACIÓN ---
with tab5:
    st.header("⚒️ Fábrica")
    df_r = cargar_datos(RECETAS_FILE)
    df_s_actual = cargar_datos(STOCK_FILE)

    st.subheader("1. Configurar Recetas")
    df_r_edit = st.data_editor(
        df_r, num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "Producto Final": st.column_config.TextColumn("Producto a Fabricar"),
            "Insumo": st.column_config.SelectboxColumn("Insumo", options=df_s_actual["Producto"].unique().tolist()),
            "Cantidad": st.column_config.NumberColumn("Cant. x Unidad")
        }
    )
    if st.button("💾 Guardar Recetas"):
        df_r_edit.to_csv(RECETAS_FILE, index=False)
        st.success("Guardado.")
        st.rerun()

    st.divider()
    st.subheader("2. Registrar Producción")
    prods = df_r["Producto Final"].unique().tolist()
    
    if prods:
        with st.form("fab"):
            p_sel = st.selectbox("Producto:", options=prods)
            c_sel = st.number_input("Cantidad:", min_value=1)
            
            # Vista previa
            receta = df_r[df_r["Producto Final"] == p_sel]
            st.write("Se descontará:")
            for _, r in receta.iterrows():
                st.write(f"- {r['Insumo']}: {r['Cantidad'] * c_sel:.2f}")

            if st.form_submit_button("🚀 Fabricar"):
                df_stk = cargar_datos(STOCK_FILE)
                # Sumar producto
                if p_sel not in df_stk["Producto"].values:
                    df_stk = pd.concat([df_stk, pd.DataFrame([{"Producto": p_sel, "Cantidad": c_sel, "Unidad": "un.", "Precio Venta": 0.0, "Stock Minimo": 0.0}])], ignore_index=True)
                else:
                    df_stk.loc[df_stk["Producto"] == p_sel, "Cantidad"] += c_sel
                
                # Restar insumos
                for _, r in receta.iterrows():
                    if r['Insumo'] in df_stk["Producto"].values:
                        df_stk.loc[df_stk["Producto"] == r['Insumo'], "Cantidad"] -= (r['Cantidad'] * c_sel)
                
                df_stk.to_csv(STOCK_FILE, index=False)
                st.success("Listo.")
                st.rerun()
    else:
        st.warning("Cargá una receta arriba primero.")

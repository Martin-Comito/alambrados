import streamlit as st
import pandas as pd
import math
import os
import io
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Del Carmen - Demo Pro", layout="wide")

# Archivos de datos
STOCK_FILE = "stock_del_carmen.csv"
GASTOS_FILE = "gastos_del_carmen.csv"
RECETAS_FILE = "recetas_del_carmen.csv"
VENTAS_FILE = "ventas_del_carmen.csv"

# --- INICIALIZACIÓN Y PARCHE DE SEGURIDAD ---
def inicializar_archivos():
    cols_stock = ["Producto", "Cantidad", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    if not os.path.exists(STOCK_FILE):
        pd.DataFrame(columns=cols_stock).to_csv(STOCK_FILE, index=False)
    else:
        df_temp = pd.read_csv(STOCK_FILE)
        for col in cols_stock:
            if col not in df_temp.columns:
                df_temp[col] = 0.0
        df_temp.to_csv(STOCK_FILE, index=False)

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

inicializar_archivos()

# --- INTERFAZ ---
st.title("🏗️ Alambrados del Carmen S.A.")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Cotizador", "📦 Inventario", "📊 Análisis", "💰 Gastos", "⚒️ Fabricación"])

# --- TAB 1: COTIZADOR (CON HILOS EDITABLES) ---
with tab1:
    st.header("Presupuesto de Obra")
    df_s = cargar_datos(STOCK_FILE)
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Nombre del Cliente", "Venta Particular")
        altura = c1.number_input("Altura del Cerco (m)", min_value=0.1, value=1.5, step=0.1)
        # NUEVA FUNCIÓN: Hilos de alambre editables
        hilos_sug = 3 if altura <= 1.5 else 4
        hilos = c1.number_input("Cantidad de hilos de alambre", min_value=1, value=hilos_sug)
        
        tipo = c2.radio("Tipo de cálculo:", ["Tramo Lineal", "Perímetro Completo"], horizontal=True)
        largo = c2.number_input("Metros Largo", min_value=1.0, value=20.0)
        ancho = c2.number_input("Metros Fondo", min_value=0.0) if tipo == "Perímetro Completo" else 0.0
        manual = st.toggle("🔓 EDITAR MATERIALES MANUALMENTE")

    total_m = (largo + ancho) * 2 if tipo == "Perímetro Completo" else largo
    s_pi = math.ceil(total_m / 3) + (1 if tipo == "Lineal" else 0)
    s_pr = math.floor(total_m / 25) + (4 if tipo == "Perímetro Completo" else 2)
    s_tj = round(total_m * 1.05, 1)
    # Cálculo de metros de alambre
    m_alambre_total = total_m * hilos

    if manual:
        col_m1, col_m2, col_m3 = st.columns(3)
        p_int = col_m1.number_input("Postes Intermedios", value=int(s_pi))
        p_ref = col_m2.number_input("Postes Refuerzo", value=int(s_pr))
        m_tej = col_m3.number_input("Metros Tejido", value=float(s_tj))
    else:
        p_int, p_ref, m_tej = s_pi, s_pr, s_tj

    def get_p(n, col):
        try: return float(df_s.loc[df_s["Producto"].str.contains(n, case=False, na=False), col].values[0])
        except: return 0.0

    # Precio basado en la configuración actual
    venta_t = (p_int * get_p("Intermedio", "Precio Venta")) + \
              (p_ref * get_p("Refuerzo", "Precio Venta")) + \
              (m_tej * get_p("Tejido", "Precio Venta")) + \
              (m_alambre_total * (get_p("Alambre", "Precio Venta") / 100)) # Ejemplo: precio por metro

    st.divider()
    res1, res2 = st.columns([2, 1])
    with res1:
        st.subheader("📋 Resumen para el Cliente")
        st.write(f"• **{p_int}** Postes Intermedios")
        st.write(f"• **{p_ref}** Postes de Refuerzo")
        st.write(f"• **{m_tej}m** Tejido Romboidal")
        st.write(f"• **{hilos}** Hilos de alambre (Total: {m_alambre_total}m)")
    
    with res2:
        st.metric("PRECIO VENTA ESTIMADO", f"$ {venta_t:,.2f}")
        if st.button("🏁 CONFIRMAR VENTA"):
            df_s.loc[df_s["Producto"].str.contains("Intermedio", case=False), "Cantidad"] -= p_int
            df_s.loc[df_s["Producto"].str.contains("Refuerzo", case=False), "Cantidad"] -= p_ref
            df_s.loc[df_s["Producto"].str.contains("Tejido", case=False), "Cantidad"] -= m_tej
            df_s.to_csv(STOCK_FILE, index=False)
            st.success("Venta realizada. Stock actualizado.")
            st.rerun()

    wa_text = f"*Alambrados del Carmen*\nCliente: {cliente}\nObra: {total_m}m x {altura}m\nMateriales:\n- {p_int} Postes Int.\n- {p_ref} Postes Ref.\n- {m_tej}m Tejido\n- {hilos} Hilos Alambre\n💰 *Total: ${venta_t:,.2f}*"
    st.text_area("Copiá para WhatsApp:", wa_text, height=140)

# --- TAB 2: INVENTARIO (FORMATO LIMPIO) ---
with tab2:
    st.header("Inventario de Galpón")
    df_s = cargar_datos(STOCK_FILE)
    # Formateo para quitar ceros decimales innecesarios
    st.dataframe(
        df_s.style.format({
            "Cantidad": "{:.1f}", 
            "Precio Costo": "$ {:.0f}", 
            "Precio Venta": "$ {:.0f}", 
            "Stock Minimo": "{:.0f}"
        }),
        use_container_width=True, hide_index=True
    )
    df_edit = st.data_editor(df_s, num_rows="dynamic", use_container_width=True, hide_index=True, key="ed_stk")
    if st.button("💾 Guardar Cambios Inventario"):
        df_edit.to_csv(STOCK_FILE, index=False)
        st.rerun()

# --- TAB 4: GASTOS (CON ALTA DE PRODUCTOS) ---
with tab4:
    st.header("Registrar Gastos")
    df_g = cargar_datos(GASTOS_FILE)
    df_s = cargar_datos(STOCK_FILE)
    
    lista_op = ["--- Seleccionar ---"] + df_s["Producto"].tolist() + ["+ AGREGAR PRODUCTO NUEVO"]
    sel_gasto = st.selectbox("Insumo comprado:", options=lista_op)

    with st.form("form_gastos", clear_on_submit=True):
        n_nom = ""
        if sel_gasto == "+ AGREGAR PRODUCTO NUEVO":
            n_nom = st.text_input("Nombre del nuevo material")
        
        c_g1, c_g2 = st.columns(2)
        cant_g = c_g1.number_input("Cantidad", min_value=0.1)
        monto_g = c_g2.number_input("Monto total ($)", min_value=0)
        
        if st.form_submit_button("Confirmar Gasto"):
            item = n_nom if sel_gasto == "+ AGREGAR PRODUCTO NUEVO" else sel_gasto
            if sel_gasto == "+ AGREGAR PRODUCTO NUEVO":
                nueva_f = pd.DataFrame([{"Producto": n_nom, "Cantidad": cant_g, "Unidad": "un.", "Precio Costo": monto_g/cant_g, "Precio Venta": 0.0, "Stock Minimo": 0.0}])
                df_s = pd.concat([df_s, nueva_f], ignore_index=True)
            else:
                df_s.loc[df_s["Producto"] == item, "Cantidad"] += cant_g
            
            pd.concat([df_g, pd.DataFrame([{"Fecha": date.today(), "Insumo": item, "Cantidad": cant_g, "Monto": monto_g}])]).to_csv(GASTOS_FILE, index=False)
            df_s.to_csv(STOCK_FILE, index=False)
            st.success("Gasto registrado y stock actualizado.")
            st.rerun()

# --- TAB 5: FABRICACIÓN (SISTEMA DE RECETAS DINÁMICAS) ---
with tab5:
    st.header("⚒️ Producción y Recetas Dinámicas")
    st.info("Aquí puedes crear cualquier ítem (como Tubos) y definir qué materiales usa.")
    
    df_r = cargar_datos(RECETAS_FILE)
    df_s_actual = cargar_datos(STOCK_FILE)

    # PARTE A: Definir la receta
    st.subheader("1. Configurar Recetas de Fabricación")
    df_r_edit = st.data_editor(
        df_r,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Producto Final": st.column_config.TextColumn("¿Qué estás fabricando?", help="Ej: Tubo de Cemento"),
            "Insumo": st.column_config.SelectboxColumn("Material necesario", options=df_s_actual["Producto"].tolist()),
            "Cantidad": st.column_config.NumberColumn("Cantidad por unidad", format="%.2f")
        }
    )
    if st.button("💾 Guardar / Actualizar Recetas"):
        df_r_edit.to_csv(RECETAS_FILE, index=False)
        st.success("Recetas guardadas.")
        st.rerun()

    st.divider()
    
    # PARTE B: Registrar fabricación
    st.subheader("2. Registrar Fabricación del Día")
    prods_finales = df_r["Producto Final"].unique().tolist()
    
    if not prods_finales:
        st.warning("Primero define una receta arriba para poder fabricar.")
    else:
        with st.form("ejecutar_fab"):
            prod_hacer = st.selectbox("Seleccionar producto fabricado", options=prods_finales)
            cant_hacer = st.number_input("Cantidad de piezas terminadas", min_value=1)
            
            receta_selec = df_r[df_r["Producto Final"] == prod_hacer]
            st.write("**Materiales que se descontarán automáticamente:**")
            for _, fila in receta_selec.iterrows():
                st.write(f"- {fila['Insumo']}: {fila['Cantidad'] * cant_hacer:.2f}")

            if st.form_submit_button("🚀 Finalizar y Descontar Materiales"):
                df_stk = cargar_datos(STOCK_FILE)
                # Sumar producto terminado
                if prod_hacer not in df_stk["Producto"].values:
                    nueva_f = pd.DataFrame([{"Producto": prod_hacer, "Cantidad": cant_hacer, "Unidad": "un.", "Precio Venta": 0.0}])
                    df_stk = pd.concat([df_stk, nueva_f], ignore_index=True)
                else:
                    df_stk.loc[df_stk["Producto"] == prod_hacer, "Cantidad"] += cant_hacer
                
                # Restar insumos de la receta
                for _, fila in receta_selec.iterrows():
                    df_stk.loc[df_stk["Producto"] == fila['Insumo'], "Cantidad"] -= (fila['Cantidad'] * cant_hacer)
                
                df_stk.to_csv(STOCK_FILE, index=False)
                st.success(f"¡Fabricación de {cant_hacer} {prod_hacer} registrada!")
                st.rerun()
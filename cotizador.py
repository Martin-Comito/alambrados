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
    # Columnas obligatorias para que no falle el sistema
    cols_stock = ["Producto", "Cantidad", "Unidad", "Precio Costo", "Precio Venta", "Stock Minimo"]
    
    # 1. Chequeo de Stock
    if not os.path.exists(STOCK_FILE):
        # Datos iniciales de prueba para que no arranque vacío
        pd.DataFrame({
            "Producto": ["Poste Intermedio", "Poste Refuerzo", "Tejido 1.50m", "Alambre", "Torniqueta"],
            "Cantidad": [50.0, 20.0, 100.0, 50.0, 100.0],
            "Unidad": ["un.", "un.", "m", "kg", "un."],
            "Precio Costo": [3000.0, 6000.0, 2500.0, 2000.0, 800.0],
            "Precio Venta": [5500.0, 9500.0, 4200.0, 3500.0, 1500.0],
            "Stock Minimo": [10.0, 5.0, 20.0, 10.0, 20.0]
        }).to_csv(STOCK_FILE, index=False)
    else:
        # PARCHE DE SEGURIDAD: Si el archivo existe pero le faltan columnas, las agrega.
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

inicializar_archivos()

# --- INTERFAZ ---
st.title("🏗️ Alambrados del Carmen S.A.")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Cotizador", "📦 Inventario", "📊 Análisis", "💰 Gastos", "⚒️ Fabricación"])

# --- TAB 1: COTIZADOR (HILOS Y ALTURA EDITABLES) ---
with tab1:
    st.header("Presupuesto de Obra")
    df_s = cargar_datos(STOCK_FILE)
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Nombre del Cliente", "Venta Particular")
        
        # 1. Altura editable
        altura = c1.number_input("Altura del Cerco (m)", min_value=0.1, value=1.5, step=0.1)
        
        # 2. Hilos automáticos pero editables
        hilos_sugeridos = 3 if altura <= 1.5 else 4
        hilos = c1.number_input("Cantidad de Hilos de Alambre", min_value=1, value=hilos_sugeridos)
        
        tipo = c2.radio("Tipo de Obra:", ["Tramo Lineal", "Perímetro Completo"], horizontal=True)
        largo = c2.number_input("Metros Largo", min_value=1.0, value=20.0)
        ancho = c2.number_input("Metros Fondo", min_value=0.0) if tipo == "Perímetro Completo" else 0.0
        
        manual = st.toggle("🔓 EDITAR CANTIDADES MANUALMENTE")

    # Cálculos de materiales
    total_m = (largo + ancho) * 2 if tipo == "Perímetro Completo" else largo
    s_pi = math.ceil(total_m / 3) + (1 if tipo == "Tramo Lineal" else 0)
    s_pr = math.floor(total_m / 25) + (4 if tipo == "Perímetro Completo" else 2)
    s_tj = round(total_m * 1.05, 1)
    
    # Cálculo de Alambre para los hilos (Metros lineales totales)
    total_alambre_hilos = total_m * hilos

    if manual:
        cm1, cm2, cm3 = st.columns(3)
        p_int = cm1.number_input("Postes Intermedios", value=int(s_pi))
        p_ref = cm2.number_input("Postes Refuerzo", value=int(s_pr))
        m_tej = cm3.number_input("Metros Tejido", value=float(s_tj))
    else:
        p_int, p_ref, m_tej = s_pi, s_pr, s_tj

    # Buscador de precios seguro
    def get_p(n, col):
        try: return float(df_s.loc[df_s["Producto"].str.contains(n, case=False, na=False), col].values[0])
        except: return 0.0

    # Precio Alambre: Asumimos rendimiento de 20m por kg (Ajustable)
    precio_alambre_stock = get_p("Alambre", "Precio Venta") 
    costo_hilos = (total_alambre_hilos / 20) * precio_alambre_stock 

    # Precio Total
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
        st.write(f"• **{hilos}** Hilos de alambre (Total: {total_alambre_hilos} metros lineales)")
    
    with res2:
        st.metric("PRECIO TOTAL ESTIMADO", f"$ {venta_t:,.2f}")
        if st.button("🏁 CONFIRMAR VENTA"):
            # Descuento de stock
            df_s.loc[df_s["Producto"].str.contains("Intermedio", case=False), "Cantidad"] -= p_int
            df_s.loc[df_s["Producto"].str.contains("Refuerzo", case=False), "Cantidad"] -= p_ref
            df_s.loc[df_s["Producto"].str.contains("Tejido", case=False), "Cantidad"] -= m_tej
            
            # Descontar alambre en kg (aprox)
            kg_alambre = total_alambre_hilos / 20 
            df_s.loc[df_s["Producto"].str.contains("Alambre", case=False), "Cantidad"] -= kg_alambre
            
            df_s.to_csv(STOCK_FILE, index=False)
            
            # Guardar Venta
            pd.concat([cargar_datos(VENTAS_FILE), pd.DataFrame([{"Fecha": date.today(), "Cliente": cliente, "Monto Total": venta_t, "Ganancia": 0.0}])]).to_csv(VENTAS_FILE, index=False)
            st.success("Venta confirmada y stock actualizado.")
            st.rerun()

    wa_text = f"*Alambrados del Carmen*\nCliente: {cliente}\nObra: {total_m}m x {altura}m\nMateriales:\n- {p_int} Postes Int.\n- {p_ref} Postes Ref.\n- {m_tej}m Tejido\n- {hilos} Hilos Alambre ({total_alambre_hilos}m)\n💰 *Total: ${venta_t:,.2f}*"
    st.text_area("Copiá para WhatsApp:", wa_text, height=140)

# --- TAB 2: INVENTARIO (FORMATO LIMPIO) ---
with tab2:
    st.header("Inventario de Galpón")
    df_s = cargar_datos(STOCK_FILE)
    
    # Función de semáforo
    def color_stock(row):
        return ['background-color: #ff4b4b; color: white' if row['Cantidad'] <= row['Stock Minimo'] else '' for _ in row]

    st.dataframe(
        df_s.style.apply(color_stock, axis=1).format({
            "Cantidad": "{:.1f}", 
            "Precio Costo": "$ {:.0f}", 
            "Precio Venta": "$ {:.0f}", 
            "Stock Minimo": "{:.0f}"
        }),
        use_container_width=True, hide_index=True
    )
    
    df_edit = st.data_editor(df_s, num_rows="dynamic", use_container_width=True, hide_index=True, key="editor_stock_principal")
    if st.button("💾 Guardar Cambios Inventario"):
        df_edit.to_csv(STOCK_FILE, index=False)
        st.rerun()

# --- TAB 3: ANÁLISIS ---
with tab3:
    st.header("Estadísticas")
    df_v = cargar_datos(VENTAS_FILE)
    if not df_v.empty:
        st.line_chart(df_v.set_index("Fecha")["Monto Total"])
        st.metric("Total Vendido Histórico", f"$ {df_v['Monto Total'].sum():,.2f}")
    else:
        st.info("Registrá una venta para ver estadísticas.")

# --- TAB 4: GASTOS (CON ALTA DE PRODUCTOS) ---
with tab4:
    st.header("Registrar Gastos / Compras")
    df_g = cargar_datos(GASTOS_FILE)
    df_s = cargar_datos(STOCK_FILE)
    
    lista_op = ["--- Seleccionar ---"] + df_s["Producto"].tolist() + ["+ AGREGAR PRODUCTO NUEVO"]
    sel_gasto = st.selectbox("Insumo comprado:", options=lista_op)

    with st.form("form_gastos", clear_on_submit=True):
        n_nom = ""
        n_un = "un."
        if sel_gasto == "+ AGREGAR PRODUCTO NUEVO":
            c_n1, c_n2 = st.columns(2)
            n_nom = c_n1.text_input("Nombre del nuevo material")
            n_un = c_n2.selectbox("Unidad", ["un.", "kg", "m", "bolsas", "m3"])
        
        c_g1, c_g2 = st.columns(2)
        cant_g = c_g1.number_input("Cantidad", min_value=0.1)
        monto_g = c_g2.number_input("Monto total ($)", min_value=0)
        
        if st.form_submit_button("Confirmar Gasto"):
            item = n_nom if sel_gasto == "+ AGREGAR PRODUCTO NUEVO" else sel_gasto
            
            # Si es nuevo, lo creamos en Stock
            if sel_gasto == "+ AGREGAR PRODUCTO NUEVO":
                if n_nom:
                    # Calculamos costo unitario aproximado
                    costo_unit = monto_g / cant_g if cant_g > 0 else 0
                    nueva_f = pd.DataFrame([{"Producto": n_nom, "Cantidad": cant_g, "Unidad": n_un, "Precio Costo": costo_unit, "Precio Venta": 0.0, "Stock Minimo": 5.0}])
                    df_s = pd.concat([df_s, nueva_f], ignore_index=True)
                else:
                    st.error("Debes escribir un nombre para el producto nuevo.")
                    st.stop()
            else:
                # Si existe, sumamos stock
                df_s.loc[df_s["Producto"] == item, "Cantidad"] += cant_g
            
            # Guardamos Gasto y Stock
            pd.concat([df_g, pd.DataFrame([{"Fecha": date.today(), "Insumo": item, "Cantidad": cant_g, "Monto": monto_g}])]).to_csv(GASTOS_FILE, index=False)
            df_s.to_csv(STOCK_FILE, index=False)
            st.success("Gasto registrado y stock actualizado.")
            st.rerun()

# --- TAB 5: FABRICACIÓN (RECETAS INFINITAS) ---
with tab5:
    st.header("⚒️ Producción y Recetas")
    st.markdown("""
    **Instrucciones:**
    1. En la tabla de arriba, definí tu receta. Si un producto lleva 3 cosas, agregá 3 filas con el mismo "Producto Final".
    2. Guardá los cambios.
    3. Usá el formulario de abajo para registrar la fabricación.
    """)
    
    df_r = cargar_datos(RECETAS_FILE)
    df_s_actual = cargar_datos(STOCK_FILE)

    # 1. CONFIGURACIÓN DE RECETAS
    st.subheader("1. Configurar Recetas")
    df_r_edit = st.data_editor(
        df_r,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Producto Final": st.column_config.TextColumn("Producto a Fabricar", help="Escribí aquí el nombre (ej: Tubo 1m)"),
            "Insumo": st.column_config.SelectboxColumn("Insumo del Stock", options=df_s_actual["Producto"].unique().tolist()),
            "Cantidad": st.column_config.NumberColumn("Cantidad usada por unidad", format="%.2f")
        }
    )
    if st.button("💾 Guardar Recetas"):
        df_r_edit.to_csv(RECETAS_FILE, index=False)
        st.success("Recetas actualizadas. Ahora aparecen en el menú de abajo.")
        st.rerun()

    st.divider()
    
    # 2. REGISTRO DE FABRICACIÓN
    st.subheader("2. Registrar Producción del Día")
    
    # Obtenemos la lista única de cosas que tienen receta
    prods_fabricables = df_r["Producto Final"].unique().tolist()
    
    if not prods_fabricables:
        st.warning("No hay recetas definidas. Agregá una en la tabla de arriba.")
    else:
        with st.form("ejecutar_fab"):
            prod_hacer = st.selectbox("¿Qué fabricaste hoy?", options=prods_fabricables)
            cant_hacer = st.number_input("Cantidad fabricada", min_value=1)
            
            # Mostrar vista previa de descuento
            receta_selec = df_r[df_r["Producto Final"] == prod_hacer]
            st.write("**Materiales que se descontarán:**")
            for _, fila in receta_selec.iterrows():
         st.write(f"- {fila['Insumo']}: {fila['Cantidad'] * cant_hacer:.2f}")

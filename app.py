# --- DETECCIÓN INTELIGENTE MEJORADA PARA TU EXCEL REAL ---
        for col in df.columns:
            c_upper = str(col).upper().strip()
            
            # Buscamos el Producto (en tu caso es 'Fabricante' o 'Modelo')
            if any(x in c_upper for x in ['FABRICANTE', 'PRODUCTO', 'MODELO', 'ITEM']):
                if 'Producto' not in df.columns: # Evitamos duplicados
                    df.rename(columns={col: 'Producto'}, inplace=True)
            
            # Buscamos el Precio de Venta (en tu caso es 'Importe' o 'Precio')
            elif any(x in c_upper for x in ['IMPORTE', 'PRECIO', 'VENTA']):
                if 'Precio_Venta' not in df.columns:
                    df.rename(columns={col: 'Precio_Venta'}, inplace=True)
            
            # Buscamos el Coste (en tu caso es 'Coste')
            elif any(x in c_upper for x in ['COSTE', 'COSTO', 'COMPRA']):
                if 'Coste_Unidad' not in df.columns:
                    df.rename(columns={col: 'Coste_Unidad'}, inplace=True)
            
            # Buscamos las Unidades (en tu caso es 'Cantidad')
            elif any(x in c_upper for x in ['CANTIDAD', 'VENTAS', 'UNIDADES']):
                if 'Ventas_Mes_Unidades' not in df.columns:
                    df.rename(columns={col: 'Ventas_Mes_Unidades'}, inplace=True)

        # Verificación de seguridad
        cols_necesarias = ['Producto', 'Precio_Venta', 'Coste_Unidad', 'Ventas_Mes_Unidades']

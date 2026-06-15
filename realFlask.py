import os
from flask import Flask
from flask import request
from flask import render_template
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Hasta aquí es solo formato.
# Esto es para conectarse a la base de datos en supabase.
# La carpeta .env contiene la supabase url y la publishable key.
# Eso lo tendremos que quitar del git luego, se supone que es privado. 
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_PUBLISHABLE_KEY")
)

# index() es básicamente lo que se carga inicialmente. Por ahora,
# está puesto que cargue el cliente.html automáticamente,
# pero eso lo cambiaremos a un menú principal y lo dividiremos
# cuando tengamos las otras páginas.

# NOTA: las páginas html tienen que estar dentro de templates

@app.route('/pedidos.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def pedidos():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            cliente = request.form['IDClienteCrear']
            fechaPedido = request.form['fechaPedidoCrear']
            fechaLimite = request.form['fechaLimiteCrear']
            vendedor = request.form['IDVendedorCrear']

            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("pedidos").insert({"cliente_asociado": cliente, "fecha_pedido": fechaPedido,
                        "fecha_entrega": fechaLimite, "vendedor_asociado": vendedor
                        }).execute()
            )
            if response.data:
                return "Pedido creado exitosamente"
            else:
                return "Error creando pedido", 500
        if (metodo == "put"):
            idAACtualizar = request.form['IdPedidoActualizar']
            cliente = request.form['IDClienteActualizar']
            fechaPedido = request.form['fechaPedidoActualizar']
            fechaLimite = request.form['fechaLimiteActualizar']
            vendedor = request.form['IDVendedorActualizar']
            response = (
                
                supabase.table("pedidos").update({"cliente_asociado": cliente, "fecha_pedido": fechaPedido,
                        "fecha_entrega": fechaLimite, "vendedor_asociado": vendedor
                        }).eq("id_pedido", idAACtualizar).select("id_pedido").execute()
            )
            if response.data:
                return "Pedido actualizado exitosamente"
            else:
                return "Error actualizando pedido", 500
        if (metodo == "delete"):
            idABorrar = request.form['idPedidoBorrar']
            response = (
                supabase.table("pedidos").delete()
                .eq("id_pedido", idABorrar)
                .execute()
            )
            if response.data:
                return "Pedido borrado exitosamente"
            else:
                return "Error borrando pedido", 500
                
    else:
        response =(
            supabase.table("pedidos").select("*").execute()
        )
            
        return render_template('pedidos.html', datos = response.data)


@app.route('/cortes.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def cortes():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            fecha = request.form['fechaCorteCrear']
            cortador = request.form['cortadorCrear']
            cantidad = request.form['cantidadCrear']
            observaciones = request.form['observacionesCrear']
            material = request.form['materialCrear']
            idProducto = request.form['IdProductoCrear']
            #Hasta aquí toma los datos que se enviaron desde cliente.html cuando
            #se pulsó el botón con submit.

            #Esto se encapsula en response para poder detectar y loggear errores.
            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("cortes").insert({"fecha_corte": fecha, "cantidad": cantidad,
                        "cortador": cortador, "observaciones": observaciones, "material_usado": material, 
                        "producto_asociado": idProducto
                        }).execute()
            )
            if response.data:
                return "Corte creado exitosamente"
            else:
                return "Error creando corte", 500
        if (metodo == "put"):
            idAACtualizar = request.form['IdCorteActualizar']
            fecha = request.form['fechaCorteActualizar']
            cortador = request.form['cortadorActualizar']
            cantidad = request.form['cantidadActualizar']
            observaciones = request.form['observacionesActualizar']
            material = request.form['materialActualizar']
            idProducto = request.form['IdProductoActualizar'] 
            response = (
                
                supabase.table("cortes").update({"fecha_corte": fecha, "cantidad": cantidad,
                        "cortador": cortador, "observaciones": observaciones, "material_usado": material, 
                        "producto_asociado": idProducto
                        }).eq("id_corte", idAACtualizar).select("id_corte").execute()
            )
            if response.data:
                return "Corte actualizado exitosamente"
            else:
                return "Error actualizando corte", 500
        if (metodo == "delete"):
            idABorrar = request.form['idCorteBorrar']
            response = (
                supabase.table("cortes").delete()
                .eq("id_corte", idABorrar)
                .execute()
            )
            if response.data:
                return "Corte borrado exitosamente"
            else:
                return "Error borrando corte", 500
                
    else:
        response =(
            supabase.table("cortes").select("*").execute()
        )
            
        return render_template('cortes.html', datos = response.data)


@app.route('/clientes.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def clientes():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            rut = request.form['rut']
            nom = request.form['nombre']
            correo = request.form['correo']
            tf = request.form['telefono']
            direccion = request.form['direccion']
            digVer = request.form['digVer']
            abreviacion = request.form['abreviacion']
            ciudad = request.form['ciudad']
            comuna = request.form['comuna']
            condVenta = request.form['condicionesVenta']
            viaDes = request.form['viaDespacho']
            porComi = request.form['porComision']
            porCobra = request.form['porCobranza']
            obs = request.form['observaciones']
            idZona = request.form.get('idZonaVentaForm')
            #Hasta aquí toma los datos que se enviaron desde cliente.html cuando
            #se pulsó el botón con submit.

            #Esto se encapsula en response para poder detectar y loggear errores.
            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("clientes").insert({"rut": rut, "nombre": nom,
                        "correo": correo, "telefono": tf, "direccion": direccion, 
                        "digito_verificador": digVer,
                        "abreviacion": abreviacion,"ciudad": ciudad,
                        "comuna": comuna, "condiciones_venta": condVenta,
                        "via_despacho": viaDes,"porcentaje_comision": porComi,
                        "porcentaje_cobranza": porCobra,"observaciones": obs,
                        "id_zona_venta": idZona
                        }).execute()
            )
            if response.data:
                return "Cliente creado exitosamente"
            else:
                return "Error creando cliente", 500
        if (metodo == "put"):
            idAACtualizar = request.form['idClienteActualizar']
            rut = request.form['rutActualizar']
            nom = request.form['nombreActualizar']
            correo = request.form['correoActualizar']
            tf = request.form['telefonoActualizar']
            direccion = request.form['direccionActualizar']
            digVer = request.form['digVerActualizar']
            abreviacion = request.form['abreviacionActualizar']
            ciudad = request.form['ciudadActualizar']
            comuna = request.form['comunaActualizar']
            condVenta = request.form['condicionesVentaActualizar']
            viaDes = request.form['viaDespachoActualizar']
            porComi = request.form['porComisionActualizar']
            porCobra = request.form['porCobranzaActualizar']
            obs = request.form['observacionesActualizar']
            idZona = request.form.get('idZonaVentaActualizar')  
            response = (
                
                supabase.table("clientes").update({"rut": rut, "nombre": nom,
                        "correo": correo, "telefono": tf, "direccion": direccion, 
                        "digito_verificador": digVer,
                        "abreviacion": abreviacion,"ciudad": ciudad,
                        "comuna": comuna, "condiciones_venta": condVenta,
                        "via_despacho": viaDes,"porcentaje_comision": porComi,
                        "porcentaje_cobranza": porCobra,"observaciones": obs,
                        "id_zona_venta": idZona
                        }).eq("id_cliente", idAACtualizar).select("id_cliente").execute()
            )
            if response.data:
                return "Cliente actualizado exitosamente"
            else:
                return "Error actualizando cliente", 500
        if (metodo == "delete"):
            idABorrar = request.form['idClienteBorrar']
            response = (
                supabase.table("clientes").delete()
                .eq("id_cliente", idABorrar)
                .execute()
            )
            if response.data:
                return "Cliente borrado exitosamente"
            else:
                return "Error borrando cliente", 500
                
    else:
        response =(
            supabase.table("clientes").select("*").execute()
        )
            
        return render_template('clientes.html', datos = response.data)

@app.route('/colores.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def colores():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            codigo = request.form['codigoCrear']
            descripcion = request.form['descripcionCrear']

            #Hasta aquí toma los datos que se enviaron desde cliente.html cuando
            #se pulsó el botón con submit.

            #Esto se encapsula en response para poder detectar y loggear errores.
            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("colores").insert({"codigo_color": codigo, "descripcion": descripcion,
                        }).execute()
            )
            if response.data:
                return "Color creado exitosamente"
            else:
                return "Error creando color", 500
        if (metodo == "put"):
            idColor = request.form['idColorActualizar']
            codigo = request.form['codigoActualizar']
            descripcion = request.form['descripcionActualizar'] 
            response = (
                
                supabase.table("colores").update({"codigo_color": codigo, "descripcion": descripcion,
                        }).eq("id_color", idColor).select("id_color").execute()
            )
            if response.data:
                return "Color actualizado exitosamente"
            else:
                return "Error actualizando color", 500
        if (metodo == "delete"):
            idABorrar = request.form['idColorBorrar']
            response = (
                supabase.table("colores").delete()
                .eq("id_color", idABorrar)
                .execute()
            )
            if response.data:
                return "Color borrado exitosamente"
            else:
                return "Error borrando color", 500
                
    else:
        response =(
            supabase.table("colores").select("*").execute()
        )
            
        return render_template('colores.html', datos = response.data)
    
@app.route('/bodegas.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def bodegas():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            descripcion = request.form['descripcionCrear']

            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("bodegas").insert({"descripcion": descripcion
                        }).execute()
            )
            if response.data:
                return "Bodega creada exitosamente"
            else:
                return "Error creando bodega", 500
        if (metodo == "put"):
            idBodega = request.form['IdBodegaActualizar']
            descripcion = request.form['descripcionActualizar'] 
            response = (
                
                supabase.table("bodegas").update({"descripcion": descripcion
                        }).eq("id_bodega", idBodega).select("id_bodega").execute()
            )
            if response.data:
                return "Bodega actualizada exitosamente"
            else:
                return "Error actualizando bodega", 500
        if (metodo == "delete"):
            idABorrar = request.form['idBodegaBorrar']
            response = (
                supabase.table("bodegas").delete()
                .eq("id_bodega", idABorrar)
                .execute()
            )
            if response.data:
                return "Bodega borrada exitosamente"
            else:
                return "Error borrando bodega", 500
                
    else:
        response =(
            supabase.table("bodegas").select("*").execute()
        )
            
        return render_template('bodegas.html', datos = response.data)

@app.route('/vendedores.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def vendedores():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            nombre = request.form['nombreCrear']
            rut = request.form['rutCrear']
            digVer = request.form['digVerCrear']
            porComi = request.form['porComiCrear']
            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("vendedores").insert({"rut": rut, "nombre": nombre,
                        "digito_verificador": digVer, "porcentaje_comision": porComi
                        }).execute()
            )
            if response.data:
                return "Vendedor creado exitosamente"
            else:
                return "Error creando vendedor", 500
        if (metodo == "put"):
            idVendedor = request.form['IdVendedorActualizar']
            nombre = request.form['nombreActualizar']
            rut = request.form['rutActualizar']
            digVer = request.form['digVerActualizar']
            porComi = request.form['porComiActualizar']
            response = (
                
                supabase.table("vendedores").update({"rut": rut, "nombre": nombre,
                        "digito_verificador": digVer, "porcentaje_comision": porComi
                        }).eq("id_vendedor", idVendedor).select("id_vendedor").execute()
            )
            if response.data:
                return "Vendedor actualizado exitosamente"
            else:
                return "Error actualizando vendedor", 500
        if (metodo == "delete"):
            idABorrar = request.form['idVendedorBorrar']
            response = (
                supabase.table("vendedores").delete()
                .eq("id_vendedor", idABorrar)
                .execute()
            )
            if response.data:
                return "Vendedor borrado exitosamente"
            else:
                return "Error borrando vendedor", 500
                
    else:
        response =(
            supabase.table("vendedores").select("*").execute()
        )
            
        return render_template('vendedores.html', datos = response.data)

@app.route('/zonasVenta.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def zonasVenta():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            descripcion = request.form['descripcionCrear'] 

            #Hasta aquí toma los datos que se enviaron desde cliente.html cuando
            #se pulsó el botón con submit.

            #Esto se encapsula en response para poder detectar y loggear errores.
            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("zona_venta").insert({"descripcion": descripcion
                        }).execute()
            )
            if response.data:
                return "Zona de venta creada exitosamente"
            else:
                return "Error creando zona de venta", 500
        if (metodo == "put"):
            idZonaVenta = request.form['IdZonaVentaActualizar']
            descripcion = request.form['descripcionActualizar'] 
            response = (
                
                supabase.table("zona_venta").update({"descripcion": descripcion
                        }).eq("id_zona_venta", idZonaVenta).select("id_zona_venta").execute()
            )
            if response.data:
                return "Zona de venta actualizada exitosamente"
            else:
                return "Error actualizando zona de venta", 500
        if (metodo == "delete"):
            idABorrar = request.form['idZonaVentaBorrar']
            response = (
                supabase.table("zona_venta").delete()
                .eq("id_zona_venta", idABorrar)
                .execute()
            )
            if response.data:
                return "Zona de venta borrada exitosamente"
            else:
                return "Error borrando zona de venta", 500
                
    else:
        response =(
            supabase.table("zona_venta").select("*").execute()
        )
            
        return render_template('zonasVenta.html', datos = response.data)

@app.route('/tallas.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def tallas():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            talla = request.form['tallaCrear']

            #Hasta aquí toma los datos que se enviaron desde cliente.html cuando
            #se pulsó el botón con submit.

            #Esto se encapsula en response para poder detectar y loggear errores.
            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("tallas").insert({"talla": talla
                        }).execute()
            )
            if response.data:
                return "Talla creada exitosamente"
            else:
                return "Error creando talla", 500
        if (metodo == "put"):
            idTalla = request.form['IdTallaActualizar']
            talla = request.form['tallaActualizar'] 
            response = (
                
                supabase.table("tallas").update({"talla": talla
                        }).eq("id_talla", idTalla).select("id_talla").execute()
            )
            if response.data:
                return "Talla actualizada exitosamente"
            else:
                return "Error actualizando talla", 500
        if (metodo == "delete"):
            idABorrar = request.form['idTallaBorrar']
            response = (
                supabase.table("tallas").delete()
                .eq("id_talla", idABorrar)
                .execute()
            )
            if response.data:
                return "Talla borrada exitosamente"
            else:
                return "Error borrando talla", 500
                
    else:
        response =(
            supabase.table("tallas").select("*").execute()
        )
            
        return render_template('tallas.html', datos = response.data)

@app.route('/productos.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def productos():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            descripcion = request.form['descripcionCrear']
            abreviacion = request.form['abreviacionCrear']
            idColor = request.form['idColorCrear']
            precio = request.form['precioCrear']
            idTalla = request.form['idTallaCrear'] 

            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("productos").insert({"abreviacion": abreviacion, "descripcion": descripcion,
                        "color": idColor, "precio": precio, "talla": idTalla
                        }).execute()
            )
            if response.data:
                return "Producto creado exitosamente"
            else:
                return "Error creando producto", 500
        if (metodo == "put"):
            idProducto = request.form['IdProductoActualizar']
            descripcion = request.form['descripcionActualizar']
            abreviacion = request.form['abreviacionActualizar']
            idColor = request.form['idColorActualizar']
            precio = request.form['precioActualizar']
            idTalla = request.form['idTallaActualizar'] 
            response = (
                
                supabase.table("productos").update({"abreviacion": abreviacion, "descripcion": descripcion,
                        "color": idColor, "precio": precio, "talla": idTalla}).eq("id_producto", idProducto).select("id_producto").execute()
            )
            if response.data:
                return "Producto actualizado exitosamente"
            else:
                return "Error actualizando producto", 500
        if (metodo == "delete"):
            idABorrar = request.form['idProductoBorrar']
            response = (
                supabase.table("productos").delete()
                .eq("id_producto", idABorrar)
                .execute()
            )
            if response.data:
                return "Producto borrado exitosamente"
            else:
                return "Error borrando producto", 500
                
    else:
        response =(
            supabase.table("productos").select("*").execute()
        )
            
        return render_template('productos.html', datos = response.data)

@app.route('/codigosEAN.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def codigosEAN():
    if request.method == 'POST':
        metodo = request.form['_method']
        if (metodo == "post"):
            producto = request.form['idProductoCrear']
            tempCodigo = request.form['codigoCrear']

            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("codigos_EAN").insert({"producto_asociado": producto,
                        "temp_codigo": tempCodigo
                        }).execute()
            )
            if response.data:
                return "Código EAN creado exitosamente"
            else:
                return "Error creando Código EAN", 500
        if (metodo == "put"):
            idCodigo = request.form['IdCodigoActualizar']
            producto = request.form['idProductoActualizar']
            tempCodigo = request.form['codigoActualizar']
            response = (
                
                supabase.table("codigos_EAN").update({"producto_asociado": producto,
                        "temp_codigo": tempCodigo
                        }).eq("id_codigo_EAN", idCodigo).select("id_codigo_EAN").execute()
            )
            if response.data:
                return "Código EAN actualizado exitosamente"
            else:
                return "Error actualizando Código EAN", 500
        if (metodo == "delete"):
            idABorrar = request.form['idCodigoBorrar']
            response = (
                supabase.table("codigos_EAN").delete()
                .eq("id_codigo_EAN", idABorrar)
                .execute()
            )
            if response.data:
                return "Código EAN borrado exitosamente"
            else:
                return "Error borrando Código EAN", 500
                
    else:
        response =(
            supabase.table("codigos_EAN").select("*").execute()
        )
            
        return render_template('codigosEAN.html', datos = response.data)


@app.route('/archivosMaestros.html', methods=['GET'])
def archivosMaestros():
        return render_template('archivosMaestros.html')

@app.route('/produccion.html', methods=['GET'])      
def produccion():
        return render_template('produccion.html')

@app.route('/', methods=['GET'])
def index():
        return render_template('index.html')

#Esto simplemente lo corre en debug mode
if __name__ == '__main__':
    app.run(debug=True)
import os
import re
from datetime import datetime, timezone
from flask import Flask
from flask import flash
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from supabase import create_client, Client
from dotenv import load_dotenv
from postgrest.exceptions import APIError
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# Hasta aquí es solo formato.
# Esto es para conectarse a la base de datos en supabase.
# La carpeta .env contiene la supabase url y la publishable key.
# Eso lo tendremos que quitar del git luego, se supone que es privado. 
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_PUBLISHABLE_KEY")
)

SYSTEM_PARAMETER_DEFAULTS = {
    "id": 1,
    "razon_social": "",
    "rut": "",
    "giro": "",
    "direccion": "",
    "telefono": "",
    "correo": "",
    "moneda": "CLP",
    "formato_moneda": "$#,##0",
    "porcentaje_impuesto": 0,
    "logotipo": "img/logo.png",
    "fecha_actualizacion": None,
    "usuario_actualizacion": "Admin"
}
ALLOWED_LOGO_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_LOGO_SIZE = 2 * 1024 * 1024


def obtener_parametros_sistema():
    """Returns the singleton configuration, or defaults if it is not configured yet."""
    response = supabase.table("parametros_sistema").select("*").eq("id", 1).execute()
    if not response.data:
        return SYSTEM_PARAMETER_DEFAULTS.copy()
    return {**SYSTEM_PARAMETER_DEFAULTS, **response.data[0]}


def obtener_porcentaje_impuesto():
    """Shared accessor for future order/document amount calculations."""
    return float(obtener_parametros_sistema().get("porcentaje_impuesto", 0))


def obtener_moneda_sistema():
    """Shared accessor for future amount formatting and generated documents."""
    parametros = obtener_parametros_sistema()
    return parametros.get("moneda", "CLP"), parametros.get("formato_moneda", "$#,##0")


def obtener_url_logotipo():
    """Builds the static URL for the configured logo, with the current logo as fallback."""
    parametros = obtener_parametros_sistema()
    return url_for("static", filename=parametros.get("logotipo", "img/logo.png"))

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

            try:
                cliente = int(cliente)
                vendedor = int(vendedor)
            except ValueError:
                flash("El cliente o vendedor seleccionado no es válido", "error")
                return redirect(url_for('pedidos'))

            try:
                response = (
                    supabase.table("pedidos").insert({"cliente_asociado": cliente, "fecha_pedido": fechaPedido,
                            "fecha_entrega": fechaLimite, "vendedor_asociado": vendedor
                            }).execute()
                )
            except APIError:
                flash("No se pudo crear el pedido. Revisa el cliente y vendedor seleccionados", "error")
                return redirect(url_for('pedidos'))
            if response.data:
                flash("Pedido creado exitosamente", "success")
                return redirect(url_for('pedidos'))
            else:
                flash("Error creando pedido", "error")
                return redirect(url_for('pedidos'))
        if (metodo == "put"):
            idAACtualizar = request.form['IdPedidoActualizar']
            cliente = request.form['IDClienteActualizar']
            fechaPedido = request.form['fechaPedidoActualizar']
            fechaLimite = request.form['fechaLimiteActualizar']
            vendedor = request.form['IDVendedorActualizar']
            try:
                cliente = int(cliente)
                vendedor = int(vendedor)
            except ValueError:
                flash("El cliente o vendedor seleccionado no es válido", "error")
                return redirect(url_for('pedidos'))
            response = (
                
                supabase.table("pedidos").update({"cliente_asociado": cliente, "fecha_pedido": fechaPedido,
                        "fecha_entrega": fechaLimite, "vendedor_asociado": vendedor
                        }).eq("id_pedido", idAACtualizar).select("id_pedido").execute()
            )
            if response.data:
                flash("Pedido actualizado exitosamente", "success")
                return redirect(url_for('pedidos'))
            else:
                flash("Error actualizando pedido", "error")
                return redirect(url_for('pedidos'))
        if (metodo == "delete"):
            idABorrar = request.form['idPedidoBorrar']
            response = (
                supabase.table("pedidos").delete()
                .eq("id_pedido", idABorrar)
                .execute()
            )
            if response.data:
                flash("Pedido borrado exitosamente", "success")
                return redirect(url_for('pedidos'))
            else:
                flash("Error borrando pedido", "error")
                return redirect(url_for('pedidos'))
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscarpedidoid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('pedidos.html', datos = response.data)
            else:
                return "No se ha encontrado ningún pedido con la id buscada"                
    else:
        response =(
            supabase.table("pedidos").select("*").execute()
        )
        clientes_response = supabase.table("clientes").select("id_cliente, nombre").execute()
        vendedores_response = supabase.table("vendedores").select("id_vendedor, nombre").execute()
            
        return render_template(
            'pedidos.html',
            datos=response.data,
            clientes=clientes_response.data,
            vendedores=vendedores_response.data
        )


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
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscarcorteid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('cortes.html', datos = response.data)
            else:
                return "No se ha encontrado ningún corte con la id buscada" 
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
                flash("Cliente creado exitosamente", "success")
                return redirect(url_for('clientes'))
            else:
                flash("Error creando cliente", "error")
                return redirect(url_for('clientes'))
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
                flash("Cliente actualizado exitosamente", "success")
                return redirect(url_for('clientes'))
            else:
                flash("Error actualizando cliente", "error")
                return redirect(url_for('clientes'))
        if (metodo == "delete"):
            idABorrar = request.form['idClienteBorrar']
            response = (
                supabase.table("clientes").delete()
                .eq("id_cliente", idABorrar)
                .execute()
            )
            if response.data:
                flash("Cliente borrado exitosamente", "success")
                return redirect(url_for('clientes'))
            else:
                flash("Error borrando cliente", "error")
                return redirect(url_for('clientes'))
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscarclienteid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('clientes.html', datos = response.data)
            else:
                return "No se ha encontrado ningún cliente con la id buscada"
        if (metodo == "buscarNombre"):
            texto = request.form["nombreBuscar"]
            response = supabase.rpc('buscarclientenombre', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('clientes.html', datos = response.data)
            else:
                return "No se ha encontrado ningún cliente con el nombre buscado"
        if (metodo == "buscarAbreviacion"):
            texto = request.form["abreviacionBuscar"]
            response = supabase.rpc('buscarclienteabreviacion', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('clientes.html', datos = response.data)
            else:
                return "No se ha encontrado ningún cliente con la abreviacion buscada" 
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
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscarcolorid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('colores.html', datos = response.data)
            else:
                return "No se ha encontrado ningún color con la id buscada"
        if (metodo == "buscarDescripcion"):
            texto = request.form["descripcionBuscar"]
            response = supabase.rpc('buscarcolordescripcion', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('colores.html', datos = response.data)
            else:
                return "No se ha encontrado ningún color con la descrpición buscada"
        if (metodo == "buscarCodigo"):
            texto = request.form["descripcionBuscar"]
            response = supabase.rpc('buscarcolorcodigo', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('colores.html', datos = response.data)
            else:
                return "No se ha encontrado ningún color con el código buscado"
    else:
        response =(
            supabase.table("colores").select("*").execute()
        )
            
        return render_template('colores.html', datos = response.data)
    
@app.route('/bodegas.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def bodegas():
    if request.method == 'POST':
        metodo = request.form['_method']
        if metodo == "inventario_post":
            response = supabase.table("inventario").insert({
                "id_bodega": request.form['idBodegaInventario'],
                "id_producto": request.form['idProductoInventario'],
                "id_talla": request.form['idTallaInventario'],
                "id_color": request.form['idColorInventario'],
                "cantidad": request.form['cantidadInventario']
            }).execute()
            if response.data:
                return redirect(url_for('bodegas'))
            return "Error creando registro de inventario", 500
        if metodo == "inventario_put":
            idInventario = request.form['idInventarioActualizar']
            response = supabase.table("inventario").update({
                "id_bodega": request.form['idBodegaInventarioActualizar'],
                "id_producto": request.form['idProductoInventarioActualizar'],
                "id_talla": request.form['idTallaInventarioActualizar'],
                "id_color": request.form['idColorInventarioActualizar'],
                "cantidad": request.form['cantidadInventarioActualizar']
            }).eq("id_inventario", idInventario).select("id_inventario").execute()
            if response.data:
                return redirect(url_for('bodegas'))
            return "Error actualizando registro de inventario", 500
        if metodo == "inventario_delete":
            response = supabase.table("inventario").delete().eq(
                "id_inventario", request.form['idInventarioBorrar']
            ).execute()
            if response.data:
                return redirect(url_for('bodegas'))
            return "Error borrando registro de inventario", 500
        if (metodo == "post"):
            descripcion = request.form['descripcionCrear']

            response = (

                #Este es el comando para insertar los datos a la base de datos.
                supabase.table("bodegas").insert({"descripcion": descripcion
                        }).execute()
            )
            if response.data:
                flash("Bodega creada exitosamente", "success")
                return redirect(url_for('bodegas'))
            else:
                flash("Error creando bodega", "error")
                return redirect(url_for('bodegas'))
        if (metodo == "put"):
            idBodega = request.form['IdBodegaActualizar']
            descripcion = request.form['descripcionActualizar'] 
            response = (
                
                supabase.table("bodegas").update({"descripcion": descripcion
                        }).eq("id_bodega", idBodega).select("id_bodega").execute()
            )
            if response.data:
                flash("Bodega actualizada exitosamente", "success")
                return redirect(url_for('bodegas'))
            else:
                flash("Error actualizando bodega", "error")
                return redirect(url_for('bodegas'))
        if (metodo == "delete"):
            idABorrar = request.form['idBodegaBorrar']
            response = (
                supabase.table("bodegas").delete()
                .eq("id_bodega", idABorrar)
                .execute()
            )
            if response.data:
                flash("Bodega borrada exitosamente", "success")
                return redirect(url_for('bodegas'))
            else:
                flash("Error borrando bodega", "error")
                return redirect(url_for('bodegas'))
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscarbodegaid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('bodegas.html', datos = response.data)
            else:
                return "No se ha encontrado ninguna bodega con la id buscada"
        if (metodo == "buscarDescripcion"):
            texto = request.form["descripcionBuscar"]
            response = supabase.rpc('buscarbodegadescripcion', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('bodegas.html', datos = response.data)
            else:
                return "No se ha encontrado ninguna bodega con la descrpición buscada"
    else:
        bodegas_response = supabase.table("bodegas").select("*").execute()
        inventario_disponible = True
        try:
            inventario_response = supabase.table("inventario").select("*").execute()
        except APIError as error:
            if "PGRST205" not in str(error):
                raise
            inventario_data = []
            inventario_disponible = False
        else:
            inventario_data = inventario_response.data
        productos_response = supabase.table("productos").select("*").execute()
        tallas_response = supabase.table("tallas").select("*").execute()
        colores_response = supabase.table("colores").select("*").execute()

        return render_template(
            'bodegas.html',
            datos=bodegas_response.data,
            inventario=inventario_data,
            inventario_disponible=inventario_disponible,
            productos=productos_response.data,
            tallas=tallas_response.data,
            colores=colores_response.data
        )

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
                flash("Vendedor creado exitosamente", "success")
                return redirect(url_for('vendedores'))
            else:
                flash("Error creando vendedor", "error")
                return redirect(url_for('vendedores'))
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
                flash("Vendedor actualizado exitosamente", "success")
                return redirect(url_for('vendedores'))
            else:
                flash("Error actualizando vendedor", "error")
                return redirect(url_for('vendedores'))
        if (metodo == "delete"):
            idABorrar = request.form['idVendedorBorrar']
            response = (
                supabase.table("vendedores").delete()
                .eq("id_vendedor", idABorrar)
                .execute()
            )
            if response.data:
                flash("Vendedor borrado exitosamente", "success")
                return redirect(url_for('vendedores'))
            else:
                flash("Error borrando vendedor", "error")
                return redirect(url_for('vendedores'))
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscarvendedorid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('vendedores.html', datos = response.data)
            else:
                return "No se ha encontrado ningún vendedor con la id buscada"
        if (metodo == "buscarNombre"):
            texto = request.form["nombreBuscar"]
            response = supabase.rpc('buscarvendedornombre', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('vendedores.html', datos = response.data)
            else:
                return "No se ha encontrado ningún vendedor con el nombre buscado"
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
                flash("Zona de venta creada exitosamente", "success")
                return redirect(url_for('zonasVenta'))
            else:
                flash("Error creando zona de venta", "error")
                return redirect(url_for('zonasVenta'))
        if (metodo == "put"):
            idZonaVenta = request.form['IdZonaVentaActualizar']
            descripcion = request.form['descripcionActualizar'] 
            response = (
                
                supabase.table("zona_venta").update({"descripcion": descripcion
                        }).eq("id_zona_venta", idZonaVenta).select("id_zona_venta").execute()
            )
            if response.data:
                flash("Zona de venta actualizada exitosamente", "success")
                return redirect(url_for('zonasVenta'))
            else:
                flash("Error actualizando zona de venta", "error")
                return redirect(url_for('zonasVenta'))
        if (metodo == "delete"):
            idABorrar = request.form['idZonaVentaBorrar']
            response = (
                supabase.table("zona_venta").delete()
                .eq("id_zona_venta", idABorrar)
                .execute()
            )
            if response.data:
                flash("Zona de venta borrada exitosamente", "success")
                return redirect(url_for('zonasVenta'))
            else:
                flash("Error borrando zona de venta", "error")
                return redirect(url_for('zonasVenta'))
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscarzonaventaid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('zonasVenta.html', datos = response.data)
            else:
                return "No se ha encontrado ninguna zona de venta con la id buscada"
        if (metodo == "buscarDescripcion"):
            texto = request.form["descripcionBuscar"]
            response = supabase.rpc('buscarzonaventadescripcion', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('zonasVenta.html', datos = response.data)
            else:
                return "No se ha encontrado ninguna zona de venta con la descripción buscada"
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
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscartallaid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('tallas.html', datos = response.data)
            else:
                return "No se ha encontrado ninguna talla con la id buscada"
        if (metodo == "buscarNTalla"):
            texto = request.form["nTallaBuscar"]
            response = supabase.rpc('buscartallanumerotalla', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('tallas.html', datos = response.data)
            else:
                return "No se ha encontrado ninguna talla con el número de talla buscado"
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

            try:
                response = (
                    supabase.table("productos").insert({"abreviacion": abreviacion, "descripcion": descripcion,
                            "color": idColor, "precio": precio, "talla": idTalla
                            }).execute()
                )
            except APIError as error:
                if error.code == "23503":
                    mensaje = "El color o talla seleccionado no existe"
                elif error.code == "22P02":
                    mensaje = "El color o talla seleccionado no es válido"
                else:
                    mensaje = "No se pudo crear el producto"
                flash(mensaje, "error")
                return redirect(url_for('productos'))
            if response.data:
                flash("Producto creado exitosamente", "success")
                return redirect(url_for('productos'))
            else:
                flash("Error creando producto", "error")
                return redirect(url_for('productos'))
        if (metodo == "put"):
            idProducto = request.form['IdProductoActualizar']
            descripcion = request.form['descripcionActualizar']
            abreviacion = request.form['abreviacionActualizar']
            idColor = request.form['idColorActualizar']
            precio = request.form['precioActualizar']
            idTalla = request.form['idTallaActualizar'] 
            try:
                response = (
                    supabase.table("productos").update({"abreviacion": abreviacion, "descripcion": descripcion,
                            "color": idColor, "precio": precio, "talla": idTalla}).eq("id_producto", idProducto).select("id_producto").execute()
                )
            except APIError as error:
                if error.code == "23503":
                    mensaje = "El color o talla seleccionado no existe"
                elif error.code == "22P02":
                    mensaje = "El color o talla seleccionado no es válido"
                else:
                    mensaje = "No se pudo actualizar el producto"
                flash(mensaje, "error")
                return redirect(url_for('productos'))
            if response.data:
                flash("Producto actualizado exitosamente", "success")
                return redirect(url_for('productos'))
            else:
                flash("Error actualizando producto", "error")
                return redirect(url_for('productos'))
        if (metodo == "delete"):
            idABorrar = request.form['idProductoBorrar']
            response = (
                supabase.table("productos").delete()
                .eq("id_producto", idABorrar)
                .execute()
            )
            if response.data:
                flash("Producto borrado exitosamente", "success")
                return redirect(url_for('productos'))
            else:
                flash("Error borrando producto", "error")
                return redirect(url_for('productos'))
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscarproductoid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('productos.html', datos = response.data)
            else:
                return "No se ha encontrado ningún producto con la id buscada"
        if (metodo == "buscarNombre"):
            texto = request.form["nombreBuscar"]
            response = supabase.rpc('buscarproductonombre', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('productos.html', datos = response.data)
            else:
                return "No se ha encontrado ningún producto con el nombre buscado"
        if (metodo == "buscarAbreviacion"):
            texto = request.form["abreviacionBuscar"]
            response = supabase.rpc('buscarproductoabreviacion', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('productos.html', datos = response.data)
            else:
                return "No se ha encontrado ningún producto con la abreviación buscada"
    else:
        response =(
            supabase.table("productos").select("*").execute()
        )
        colores_response = supabase.table("colores").select("*").execute()
        tallas_response = supabase.table("tallas").select("*").execute()
            
        return render_template(
            'productos.html',
            datos=response.data,
            colores=colores_response.data,
            tallas=tallas_response.data
        )

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
        if (metodo == "buscarID"):
            texto = request.form["idBuscar"]
            response = supabase.rpc('buscarcodigoeanid', { 'textobusqueda': texto }).execute()
            if response.data:
                return render_template('codigosEAN.html', datos = response.data)
            else:
                return "No se ha encontrado ningún código EAN con la id buscada"
    else:
        response =(
            supabase.table("codigos_EAN").select("*").execute()
        )
            
        return render_template('codigosEAN.html', datos = response.data)


@app.route('/archivosMaestros.html', methods=['GET'])
def archivosMaestros():
        return render_template('archivosMaestros.html')

@app.route('/configuracion.html', methods=['GET', 'POST'])
def configuracion():
    if request.method == 'GET':
        try:
            parametros = obtener_parametros_sistema()
        except APIError:
            parametros = SYSTEM_PARAMETER_DEFAULTS.copy()
            flash("No se pudo cargar la configuración desde Supabase", "error")
        return render_template('configuracion.html', parametros=parametros)

    campos = {
        "razon_social": request.form.get("razon_social", "").strip(),
        "rut": request.form.get("rut", "").strip(),
        "giro": request.form.get("giro", "").strip(),
        "direccion": request.form.get("direccion", "").strip(),
        "telefono": request.form.get("telefono", "").strip(),
        "correo": request.form.get("correo", "").strip(),
        "moneda": request.form.get("moneda", "").strip().upper(),
        "formato_moneda": request.form.get("formato_moneda", "").strip(),
        "porcentaje_impuesto": request.form.get("porcentaje_impuesto", "").strip()
    }
    monedas_permitidas = {"CLP", "USD", "EUR"}
    rut_valido = re.fullmatch(r"(?:\d{7,8}-[\dkK]|\d{1,2}(?:\.\d{3}){2}-[\dkK])", campos["rut"])
    correo_valido = re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", campos["correo"])

    try:
        impuesto = float(campos["porcentaje_impuesto"])
    except (TypeError, ValueError):
        impuesto = None

    if not campos["razon_social"]:
        flash("La razón social es obligatoria", "error")
        return redirect(url_for('configuracion'))
    if not rut_valido:
        flash("El RUT no tiene un formato válido", "error")
        return redirect(url_for('configuracion'))
    if not correo_valido:
        flash("El correo electrónico no tiene un formato válido", "error")
        return redirect(url_for('configuracion'))
    if campos["moneda"] not in monedas_permitidas:
        flash("Selecciona una moneda válida", "error")
        return redirect(url_for('configuracion'))
    if not campos["formato_moneda"]:
        flash("El formato de moneda es obligatorio", "error")
        return redirect(url_for('configuracion'))
    if impuesto is None or not 0 <= impuesto <= 100:
        flash("El impuesto debe ser un valor entre 0 y 100", "error")
        return redirect(url_for('configuracion'))

    logo = request.files.get("logotipo")
    logo_path = None
    if logo and logo.filename:
        nombre_seguro = secure_filename(logo.filename)
        extension = nombre_seguro.rsplit(".", 1)[-1].lower() if "." in nombre_seguro else ""
        if not nombre_seguro or extension not in ALLOWED_LOGO_EXTENSIONS:
            flash("El archivo de logotipo no está permitido", "error")
            return redirect(url_for('configuracion'))
        logo.stream.seek(0, os.SEEK_END)
        tamano_logo = logo.stream.tell()
        logo.stream.seek(0)
        if tamano_logo > MAX_LOGO_SIZE:
            flash("El logotipo no puede superar los 2 MB", "error")
            return redirect(url_for('configuracion'))
        nombre_logo = f"logo-configurado.{extension}"
        carpeta_logo = os.path.join(app.static_folder, "img")
        os.makedirs(carpeta_logo, exist_ok=True)
        logo.save(os.path.join(carpeta_logo, nombre_logo))
        logo_path = f"img/{nombre_logo}"

    payload = {
        **campos,
        "porcentaje_impuesto": impuesto,
        "fecha_actualizacion": datetime.now(timezone.utc).isoformat(),
        "usuario_actualizacion": os.environ.get("SYSTEM_USER", "Admin")
    }
    if logo_path:
        payload["logotipo"] = logo_path

    try:
        existente = supabase.table("parametros_sistema").select("id").eq("id", 1).execute()
        if existente.data:
            response = (
                supabase.table("parametros_sistema").update(payload)
                .eq("id", 1).select("id").execute()
            )
        else:
            response = supabase.table("parametros_sistema").insert({"id": 1, **payload}).execute()
        if not response.data:
            flash("No se pudo guardar la configuración", "error")
            return redirect(url_for('configuracion'))
    except (APIError, OSError):
        flash("No se pudo guardar la configuración", "error")
        return redirect(url_for('configuracion'))

    flash("Configuración guardada correctamente", "success")
    return redirect(url_for('configuracion'))

@app.route('/notasCredito.html', methods=['GET'])
def notasCredito():
    ordenes_permitidas = {
        "folio": "folio",
        "fecha": "fecha",
        "cliente": "cliente_asociado",
        "factura": "factura_referencia",
        "monto": "monto_total",
        "motivo": "motivo",
        "estado": "estado"
    }
    orden_por = request.args.get("orden_por", "fecha")
    orden_dir = request.args.get("orden_dir", "desc").lower()
    if orden_por not in ordenes_permitidas:
        orden_por = "fecha"
    if orden_dir not in {"asc", "desc"}:
        orden_dir = "desc"

    filtros = {
        "folio": request.args.get("folio", "").strip(),
        "cliente": request.args.get("cliente", "").strip().casefold(),
        "factura_referencia": request.args.get("factura_referencia", "").strip(),
        "fecha_desde": request.args.get("fecha_desde", "").strip(),
        "fecha_hasta": request.args.get("fecha_hasta", "").strip()
    }
    orden_links = {}
    for clave in ordenes_permitidas:
        siguiente_direccion = "asc" if orden_por != clave or orden_dir == "desc" else "desc"
        parametros_orden = {
            **{key: value for key, value in filtros.items() if value},
            "orden_por": clave,
            "orden_dir": siguiente_direccion
        }
        orden_links[clave] = url_for("notasCredito", **parametros_orden)
    try:
        notas_query = supabase.table("notas_credito").select("*")
        notas_query = notas_query.order(
            ordenes_permitidas[orden_por], desc=orden_dir == "desc"
        )
        notas_response = notas_query.execute()
        clientes_response = supabase.table("clientes").select("id_cliente, nombre").execute()
        facturas_response = supabase.table("facturas").select("id_factura, folio").execute()
    except APIError:
        flash("No se pudo cargar el listado de notas de crédito", "error")
        return render_template(
            "notasCredito.html",
            datos=[], filtros=filtros, orden_por=orden_por,
                        orden_dir=orden_dir, orden_links=orden_links,
                        filtro_aplicado=any(filtros.values())
        )

    clientes = {str(item["id_cliente"]): item.get("nombre", "") for item in clientes_response.data}
    facturas = {str(item["id_factura"]): item.get("folio", "") for item in facturas_response.data}
    datos = []
    for nota in notas_response.data:
        cliente_id = str(nota.get("cliente_asociado", ""))
        factura_id = str(nota.get("factura_referencia", ""))
        fila = {
            **nota,
            "cliente_nombre": clientes.get(cliente_id, "Cliente no encontrado"),
            "factura_folio": facturas.get(factura_id, "Factura no encontrada")
        }
        fecha = str(fila.get("fecha", ""))
        if filtros["folio"] and filtros["folio"] not in str(fila.get("folio", "")):
            continue
        if filtros["cliente"] and filtros["cliente"] not in fila["cliente_nombre"].casefold():
            continue
        if filtros["factura_referencia"] and filtros["factura_referencia"] not in str(fila["factura_folio"]):
            continue
        if filtros["fecha_desde"] and fecha < filtros["fecha_desde"]:
            continue
        if filtros["fecha_hasta"] and fecha > filtros["fecha_hasta"]:
            continue
        datos.append(fila)

    claves_orden = {
        "folio": lambda item: item.get("folio", 0),
        "fecha": lambda item: item.get("fecha", ""),
        "cliente": lambda item: item.get("cliente_nombre", "").casefold(),
        "factura": lambda item: item.get("factura_folio", 0),
        "monto": lambda item: float(item.get("monto_total", 0) or 0),
        "motivo": lambda item: item.get("motivo", "").casefold(),
        "estado": lambda item: item.get("estado", "").casefold()
    }
    datos.sort(key=claves_orden[orden_por], reverse=orden_dir == "desc")
    return render_template(
        "notasCredito.html", datos=datos, filtros=filtros,
        orden_por=orden_por, orden_dir=orden_dir,
                orden_links=orden_links,
        filtro_aplicado=any(filtros.values())
    )

@app.route('/ingresoBodega.html', methods=['GET', 'POST'])
def ingresoBodega():
    if request.method == 'GET':
        try:
            bodegas_response = supabase.table("bodegas").select("*").execute()
        except APIError:
            flash("No se pudieron cargar las bodegas disponibles", "error")
            return redirect(url_for('ingresoBodega'))
        return render_template('ingresoBodega.html', bodegas=bodegas_response.data)

    codigo_corte = request.form.get('codigoCorte', '')
    id_bodega = request.form.get('idBodega', '')
    try:
        codigo_corte = int(codigo_corte)
        id_bodega = int(id_bodega)
    except (TypeError, ValueError):
        flash("El código de corte o la bodega seleccionada no es válido", "error")
        return redirect(url_for('ingresoBodega'))

    try:
        corte_response = (
            supabase.table("cortes").select("*")
            .eq("id_corte", codigo_corte).execute()
        )
        if not corte_response.data:
            flash("No se encontró ninguna guía de cortes con ese código", "error")
            return redirect(url_for('ingresoBodega'))

        corte = corte_response.data[0]
        id_producto = int(corte['producto_asociado'])
        cantidad_corte = int(corte['cantidad'])
        producto_response = (
            supabase.table("productos").select("color, talla")
            .eq("id_producto", id_producto).execute()
        )
        if not producto_response.data:
            flash("No se encontró el producto asociado a la guía de cortes", "error")
            return redirect(url_for('ingresoBodega'))

        producto = producto_response.data[0]
        id_color = int(producto['color'])
        id_talla = int(producto['talla'])
        inventario_response = (
            supabase.table("inventario").select("*")
            .eq("id_bodega", id_bodega)
            .eq("id_producto", id_producto)
            .eq("id_talla", id_talla)
            .eq("id_color", id_color)
            .execute()
        )

        if inventario_response.data:
            inventario = inventario_response.data[0]
            nueva_cantidad = int(inventario['cantidad']) + cantidad_corte
            inventario_result = (
                supabase.table("inventario")
                .update({"cantidad": nueva_cantidad})
                .eq("id_inventario", inventario['id_inventario'])
                .select("id_inventario").execute()
            )
        else:
            inventario_result = (
                supabase.table("inventario").insert({
                    "id_bodega": id_bodega,
                    "id_producto": id_producto,
                    "id_talla": id_talla,
                    "id_color": id_color,
                    "cantidad": cantidad_corte
                }).execute()
            )

        if not inventario_result.data:
            flash("No se pudo ingresar el producto a la bodega", "error")
            return redirect(url_for('ingresoBodega'))
    except (APIError, KeyError, TypeError, ValueError):
        flash("No se pudo ingresar la guía de cortes a la bodega", "error")
        return redirect(url_for('ingresoBodega'))

    flash(
        f"Se ingresaron {cantidad_corte} unidades del producto {id_producto} en la bodega {id_bodega}",
        "success"
    )
    return redirect(url_for('ingresoBodega'))

@app.route('/produccion.html', methods=['GET'])      
def produccion():
        return render_template('produccion.html')

@app.route('/', methods=['GET'])
def index():
        return render_template('index.html')

#Esto simplemente lo corre en debug mode
if __name__ == '__main__':
    app.run(debug=True)
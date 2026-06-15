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
                return "Bodega borrada exitosamente"
            else:
                return "Error borrando color", 500
                
    else:
        response =(
            supabase.table("bodegas").select("*").execute()
        )
            
        return render_template('bodegas.html', datos = response.data)

@app.route('/vendedores.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def vendedores():
    if request.method == 'POST':
        rut = request.form['rutCrear']
        nom = request.form['nombreCrear']
        correo = request.form['correoCrear']
        tf = request.form['telefonoCrear']
        digVer = request.form['digVerCrear']
        porComi = request.form['porComisionCrear']

        response = (
            supabase.table("vendedores").insert({"rut": rut, "nombre": nom,
                      "correo": correo, "telefono": tf, 
                      "digito_verificador": digVer,
                      "porcentaje_comision": porComi,
                      }).execute()
        )
        if response.data:
            return "Vendedor creado exitosamente"
        else:
            return "Error creando vendedor", 500
    else:
        return render_template('vendedores.html')

@app.route('/zonasVenta.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def zonasVenta():
    if request.method == 'POST':
        descripcion = request.form['descripcionCrear']

        response = (
            supabase.table("zona_venta").insert({"descripcion": descripcion
                      }).execute()
        )
        if response.data:
            return "Zona de venta creada exitosamente"
        else:
            return "Error creando zona de venta", 500
    else:
        return render_template('zonaVenta.html')

@app.route('/tallas.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def tallas():
    if request.method == 'POST':
        talla = request.form['tallaCrear']

        response = (
            supabase.table("tallas").insert({"talla": talla
                      }).execute()
        )
        if response.data:
            return "Talla creada exitosamente"
        else:
            return "Error creando talla", 500
    else:
        return render_template('tallas.html')

@app.route('/productos.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def productos():
    if request.method == 'POST':
        descripcion = request.form['descripcionCrear']
        abreviacion = request.form['abreviacionCrear']
        listaColores = request.form['listaColoresCrear']
        precioMayor = request.form['precioMayorCrear']
        precioCosto = request.form['precioCostoCrear']
        precioDetalle = request.form['precioDetalle']
        codigoEAN = request.form['codigoEANCrear']
        listaTallas = request.form['listaTallasCrear']

        response = (
            supabase.table("productos").insert({"descripcion": descripcion,
                      "abreviacion": abreviacion,"listaColores": listaColores,
                      "precioMayor": precioMayor, "precioCosto": precioCosto,
                      "precioDetalle": precioDetalle,"codigoEAN": codigoEAN,
                      "listaTallas": listaTallas
                      }).execute()
        )
        if response.data:
            return "Producto creado exitosamente"
        else:
            return "Error creando producto", 500
    else:
        return render_template('productos.html')

@app.route('/codigosEAN.html', methods=['GET', 'POST', 'DELETE', 'PUT'])
def codigosEAN():
    if request.method == 'POST':
        producto = request.form['productoCrear']

        response = (

            #Este es el comando para insertar los datos a la base de datos.
            supabase.table("codigosEAN").insert({"producto": producto
                      }).execute()
        )
        if response.data:
            return "Código creado exitosamente"
        else:
            return "Error creando código", 500
    else:
        return render_template('codigosEAN.html')


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
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
# index.html no hace nada aún

@app.route('/', methods=['GET', 'POST'])
def index():
    #Esta parte se activa cuando recibe una solicitud POST.
    #Ocurre cuando se usa un botón con submit.
    if request.method == 'POST':
        rut = request.form['rut']
        nom = request.form['nombre']
        correo = request.form['correo']
        tf = request.form['telefono']
        direccion = request.form['direccion']
        #activo = request.form['activo']
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
            return "Éxito!"
        else:
            return "Error", 500
    #Esto ocurre por defecto, y simplemente carga cliente.html
    else:
        return render_template('cliente.html')
#Esto simplemente lo corre en debug mode
if __name__ == '__main__':
    app.run(debug=True)
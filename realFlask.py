import os
from flask import Flask
from flask import request
from flask import render_template
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_PUBLISHABLE_KEY")
)

@app.route('/', methods=['GET', 'POST'])
def index():
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
        response = (
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
    else:
        return render_template('cliente.html')
    
if __name__ == '__main__':
    app.run(debug=True)
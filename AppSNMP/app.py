from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import subprocess
import os
# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snmp_data.db'
db = SQLAlchemy(app)

# Modelo de la base de datos para almacenar los datos SNMP
class SNMPData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    memory_physical = db.Column(db.Float)  # Uso de memoria física
    memory_virtual = db.Column(db.Float)   # Uso de memoria virtual

# Configuración y creación de la base de datos en el contexto de la app
with app.app_context():
    db.create_all()  # Crea la tabla si no existe

# Configuración SNMP
SNMP_TARGET = "127.0.0.1"
COMMUNITY_STRING = "interyr3d"
MEMORY_PHYSICAL_OID = ".1.3.6.1.2.1.25.2.3.1.6.3"
MEMORY_TOTAL_PHYSICAL_OID = ".1.3.6.1.2.1.25.2.3.1.5.3"
MEMORY_VIRTUAL_OID = ".1.3.6.1.2.1.25.2.3.1.6.2"
MEMORY_TOTAL_VIRTUAL_OID = ".1.3.6.1.2.1.25.2.3.1.5.2"
SNMPGET_PATH = r"D:\Usuarios\alexanderarciniegas\Downloads\SnmpGet\SnmpGet.exe"  # Ruta completa al archivo snmpget.exe

# Función para realizar la consulta SNMP usando snmpget
def get_snmp_data_with_snmpget(oid):
    """
    Realiza una consulta SNMP usando el comando snmpget.
    """
    # Verificar si snmpget.exe existe en la ruta especificada
    if not os.path.exists(SNMPGET_PATH):
        print(f"El archivo {SNMPGET_PATH} no se encuentra.")
        return None

    # Construir el comando snmpget con los parámetros correctos
    command = [
        SNMPGET_PATH,  # Ruta completa al snmpget.exe
        "-r:" + SNMP_TARGET,  # Dirección IP del objetivo (con el parámetro '-r:')
        "-v:2c",  # Versión SNMP (2c)
        "-c:" + COMMUNITY_STRING,  # Cadena de comunidad
        "-o:" + oid  # OID a consultar
    ]
    
    try:
        # Ejecutar el comando snmpget y obtener la salida
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Mostrar la salida completa para depuración
        print("Comando ejecutado:", " ".join(command))
        print("Salida estándar:", result.stdout)
        print("Salida de error:", result.stderr)
        
        if result.returncode == 0:
            # Procesar la salida buscando el valor después del "="
            lines = result.stdout.splitlines()
            for line in lines:
                if "Value=" in line:  # Asegurarse de que la línea contiene el valor
                    value = line.split("Value=")[1].strip()  # Obtener el valor después de "Value="
                    return value
        else:
            print(f"Error ejecutando snmpget: {result.stderr}")
            return None

    except Exception as e:
        print(f"Excepción en snmpget: {e}")
        return None

# Ruta principal de la aplicación
@app.route("/")
def index():
    print("Obteniendo datos SNMP...")  # Indicar que estamos comenzando a obtener datos
    
    # Obtener valores de memoria física y virtual
    memory_physical_used = get_snmp_data_with_snmpget(MEMORY_PHYSICAL_OID)
    memory_physical_total = get_snmp_data_with_snmpget(MEMORY_TOTAL_PHYSICAL_OID)
    memory_virtual_used = get_snmp_data_with_snmpget(MEMORY_VIRTUAL_OID)
    memory_virtual_total = get_snmp_data_with_snmpget(MEMORY_TOTAL_VIRTUAL_OID)

    # Mostrar los valores obtenidos antes de calcular
    print(f"memory_physical_used: {memory_physical_used}")
    print(f"memory_physical_total: {memory_physical_total}")
    print(f"memory_virtual_used: {memory_virtual_used}")
    print(f"memory_virtual_total: {memory_virtual_total}")

    # Calcular uso de memoria física y virtual en porcentaje
    memory_physical = (float(memory_physical_used) / float(memory_physical_total)) * 100 if memory_physical_total else None
    memory_virtual = (float(memory_virtual_used) / float(memory_virtual_total)) * 100 if memory_virtual_total else None

    # Mostrar los valores calculados
    print(f"Uso de memoria física: {memory_physical}%")
    print(f"Uso de memoria virtual: {memory_virtual}%")

    # Guardar los valores en la base de datos solo si todos los valores son válidos
    if memory_physical is not None and memory_virtual is not None:
        print("Guardando datos en la base de datos...")
        snmp_data = SNMPData(memory_physical=memory_physical, memory_virtual=memory_virtual)
        db.session.add(snmp_data)
        db.session.commit()
        print("Datos guardados correctamente.")

    # Consulta los últimos 3 días de datos para graficar
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    data = SNMPData.query.filter(SNMPData.timestamp >= three_days_ago).all()

    # Si no hay datos, enviar un mensaje
    if not data:
        print("No hay datos en la base de datos para mostrar.")
        return render_template(
            "index.html",
            message="No se pudieron obtener datos SNMP.",
            timestamps=[],
            memory_physical_values=[],
            memory_virtual_values=[]
        )

    # Extrae los datos para graficar
    timestamps = [d.timestamp for d in data]
    memory_physical_values = [d.memory_physical for d in data]
    memory_virtual_values = [d.memory_virtual for d in data]

    print(f"Tiempos registrados: {timestamps}")
    print(f"Valores de memoria física: {memory_physical_values}")
    print(f"Valores de memoria virtual: {memory_virtual_values}")

    return render_template(
        "index.html",
        timestamps=timestamps,
        memory_physical_values=memory_physical_values,
        memory_virtual_values=memory_virtual_values
    )

if __name__ == "__main__":
    app.run(debug=True)

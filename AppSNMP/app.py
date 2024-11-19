from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from pytz import timezone
import subprocess
import os

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snmp_data.db'
db = SQLAlchemy(app)

# Modelo de la base de datos para almacenar los datos SNMP
class SNMPData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone("America/Bogota"))
    )
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
    if not os.path.exists(SNMPGET_PATH):
        print(f"El archivo {SNMPGET_PATH} no se encuentra.")
        return None

    command = [
        SNMPGET_PATH,
        "-r:" + SNMP_TARGET,
        "-v:2c",
        "-c:" + COMMUNITY_STRING,
        "-o:" + oid
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            for line in lines:
                if "Value=" in line:
                    value = line.split("Value=")[1].strip()
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
    # Obtener valores de memoria física y virtual
    memory_physical_used = get_snmp_data_with_snmpget(MEMORY_PHYSICAL_OID)
    memory_physical_total = get_snmp_data_with_snmpget(MEMORY_TOTAL_PHYSICAL_OID)
    memory_virtual_used = get_snmp_data_with_snmpget(MEMORY_VIRTUAL_OID)
    memory_virtual_total = get_snmp_data_with_snmpget(MEMORY_TOTAL_VIRTUAL_OID)

    # Calcular uso de memoria física y virtual en porcentaje
    memory_physical = (float(memory_physical_used) / float(memory_physical_total)) * 100 if memory_physical_total else None
    memory_virtual = (float(memory_virtual_used) / float(memory_virtual_total)) * 100 if memory_virtual_total else None

    # Guardar los valores en la base de datos si son válidos
    if memory_physical is not None and memory_virtual is not None:
        snmp_data = SNMPData(
            timestamp=datetime.now(timezone("America/Bogota")),
            memory_physical=memory_physical,
            memory_virtual=memory_virtual
        )
        db.session.add(snmp_data)
        db.session.commit()

    # Consulta los últimos 3 días de datos para graficar
    three_days_ago = datetime.now(timezone("America/Bogota")) - timedelta(days=3)
    data = SNMPData.query.filter(SNMPData.timestamp >= three_days_ago).all()

    # Preparar datos para el gráfico
    timestamps = [d.timestamp.isoformat() for d in data]
    memory_physical_values = [d.memory_physical for d in data]
    memory_virtual_values = [d.memory_virtual for d in data]

    return render_template(
        "index.html",
        timestamps=timestamps,
        memory_physical_values=memory_physical_values,
        memory_virtual_values=memory_virtual_values
    )

if __name__ == "__main__":
    app.run(debug=True)

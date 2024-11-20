import subprocess
import os

# Configuración SNMP
SNMP_TARGET = ["127.0.0.1", "192.168.56.101"]
COMMUNITY_STRING = "interyr3d"
MEMORY_PHYSICAL_OID = ".1.3.6.1.2.1.25.2.3.1.6.3"
SNMPGET_PATH = r"C:\Users\Ordon\Downloads\SnmpGet\SnmpGet.exe"  # Ruta completa al archivo snmpget.exe

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

# Función principal para ejecutar la consulta
def main():
    print("Iniciando consulta SNMP...")

    # Obtener datos de memoria
    memory_physical_used = get_snmp_data_with_snmpget(MEMORY_PHYSICAL_OID)

    if memory_physical_used is not None:
        print(f"Valor de memoria física usada: {memory_physical_used}")
    else:
        print("No se pudo obtener el valor de memoria física.")

if __name__ == "__main__":
    main()

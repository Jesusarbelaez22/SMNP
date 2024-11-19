import sqlite3
import os

# Ruta al archivo de base de datos
DB_PATH = "instance/snmp_data.db"  # Ajusta esta ruta si es necesario

def reset_database():
    print(f"Ruta de la base de datos: {DB_PATH}")
    
    # Verificar si la base de datos existe y eliminarla
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Base de datos eliminada: {DB_PATH}")
    else:
        print(f"No se encontró la base de datos en {DB_PATH}. Se creará una nueva.")

    # Crear una nueva base de datos y establecer la conexión
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear las tablas necesarias
    cursor.execute('''
    CREATE TABLE snmp_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        memory_physical REAL NOT NULL,
        memory_virtual REAL NOT NULL
    )
    ''')
    print("Tabla 'snmp_data' creada con éxito.")

    conn.commit()
    conn.close()
    print("Base de datos reiniciada con éxito.")

if __name__ == "__main__":
    reset_database()

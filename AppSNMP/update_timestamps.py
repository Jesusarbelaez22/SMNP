from app import db, SNMPData  # Importar la base de datos y el modelo
from pytz import timezone, utc  # Importar zonas horarias y UTC
from datetime import datetime

# Zona horaria de Bogotá
bogota_tz = timezone("America/Bogota")

def update_timestamps_to_bogota():
    """
    Actualiza todos los timestamps existentes en la base de datos a la hora de Bogotá.
    """
    with db.session.begin():  # Manejo de transacciones en SQLAlchemy
        for record in SNMPData.query.all():
            if record.timestamp:
                # Convertir de UTC a Bogotá y remover información de zona horaria para almacenar en la base
                record.timestamp = record.timestamp.replace(tzinfo=utc).astimezone(bogota_tz).replace(tzinfo=None)
        db.session.commit()  # Guardar cambios en la base de datos
    print("Timestamps actualizados a la hora de Bogotá.")

# Función principal
if __name__ == "__main__":
    print("Iniciando actualización de timestamps...")
    update_timestamps_to_bogota()
    print("¡Actualización completada!")
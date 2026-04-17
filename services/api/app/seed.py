from datetime import timedelta

from sqlmodel import Session, select

from .db import engine
from .models import Alert, Charge, Reactor, Sensor, SensorValue, Task, WikiPage, _utcnow


def seed_data() -> bool:
    with Session(engine) as session:
        has_charge = session.exec(select(Charge)).first()
        has_sensor = session.exec(select(Sensor)).first()
        reactor = session.exec(select(Reactor)).first()
        seeded_any = False

        if reactor is None:
            reactor = Reactor(
                name='Reaktor-A1',
                reactor_type='mobil',
                status='online',
                volume_l=1.6,
                location='Regal A',
                notes='Seed-Reaktor fuer lokale Entwicklung',
            )
            session.add(reactor)
            session.commit()
            session.refresh(reactor)
            seeded_any = True

        if has_charge is None:
            session.add(Charge(name='Charge-001', species='Chlorella vulgaris', status='active', volume_l=1.4, reactor_id=reactor.id))
            session.add(Task(title='Probe entnehmen', status='open'))
            session.add(Alert(level='warning', message='pH-Kalibrierung in 2 Tagen fällig', status='open'))
            session.add(WikiPage(slug='howto/erste-charge', title='Erste Charge anlegen', summary='Kurzanleitung für die erste Charge'))
            session.add(WikiPage(slug='sop/reinigung-reaktor', title='SOP Reaktor reinigen', summary='Reinigungsschritte für mobile Reaktoren'))
            session.commit()
            seeded_any = True

        if has_sensor is None:
            now = _utcnow()
            temp_sensor = Sensor(
                name='Mediumtemperatur A1',
                sensor_type='water_temperature',
                unit='°C',
                status='active',
                reactor_id=reactor.id,
                location='Reaktor-A1',
                notes='Seed-Sensor fuer Temperaturverlauf',
            )
            ph_sensor = Sensor(
                name='pH Sonde A1',
                sensor_type='ph',
                unit='pH',
                status='active',
                reactor_id=reactor.id,
                location='Reaktor-A1',
            )
            room_sensor = Sensor(
                name='Raumfeuchte Nordregal',
                sensor_type='humidity',
                unit='%RH',
                status='error',
                location='Nordregal',
                notes='Zeigt einen Kommunikationsfehler fuer Dashboard-Demos',
            )
            session.add(temp_sensor)
            session.add(ph_sensor)
            session.add(room_sensor)
            session.commit()
            session.refresh(temp_sensor)
            session.refresh(ph_sensor)
            session.refresh(room_sensor)

            session.add(
                SensorValue(
                    sensor_id=temp_sensor.id,
                    value=23.4,
                    source='seed',
                    recorded_at=now - timedelta(minutes=30),
                )
            )
            session.add(
                SensorValue(
                    sensor_id=temp_sensor.id,
                    value=23.8,
                    source='seed',
                    recorded_at=now - timedelta(minutes=10),
                )
            )
            session.add(
                SensorValue(
                    sensor_id=ph_sensor.id,
                    value=7.1,
                    source='seed',
                    recorded_at=now - timedelta(minutes=20),
                )
            )
            session.add(
                SensorValue(
                    sensor_id=ph_sensor.id,
                    value=6.9,
                    source='seed',
                    recorded_at=now - timedelta(minutes=5),
                )
            )
            session.add(
                SensorValue(
                    sensor_id=room_sensor.id,
                    value=58.0,
                    source='seed',
                    recorded_at=now - timedelta(hours=2),
                )
            )
            session.commit()
            seeded_any = True

        return seeded_any


if __name__ == '__main__':
    seed_data()

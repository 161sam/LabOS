from datetime import timedelta

from sqlmodel import Session, select

from .db import engine
from .models import Alert, Charge, Reactor, Sensor, SensorValue, Task, WikiPage, _utcnow


def seed_data() -> bool:
    with Session(engine) as session:
        has_charge = session.exec(select(Charge)).first()
        has_sensor = session.exec(select(Sensor)).first()
        reactor = session.exec(select(Reactor)).first()
        charge = session.exec(select(Charge)).first()
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
            session.add(WikiPage(slug='howto/erste-charge', title='Erste Charge anlegen', summary='Kurzanleitung für die erste Charge'))
            session.add(WikiPage(slug='sop/reinigung-reaktor', title='SOP Reaktor reinigen', summary='Reinigungsschritte für mobile Reaktoren'))
            session.commit()
            seeded_any = True
            charge = session.exec(select(Charge)).first()

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

        now = _utcnow()

        if charge is None:
            charge = session.exec(select(Charge)).first()

        if session.exec(select(Task).where(Task.title == 'Reinigung Reaktor A')).first() is None:
            session.add(
                Task(
                    title='Reinigung Reaktor A',
                    description='Reaktor-A1 nach dem letzten Lauf reinigen und dokumentieren.',
                    status='open',
                    priority='high',
                    due_at=now + timedelta(hours=6),
                    reactor_id=reactor.id if reactor else None,
                )
            )
            seeded_any = True

        if session.exec(select(Task).where(Task.title == 'Probe Charge X')).first() is None:
            session.add(
                Task(
                    title='Probe Charge X',
                    description='Probe der aktiven Charge fuer pH- und Mikroskopie-Check entnehmen.',
                    status='doing',
                    priority='normal',
                    due_at=now + timedelta(hours=2),
                    charge_id=charge.id if charge else None,
                    reactor_id=reactor.id if reactor else None,
                )
            )
            seeded_any = True

        if session.exec(select(Alert).where(Alert.title == 'Sensor ohne Werte Warnung')).first() is None:
            sensor_without_recent_value = session.exec(
                select(Sensor).where(Sensor.name == 'Raumfeuchte Nordregal')
            ).first()
            session.add(
                Alert(
                    title='Sensor ohne Werte Warnung',
                    message='Der Sensor Raumfeuchte Nordregal hat seit laengerer Zeit keinen aktuellen Wert geliefert.',
                    severity='warning',
                    status='open',
                    source_type='sensor',
                    source_id=sensor_without_recent_value.id if sensor_without_recent_value else None,
                )
            )
            seeded_any = True

        if session.exec(select(Alert).where(Alert.title == 'Temperatur Warnung')).first() is None:
            temp_sensor = session.exec(select(Sensor).where(Sensor.name == 'Mediumtemperatur A1')).first()
            session.add(
                Alert(
                    title='Temperatur Warnung',
                    message='Die Mediumtemperatur in Reaktor-A1 liegt ueber dem Sollbereich.',
                    severity='high',
                    status='open',
                    source_type='sensor',
                    source_id=temp_sensor.id if temp_sensor else None,
                )
            )
            seeded_any = True

        if seeded_any:
            session.commit()

        return seeded_any


if __name__ == '__main__':
    seed_data()

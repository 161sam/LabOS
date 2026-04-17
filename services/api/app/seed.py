from datetime import timedelta

from sqlmodel import Session, select

from .db import engine
from .models import Asset, Alert, Charge, Reactor, Rule, Sensor, SensorValue, Task, WikiPage, _utcnow


def seed_data() -> bool:
    with Session(engine) as session:
        has_charge = session.exec(select(Charge)).first()
        has_sensor = session.exec(select(Sensor)).first()
        has_asset = session.exec(select(Asset)).first()
        reactor = session.exec(select(Reactor)).first()
        charge = session.exec(select(Charge)).first()
        seeded_any = False
        now = _utcnow()

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

        if has_asset is None:
            assets = [
                Asset(
                    name='Prusa MK4',
                    asset_type='printer_3d',
                    category='MakerOps',
                    status='active',
                    location='Werkbank 1',
                    zone='Maker Corner',
                    manufacturer='Prusa',
                    model='MK4',
                    serial_number='MK4-ESL-001',
                    notes='Primärer 3D-Drucker für Gehäuse, Halterungen und Prototypen.',
                    maintenance_notes='Düse monatlich prüfen und Filamentpfad reinigen.',
                    last_maintenance_at=now - timedelta(days=12),
                    next_maintenance_at=now + timedelta(days=18),
                    wiki_ref='Lab-Projekte/Labor-Geraete/3D-Druck/Prusa-MK4',
                ),
                Asset(
                    name='Mikroskop Nordbank',
                    asset_type='microscope',
                    category='BioOps',
                    status='maintenance',
                    location='Laborbank Nord',
                    zone='Wet Lab',
                    manufacturer='Motic',
                    model='BA310',
                    maintenance_notes='Kalibrierung der Optik und Reinigung der Objektive offen.',
                    last_maintenance_at=now - timedelta(days=90),
                    next_maintenance_at=now + timedelta(days=4),
                    wiki_ref='Lab-Projekte/Labor-Geraete/Mikroskopie/Mikroskop-Nordbank',
                ),
                Asset(
                    name='Lötstation TS100 Bench',
                    asset_type='soldering_station',
                    category='MakerOps',
                    status='active',
                    location='Elektronikplatz',
                    zone='Maker Corner',
                    manufacturer='Miniware',
                    model='TS100',
                    next_maintenance_at=now + timedelta(days=45),
                ),
                Asset(
                    name='Server1',
                    asset_type='server',
                    category='ITOps',
                    status='active',
                    location='Rack A',
                    zone='Infra',
                    manufacturer='Supermicro',
                    model='Storage Node',
                    notes='Lokaler LabOS und Storage Host fuer Entwicklungs-Workloads.',
                    next_maintenance_at=now + timedelta(days=30),
                    wiki_ref='Lab-Projekte/Infra/Server1',
                ),
                Asset(
                    name='RTX3060 Node',
                    asset_type='gpu_node',
                    category='AI Assistenz',
                    status='error',
                    location='Rack A',
                    zone='Infra',
                    manufacturer='Custom',
                    model='RTX3060 Edge',
                    notes='Zeigt aktuell einen instabilen Lüfter an.',
                    maintenance_notes='Lüfter und Staubfilter prüfen.',
                    next_maintenance_at=now + timedelta(days=2),
                ),
                Asset(
                    name='Odroid N2+',
                    asset_type='sbc',
                    category='Automation',
                    status='active',
                    location='Regal Süd',
                    zone='Infra',
                    manufacturer='Hardkernel',
                    model='N2+',
                    wiki_ref='Lab-Projekte/Automation/Odroid-N2-Edge',
                ),
                Asset(
                    name='Pumpe A',
                    asset_type='pump',
                    category='BioOps',
                    status='active',
                    location='Fluidik Rack',
                    zone='Wet Lab',
                    maintenance_notes='Schlauchwechsel alle 60 Tage dokumentieren.',
                    next_maintenance_at=now + timedelta(days=9),
                ),
                Asset(
                    name='Netzteil Labor',
                    asset_type='power_supply',
                    category='MakerOps',
                    status='inactive',
                    location='Elektronikplatz',
                    zone='Maker Corner',
                    manufacturer='Rigol',
                    model='DP832',
                ),
            ]
            session.add_all(assets)
            session.commit()
            seeded_any = True

        printer_asset = session.exec(select(Asset).where(Asset.name == 'Prusa MK4')).first()
        microscope_asset = session.exec(select(Asset).where(Asset.name == 'Mikroskop Nordbank')).first()

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

        if session.exec(select(Task).where(Task.title == '3D Drucker Duesencheck')).first() is None:
            session.add(
                Task(
                    title='3D Drucker Duesencheck',
                    description='Prusa MK4 reinigen, Duesenbild pruefen und Wartung dokumentieren.',
                    status='open',
                    priority='normal',
                    due_at=now + timedelta(days=2),
                    asset_id=printer_asset.id if printer_asset else None,
                )
            )
            seeded_any = True

        if session.exec(select(Task).where(Task.title == 'Mikroskop Kalibrierung abschliessen')).first() is None:
            session.add(
                Task(
                    title='Mikroskop Kalibrierung abschliessen',
                    description='Optik pruefen und Maintenance-Notizen fuer das Mikroskop Nordbank aktualisieren.',
                    status='doing',
                    priority='high',
                    due_at=now + timedelta(days=1),
                    asset_id=microscope_asset.id if microscope_asset else None,
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

        temp_sensor = session.exec(select(Sensor).where(Sensor.name == 'Mediumtemperatur A1')).first()
        ph_sensor = session.exec(select(Sensor).where(Sensor.name == 'pH Sonde A1')).first()

        if session.exec(select(Rule).where(Rule.name == 'Temperatur zu hoch -> Alert')).first() is None and temp_sensor is not None:
            session.add(
                Rule(
                    name='Temperatur zu hoch -> Alert',
                    description='Erzeugt einen Alert, wenn die Mediumtemperatur ueber dem Grenzwert liegt.',
                    is_enabled=True,
                    trigger_type='sensor_threshold',
                    condition_type='threshold_gt',
                    condition_config={'sensor_id': temp_sensor.id, 'threshold': 23.5},
                    action_type='create_alert',
                    action_config={
                        'title_template': 'Automationsregel: {sensor_name} zu hoch',
                        'message_template': 'Sensor {sensor_name} meldet {value} {unit} und liegt damit ueber {threshold} {unit}.',
                        'severity': 'high',
                        'source_type': 'sensor',
                    },
                )
            )
            seeded_any = True

        if session.exec(select(Rule).where(Rule.name == 'pH zu niedrig -> Task')).first() is None and ph_sensor is not None:
            session.add(
                Rule(
                    name='pH zu niedrig -> Task',
                    description='Erzeugt eine Aufgabe, wenn der pH-Wert unter den Grenzwert faellt.',
                    is_enabled=True,
                    trigger_type='sensor_threshold',
                    condition_type='threshold_lt',
                    condition_config={'sensor_id': ph_sensor.id, 'threshold': 7.0},
                    action_type='create_task',
                    action_config={
                        'title_template': 'Automationsregel: {sensor_name} pruefen',
                        'description_template': 'Der Sensor {sensor_name} meldet {value} {unit} und liegt unter {threshold} {unit}. Bitte Charge und Reaktor pruefen.',
                        'priority': 'high',
                        'reactor_id': '{reactor_id}',
                        'due_in_hours': 4,
                    },
                )
            )
            seeded_any = True

        if session.exec(select(Rule).where(Rule.name == 'Sensor ohne Werte 24h -> Alert')).first() is None:
            session.add(
                Rule(
                    name='Sensor ohne Werte 24h -> Alert',
                    description='Erzeugt einen Alert, wenn ein Sensor seit mehr als 24 Stunden keine Werte geliefert hat.',
                    is_enabled=True,
                    trigger_type='stale_sensor',
                    condition_type='age_gt_hours',
                    condition_config={'hours': 24},
                    action_type='create_alert',
                    action_config={
                        'title_template': 'Automationsregel: Sensor stale',
                        'message_template': 'Sensor {sensor_name} hat seit mehr als {hours} Stunden keine aktuellen Werte geliefert.',
                        'severity': 'warning',
                        'source_type': 'sensor',
                    },
                )
            )
            seeded_any = True

        if session.exec(select(Rule).where(Rule.name == 'Ueberfaellige Tasks -> Alert')).first() is None:
            session.add(
                Rule(
                    name='Ueberfaellige Tasks -> Alert',
                    description='Erzeugt einen Alert, wenn ueberfaellige Aufgaben vorhanden sind.',
                    is_enabled=True,
                    trigger_type='overdue_tasks',
                    condition_type='count_gt',
                    condition_config={'count': 0, 'overdue_by_hours': 0},
                    action_type='create_alert',
                    action_config={
                        'title_template': 'Automationsregel: Ueberfaellige Aufgaben',
                        'message_template': 'Es gibt {count} ueberfaellige Aufgaben. Aelteste Aufgabe: {oldest_task_title}.',
                        'severity': 'warning',
                        'source_type': 'system',
                    },
                )
            )
            seeded_any = True

        if seeded_any:
            session.commit()

        return seeded_any


if __name__ == '__main__':
    seed_data()

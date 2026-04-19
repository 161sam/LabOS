from datetime import timedelta

from sqlmodel import Session, select

from .config import settings
from .db import engine
from .models import (
    Asset,
    Alert,
    CalibrationRecord,
    Charge,
    DeviceNode,
    InventoryItem,
    Label,
    MaintenanceRecord,
    Reactor,
    ReactorCommand,
    ReactorEvent,
    ReactorSetpoint,
    ReactorTwin,
    Rule,
    SafetyIncident,
    Sensor,
    SensorValue,
    Task,
    TelemetryValue,
    UserAccount,
    WikiPage,
    _utcnow,
)
from .security import hash_password


def seed_data() -> bool:
    with Session(engine) as session:
        has_charge = session.exec(select(Charge)).first()
        has_sensor = session.exec(select(Sensor)).first()
        has_telemetry_value = session.exec(select(TelemetryValue)).first()
        has_device_node = session.exec(select(DeviceNode)).first()
        has_reactor_setpoint = session.exec(select(ReactorSetpoint)).first()
        has_reactor_command = session.exec(select(ReactorCommand)).first()
        has_asset = session.exec(select(Asset)).first()
        has_inventory_item = session.exec(select(InventoryItem)).first()
        has_label = session.exec(select(Label)).first()
        has_user = session.exec(select(UserAccount)).first()
        reactor = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-A1')).first()
        charge = session.exec(select(Charge)).first()
        seeded_any = False
        now = _utcnow()

        if reactor is None:
            reactors = [
                Reactor(
                    name='Reaktor-A1',
                    reactor_type='mobil',
                    status='online',
                    volume_l=1.6,
                    location='Regal A',
                    notes='Seed-Reaktor fuer lokale Entwicklung und Spirulina-Wachstum.',
                ),
                Reactor(
                    name='Reaktor-B1',
                    reactor_type='tower',
                    status='online',
                    volume_l=3.2,
                    location='Nordbank',
                    notes='Testreaktor fuer Stabilisierung und Mediumwechsel.',
                ),
                Reactor(
                    name='Reaktor-C1',
                    reactor_type='panel',
                    status='maintenance',
                    volume_l=2.4,
                    location='Service Bay',
                    notes='Reaktor mit technischem Warning-/Maintenance-Szenario fuer ReactorOps V1.',
                ),
            ]
            session.add_all(reactors)
            session.commit()
            seeded_any = True

        reactor = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-A1')).first()
        reactor_b = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-B1')).first()
        reactor_c = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-C1')).first()

        if reactor_b is None:
            reactor_b = Reactor(
                name='Reaktor-B1',
                reactor_type='tower',
                status='online',
                volume_l=3.2,
                location='Nordbank',
                notes='Testreaktor fuer Stabilisierung und Mediumwechsel.',
            )
            session.add(reactor_b)
            session.commit()
            session.refresh(reactor_b)
            seeded_any = True

        if reactor_c is None:
            reactor_c = Reactor(
                name='Reaktor-C1',
                reactor_type='panel',
                status='maintenance',
                volume_l=2.4,
                location='Service Bay',
                notes='Reaktor mit technischem Warning-/Maintenance-Szenario fuer ReactorOps V1.',
            )
            session.add(reactor_c)
            session.commit()
            session.refresh(reactor_c)
            seeded_any = True

        if has_charge is None:
            session.add(Charge(name='Charge-001', species='Chlorella vulgaris', status='active', volume_l=1.4, reactor_id=reactor.id))
            session.add(WikiPage(slug='howto/erste-charge', title='Erste Charge anlegen', summary='Kurzanleitung für die erste Charge'))
            session.add(WikiPage(slug='sop/reinigung-reaktor', title='SOP Reaktor reinigen', summary='Reinigungsschritte für mobile Reaktoren'))
            session.commit()
            seeded_any = True
            charge = session.exec(select(Charge)).first()

        if has_user is None:
            session.add(
                UserAccount(
                    username=settings.bootstrap_admin_username.strip().lower(),
                    display_name=settings.bootstrap_admin_display_name,
                    email=settings.bootstrap_admin_email,
                    password_hash=hash_password(settings.bootstrap_admin_password),
                    role='admin',
                    is_active=True,
                    auth_source='local',
                    note='Bootstrap admin user generated for local LabOS access.',
                )
            )
            session.commit()
            seeded_any = True

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

        if has_telemetry_value is None:
            telemetry_values = [
                TelemetryValue(
                    reactor_id=reactor.id,
                    sensor_type='temp',
                    value=31.2,
                    unit='degC',
                    source='device',
                    timestamp=now - timedelta(minutes=14),
                ),
                TelemetryValue(
                    reactor_id=reactor.id,
                    sensor_type='ph',
                    value=9.1,
                    unit='pH',
                    source='device',
                    timestamp=now - timedelta(minutes=11),
                ),
                TelemetryValue(
                    reactor_id=reactor.id,
                    sensor_type='light',
                    value=268.0,
                    unit='umol',
                    source='simulated',
                    timestamp=now - timedelta(minutes=9),
                ),
                TelemetryValue(
                    reactor_id=reactor_b.id,
                    sensor_type='temp',
                    value=25.8,
                    unit='degC',
                    source='device',
                    timestamp=now - timedelta(minutes=18),
                ),
                TelemetryValue(
                    reactor_id=reactor_b.id,
                    sensor_type='ph',
                    value=7.2,
                    unit='pH',
                    source='device',
                    timestamp=now - timedelta(minutes=16),
                ),
                TelemetryValue(
                    reactor_id=reactor_c.id,
                    sensor_type='flow',
                    value=0.0,
                    unit='l/min',
                    source='manual',
                    timestamp=now - timedelta(hours=1, minutes=5),
                ),
            ]
            session.add_all(telemetry_values)
            session.commit()
            seeded_any = True

        if has_device_node is None:
            device_nodes = [
                DeviceNode(
                    name='ESP32-A1 Sensor Bridge',
                    node_id='esp32-a1',
                    node_type='sensor_bridge',
                    status='online',
                    last_seen_at=now - timedelta(minutes=2),
                    firmware_version='v0.3.1',
                    reactor_id=reactor.id,
                ),
                DeviceNode(
                    name='ESP32-B1 Env Control',
                    node_id='esp32-b1',
                    node_type='env_control',
                    status='warning',
                    last_seen_at=now - timedelta(minutes=7),
                    firmware_version='v0.2.8',
                    reactor_id=reactor_b.id,
                ),
                DeviceNode(
                    name='ESP32-C1 Pump Driver',
                    node_id='esp32-c1',
                    node_type='pump_driver',
                    status='offline',
                    last_seen_at=now - timedelta(hours=3),
                    firmware_version='v0.2.4',
                    reactor_id=reactor_c.id,
                ),
            ]
            session.add_all(device_nodes)
            session.commit()
            seeded_any = True

        if has_reactor_setpoint is None:
            setpoints = [
                ReactorSetpoint(reactor_id=reactor.id, parameter='temp', target_value=32.0, min_value=30.0, max_value=34.0, mode='auto'),
                ReactorSetpoint(reactor_id=reactor.id, parameter='ph', target_value=9.2, min_value=8.8, max_value=9.6, mode='manual'),
                ReactorSetpoint(reactor_id=reactor.id, parameter='light', target_value=280.0, min_value=220.0, max_value=320.0, mode='auto'),
                ReactorSetpoint(reactor_id=reactor_b.id, parameter='temp', target_value=26.0, min_value=24.0, max_value=27.0, mode='manual'),
                ReactorSetpoint(reactor_id=reactor_b.id, parameter='ph', target_value=7.1, min_value=6.8, max_value=7.4, mode='manual'),
                ReactorSetpoint(reactor_id=reactor_c.id, parameter='flow', target_value=0.0, min_value=0.0, max_value=0.2, mode='manual'),
            ]
            session.add_all(setpoints)
            session.commit()
            seeded_any = True

        if has_reactor_command is None:
            session.add(
                ReactorCommand(
                    reactor_id=reactor.id,
                    command_type='sample_capture',
                    status='pending',
                )
            )
            session.commit()
            seeded_any = True

        reactor_twin_payloads = [
            (
                reactor.id,
                ReactorTwin(
                    reactor_id=reactor.id,
                    culture_type='Spirulina platensis',
                    strain='SP-Blue-01',
                    medium_recipe='Medium A / alkalisch',
                    inoculated_at=now - timedelta(days=6),
                    current_phase='growth',
                    target_ph_min=8.8,
                    target_ph_max=9.6,
                    target_temp_min=30.0,
                    target_temp_max=34.0,
                    target_light_min=220.0,
                    target_light_max=320.0,
                    target_flow_min=0.8,
                    target_flow_max=1.4,
                    expected_harvest_window_start=now + timedelta(days=2),
                    expected_harvest_window_end=now + timedelta(days=4),
                    technical_state='nominal',
                    biological_state='growing',
                    notes='Primärer Spirulina-Lauf mit stabilen Wachstumswerten.',
                ),
            ),
            (
                reactor_b.id,
                ReactorTwin(
                    reactor_id=reactor_b.id,
                    culture_type='Testkultur',
                    strain='TS-042',
                    medium_recipe='Medium B / low nitrogen',
                    inoculated_at=now - timedelta(days=3),
                    current_phase='stabilization',
                    target_ph_min=6.8,
                    target_ph_max=7.4,
                    target_temp_min=24.0,
                    target_temp_max=27.0,
                    target_light_min=120.0,
                    target_light_max=180.0,
                    target_flow_min=0.5,
                    target_flow_max=0.9,
                    expected_harvest_window_start=now + timedelta(days=5),
                    expected_harvest_window_end=now + timedelta(days=7),
                    technical_state='warning',
                    biological_state='adapting',
                    notes='Stabilisierungsphase nach Mediumwechsel und Prozessbeobachtung.',
                ),
            ),
            (
                reactor_c.id,
                ReactorTwin(
                    reactor_id=reactor_c.id,
                    culture_type='Reinigungszyklus',
                    strain=None,
                    medium_recipe='n/a',
                    inoculated_at=None,
                    current_phase='maintenance',
                    target_temp_min=20.0,
                    target_temp_max=25.0,
                    technical_state='maintenance',
                    biological_state='unknown',
                    contamination_state='suspected',
                    notes='Reaktor aktuell nicht produktiv, Wartung und Kontaminationspruefung laufen.',
                ),
            ),
        ]
        missing_twins = [
            twin
            for reactor_id, twin in reactor_twin_payloads
            if session.exec(select(ReactorTwin).where(ReactorTwin.reactor_id == reactor_id)).first() is None
        ]
        if missing_twins:
            session.add_all(missing_twins)
            session.commit()
            seeded_any = True

        reactor_event_payloads = [
            ReactorEvent(
                reactor_id=reactor.id,
                event_type='inoculation',
                title='Spirulina inokuliert',
                description='Frische Spirulina-Kultur mit Medium A angesetzt und Luftfluss geprueft.',
                severity='info',
                phase_snapshot='inoculation',
                created_at=now - timedelta(days=6),
            ),
            ReactorEvent(
                reactor_id=reactor_b.id,
                event_type='medium_change',
                title='Mediumwechsel B1',
                description='Teilweiser Mediumwechsel auf Medium B, danach Stabilisierung gestartet.',
                severity='warning',
                phase_snapshot='stabilization',
                created_at=now - timedelta(days=1, hours=3),
            ),
            ReactorEvent(
                reactor_id=reactor.id,
                event_type='observation',
                title='Wachstum homogen',
                description='Biomasseverteilung gleichmaessig, Schaumbildung unkritisch.',
                severity='info',
                phase_snapshot='growth',
                created_at=now - timedelta(hours=8),
            ),
            ReactorEvent(
                reactor_id=reactor_c.id,
                event_type='contamination_suspected',
                title='Kontaminationsverdacht C1',
                description='Auffaellige Truebung und Geruch festgestellt, Reaktor in Wartungsmodus belassen.',
                severity='high',
                phase_snapshot='incident',
                created_at=now - timedelta(hours=5),
            ),
        ]
        missing_events = [
            event
            for event in reactor_event_payloads
            if session.exec(select(ReactorEvent).where(ReactorEvent.title == event.title)).first() is None
        ]
        if missing_events:
            session.add_all(missing_events)
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
        pump_asset = session.exec(select(Asset).where(Asset.name == 'Pumpe A')).first()

        if has_inventory_item is None:
            inventory_items = [
                InventoryItem(
                    name='PLA Filament schwarz',
                    category='filament',
                    status='available',
                    quantity=2.5,
                    unit='kg',
                    min_quantity=1.0,
                    location='Werkbank 1',
                    zone='Maker Corner',
                    supplier='Prusa',
                    sku='FIL-PLA-BLK',
                    notes='Standardmaterial fuer Gehaeuse und Halterungen.',
                    asset_id=printer_asset.id if printer_asset else None,
                    last_restocked_at=now - timedelta(days=14),
                ),
                InventoryItem(
                    name='Isopropanol',
                    category='cleaning_supply',
                    status='low_stock',
                    quantity=0.7,
                    unit='l',
                    min_quantity=1.0,
                    location='Chemikalienschrank',
                    zone='Wet Lab',
                    supplier='Carl Roth',
                    sku='IPA-99',
                    expiry_date=(now + timedelta(days=300)).date(),
                ),
                InventoryItem(
                    name='pH Teststreifen',
                    category='consumable',
                    status='available',
                    quantity=60,
                    unit='pcs',
                    min_quantity=20,
                    location='Analytikschublade',
                    zone='Wet Lab',
                ),
                InventoryItem(
                    name='Silikonschlauch 6 mm',
                    category='tubing',
                    status='available',
                    quantity=8,
                    unit='m',
                    min_quantity=3,
                    location='Fluidik Rack',
                    zone='Wet Lab',
                    asset_id=pump_asset.id if pump_asset else None,
                ),
                InventoryItem(
                    name='JST Kabelsatz',
                    category='cable',
                    status='available',
                    quantity=12,
                    unit='sets',
                    min_quantity=4,
                    location='Elektronikplatz',
                    zone='Maker Corner',
                ),
                InventoryItem(
                    name='M3 Schrauben',
                    category='screw',
                    status='available',
                    quantity=240,
                    unit='pcs',
                    min_quantity=80,
                    location='Kleinteilewand',
                    zone='Maker Corner',
                ),
                InventoryItem(
                    name='Reinigungstuecher',
                    category='cleaning_supply',
                    status='low_stock',
                    quantity=1,
                    unit='pack',
                    min_quantity=2,
                    location='Putzschrank',
                    zone='Wet Lab',
                ),
                InventoryItem(
                    name='Ersatzduese MK4',
                    category='spare_part',
                    status='available',
                    quantity=3,
                    unit='pcs',
                    min_quantity=1,
                    location='Werkbank 1',
                    zone='Maker Corner',
                    asset_id=printer_asset.id if printer_asset else None,
                    notes='0.4 mm Messingduesen fuer den Prusa MK4.',
                ),
                InventoryItem(
                    name='Naehrmedium A',
                    category='nutrient',
                    status='low_stock',
                    quantity=0.4,
                    unit='l',
                    min_quantity=0.5,
                    location='Kuehlschrank Nord',
                    zone='Wet Lab',
                    expiry_date=(now + timedelta(days=12)).date(),
                ),
                InventoryItem(
                    name='Schrumpfschlauch Set',
                    category='electronic_component',
                    status='out_of_stock',
                    quantity=0,
                    unit='sets',
                    min_quantity=1,
                    location='Elektronikplatz',
                    zone='Maker Corner',
                ),
            ]
            session.add_all(inventory_items)
            session.commit()
            seeded_any = True

        server_asset = session.exec(select(Asset).where(Asset.name == 'Server1')).first()
        pla_filament = session.exec(select(InventoryItem).where(InventoryItem.name == 'PLA Filament schwarz')).first()
        isopropanol = session.exec(select(InventoryItem).where(InventoryItem.name == 'Isopropanol')).first()
        nozzle = session.exec(select(InventoryItem).where(InventoryItem.name == 'Ersatzduese MK4')).first()

        if has_label is None:
            labels = [
                Label(
                    label_code='LBL-AST-PRUSA-MK4',
                    label_type='qr',
                    target_type='asset',
                    target_id=printer_asset.id if printer_asset else 0,
                    display_name='Prusa MK4 QR',
                    location_snapshot='Werkbank 1 / Maker Corner',
                    is_active=printer_asset is not None,
                ),
                Label(
                    label_code='LBL-AST-SERVER1',
                    label_type='qr',
                    target_type='asset',
                    target_id=server_asset.id if server_asset else 0,
                    display_name='Server1 Rack Label',
                    location_snapshot='Rack A / Infra',
                    is_active=server_asset is not None,
                ),
                Label(
                    label_code='LBL-AST-MICRO-NORD',
                    label_type='qr',
                    target_type='asset',
                    target_id=microscope_asset.id if microscope_asset else 0,
                    display_name='Mikroskop Nordbank Label',
                    location_snapshot='Laborbank Nord / Wet Lab',
                    is_active=microscope_asset is not None,
                ),
                Label(
                    label_code='LBL-INV-PLA-BLACK',
                    label_type='qr',
                    target_type='inventory_item',
                    target_id=pla_filament.id if pla_filament else 0,
                    display_name='PLA Filament schwarz',
                    location_snapshot='Werkbank 1 / Maker Corner',
                    is_active=pla_filament is not None,
                ),
                Label(
                    label_code='LBL-INV-IPA-99',
                    label_type='qr',
                    target_type='inventory_item',
                    target_id=isopropanol.id if isopropanol else 0,
                    display_name='Isopropanol',
                    location_snapshot='Chemikalienschrank / Wet Lab',
                    is_active=isopropanol is not None,
                ),
                Label(
                    label_code='LBL-INV-MK4-NOZZLE',
                    label_type='qr',
                    target_type='inventory_item',
                    target_id=nozzle.id if nozzle else 0,
                    display_name='Ersatzduese MK4',
                    location_snapshot='Werkbank 1 / Maker Corner',
                    is_active=nozzle is not None,
                ),
            ]
            session.add_all([label for label in labels if label.target_id > 0])
            session.commit()
            seeded_any = True

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

        if session.exec(select(Task).where(Task.title == 'Reaktor C1 Laborcheck')).first() is None:
            session.add(
                Task(
                    title='Reaktor C1 Laborcheck',
                    description='Kontaminationsverdacht pruefen, Probe nehmen und ReactorOps-Status bestaetigen.',
                    status='open',
                    priority='critical',
                    due_at=now + timedelta(hours=4),
                    reactor_id=reactor_c.id if reactor_c else None,
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

        if session.exec(select(Alert).where(Alert.title == 'Reaktor C1 Kontaminationsverdacht')).first() is None:
            session.add(
                Alert(
                    title='Reaktor C1 Kontaminationsverdacht',
                    message='Reaktor-C1 bleibt bis zum Laborcheck in Maintenance; ReactorOps-V1 markiert den Twin als suspected.',
                    severity='high',
                    status='open',
                    source_type='reactor',
                    source_id=reactor_c.id if reactor_c else None,
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

        if session.exec(select(CalibrationRecord)).first() is None:
            reactor = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-A1')).first()
            reactor_c = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-C1')).first()
            node = session.exec(select(DeviceNode)).first()
            if reactor is not None:
                session.add(CalibrationRecord(
                    target_type='reactor',
                    target_id=reactor.id,
                    parameter='ph',
                    status='expired',
                    calibrated_at=now - timedelta(days=90),
                    due_at=now - timedelta(days=30),
                    calibration_value=7.01,
                    reference_value=7.00,
                    note='pH-Sonde A1 abgelaufen – Nachkalibrierung erforderlich.',
                    created_at=now - timedelta(days=90),
                    updated_at=now - timedelta(days=30),
                ))
                session.add(CalibrationRecord(
                    target_type='reactor',
                    target_id=reactor.id,
                    parameter='temp',
                    status='valid',
                    calibrated_at=now - timedelta(days=14),
                    due_at=now + timedelta(days=76),
                    calibration_value=23.1,
                    reference_value=23.0,
                    note='Temperaturmessung A1 kalibriert.',
                    created_at=now - timedelta(days=14),
                    updated_at=now - timedelta(days=14),
                ))
            if reactor_c is not None:
                session.add(CalibrationRecord(
                    target_type='reactor',
                    target_id=reactor_c.id,
                    parameter='ec',
                    status='due',
                    calibrated_at=now - timedelta(days=60),
                    due_at=now - timedelta(days=1),
                    note='EC-Sonde C1 faellig.',
                    created_at=now - timedelta(days=60),
                    updated_at=now - timedelta(days=1),
                ))
            if node is not None:
                session.add(CalibrationRecord(
                    target_type='device_node',
                    target_id=node.id,
                    parameter='flow',
                    status='valid',
                    calibrated_at=now - timedelta(days=7),
                    due_at=now + timedelta(days=83),
                    note='Flow-Sensor Node kalibriert.',
                    created_at=now - timedelta(days=7),
                    updated_at=now - timedelta(days=7),
                ))
            seeded_any = True

        if session.exec(select(MaintenanceRecord)).first() is None:
            reactor = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-A1')).first()
            reactor_b = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-B1')).first()
            node = session.exec(select(DeviceNode)).first()
            if reactor is not None:
                session.add(MaintenanceRecord(
                    target_type='reactor',
                    target_id=reactor.id,
                    maintenance_type='cleaning',
                    status='overdue',
                    due_at=now - timedelta(days=5),
                    note='Wöchentliche Reinigung Reaktor A1 ueberfaellig.',
                    created_at=now - timedelta(days=12),
                    updated_at=now - timedelta(days=5),
                ))
                session.add(MaintenanceRecord(
                    target_type='reactor',
                    target_id=reactor.id,
                    maintenance_type='tubing_flush',
                    status='scheduled',
                    due_at=now + timedelta(days=3),
                    note='Schlauchspuelung planmaessig.',
                    created_at=now - timedelta(days=2),
                    updated_at=now - timedelta(days=2),
                ))
            if reactor_b is not None:
                session.add(MaintenanceRecord(
                    target_type='reactor',
                    target_id=reactor_b.id,
                    maintenance_type='pump_service',
                    status='done',
                    performed_at=now - timedelta(days=3),
                    note='Pumpenservice Reaktor B1 abgeschlossen.',
                    created_at=now - timedelta(days=10),
                    updated_at=now - timedelta(days=3),
                ))
            if node is not None:
                session.add(MaintenanceRecord(
                    target_type='device_node',
                    target_id=node.id,
                    maintenance_type='inspection',
                    status='scheduled',
                    due_at=now + timedelta(days=7),
                    note='Node-Inspektion geplant.',
                    created_at=now - timedelta(days=1),
                    updated_at=now - timedelta(days=1),
                ))
            seeded_any = True

        if session.exec(select(SafetyIncident)).first() is None:
            reactor = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-A1')).first()
            reactor_c = session.exec(select(Reactor).where(Reactor.name == 'Reaktor-C1')).first()
            node = session.exec(select(DeviceNode)).first()
            if reactor is not None:
                session.add(SafetyIncident(
                    reactor_id=reactor.id,
                    incident_type='calibration_expired',
                    severity='high',
                    status='open',
                    title='pH-Kalibrierung Reaktor A1 abgelaufen',
                    description='Die pH-Sonde wurde seit 90 Tagen nicht kalibriert. Steuerungsbefehle mit pH-Bezug koennen blockiert werden.',
                    created_at=now - timedelta(days=2),
                ))
                session.add(SafetyIncident(
                    reactor_id=reactor.id,
                    incident_type='clogging_suspected',
                    severity='warning',
                    status='acknowledged',
                    title='Verstopfungsverdacht Zulaufschlauch A1',
                    description='Anomaler Druckabfall im Zuluftschlauch erkannt. Bitte ueberpruefen.',
                    created_at=now - timedelta(days=5),
                ))
            if reactor_c is not None:
                session.add(SafetyIncident(
                    reactor_id=reactor_c.id,
                    incident_type='node_offline',
                    severity='warning',
                    status='open',
                    title='Sensor-Node Reaktor C1 offline',
                    description='Der zugeordnete Sensor-Node meldet sich seit > 15 Minuten nicht mehr.',
                    created_at=now - timedelta(hours=2),
                ))
            if node is not None:
                session.add(SafetyIncident(
                    device_node_id=node.id,
                    incident_type='invalid_telemetry',
                    severity='info',
                    status='resolved',
                    title='Ungueltige Telemetriewerte empfangen',
                    description='Kurzzeitig ungueltige Messwerte vom Node empfangen. Selbst behoben.',
                    created_at=now - timedelta(days=7),
                    resolved_at=now - timedelta(days=6),
                ))
            seeded_any = True

        if seeded_any:
            session.commit()

        return seeded_any


if __name__ == '__main__':
    seed_data()

"""ABrain Action Catalog V1.

Statischer, kuratierter Katalog der LabOS-Aktionen, die ABrain als externes
Brain vorschlagen oder ausloesen darf. LabOS definiert hier bewusst eine
enge, begruendete Tool-Surface anstelle einer dynamischen Registry.

Jede Aktion traegt Risiko-/Approval-/Rollen-Metadaten, damit ABrain
Governance-Entscheidungen treffen kann. Die tatsaechliche Ausfuehrung
bleibt immer auf den regulaeren LabOS-Endpunkten und wird von den lokalen
Safety-/Role-Guards ueberprueft.
"""

from ..models import _utcnow
from ..schemas import (
    ABrainActionCatalogRead,
    ABrainActionDescriptor,
    ABrainActionDomain,
    ABrainActionRiskLevel,
)


_CONTRACT_VERSION = 'v1'


_ACTIONS: list[ABrainActionDescriptor] = [
    ABrainActionDescriptor(
        name='labos.create_task',
        description='Erzeugt einen operativen Task im LabOS Task-Board.',
        domain=ABrainActionDomain.operations,
        risk_level=ABrainActionRiskLevel.low,
        requires_approval=False,
        allowed_roles=['operator', 'admin'],
        arguments={
            'title': 'string, required',
            'description': 'string, optional',
            'priority': 'low|normal|high|critical, optional',
            'due_at': 'ISO-8601 datetime, optional',
            'charge_id': 'int, optional',
            'reactor_id': 'int, optional',
            'asset_id': 'int, optional',
        },
        guarded_by=['role: operator|admin'],
    ),
    ABrainActionDescriptor(
        name='labos.create_alert',
        description='Erzeugt einen Alert (z.B. fuer Incident-Tracking oder Operator-Aufmerksamkeit).',
        domain=ABrainActionDomain.operations,
        risk_level=ABrainActionRiskLevel.low,
        requires_approval=False,
        allowed_roles=['operator', 'admin'],
        arguments={
            'title': 'string, required',
            'message': 'string, required',
            'severity': 'info|warning|high|critical',
            'source_type': 'sensor|charge|reactor|manual',
            'source_id': 'int, optional',
        },
        guarded_by=['role: operator|admin'],
    ),
    ABrainActionDescriptor(
        name='labos.run_reactor_health_assessment',
        description='Triggert eine neue deterministische Reactor-Health-Bewertung fuer einen Reaktor.',
        domain=ABrainActionDomain.reactor,
        risk_level=ABrainActionRiskLevel.low,
        requires_approval=False,
        allowed_roles=['operator', 'admin'],
        arguments={'reactor_id': 'int, required'},
        guarded_by=['role: operator|admin'],
        notes='Keine Hardware-Wirkung. Reine Auswertung aus vorhandenen Daten.',
    ),
    ABrainActionDescriptor(
        name='labos.create_reactor_command',
        description='Queued einen Reactor-Command (Licht, Pumpe, Aeration, Sample-Capture, ...) ueber den Safety-Guard-Pfad.',
        domain=ABrainActionDomain.reactor,
        risk_level=ABrainActionRiskLevel.high,
        requires_approval=True,
        allowed_roles=['operator', 'admin'],
        arguments={
            'reactor_id': 'int, required',
            'command_type': 'light_on|light_off|pump_on|pump_off|aeration_on|aeration_off|sample_capture',
            'channel': 'string, optional',
            'params': 'object, optional',
        },
        guarded_by=[
            'SafetyIncident critical',
            'DeviceNode offline/error',
            'dry_run_risk incident',
            'expired calibration for sample_capture',
        ],
        notes='Wird lokal durch Command-Guard serverseitig validiert; LabOS kann den Befehl mit blocked_reason zurueckweisen.',
    ),
    ABrainActionDescriptor(
        name='labos.retry_reactor_command',
        description='Wiederholt einen zuvor fehlgeschlagenen oder abgelaufenen Reactor-Command.',
        domain=ABrainActionDomain.reactor,
        risk_level=ABrainActionRiskLevel.high,
        requires_approval=True,
        allowed_roles=['operator', 'admin'],
        arguments={'command_id': 'int, required'},
        guarded_by=['max_retries', 'Command-Status not acknowledged/blocked'],
    ),
    ABrainActionDescriptor(
        name='labos.ack_safety_incident',
        description='Quittiert einen offenen Safety-Incident.',
        domain=ABrainActionDomain.safety,
        risk_level=ABrainActionRiskLevel.medium,
        requires_approval=True,
        allowed_roles=['operator', 'admin'],
        arguments={'incident_id': 'int, required', 'note': 'string, optional'},
        guarded_by=['role: operator|admin', 'Incident-Status open'],
    ),
    ABrainActionDescriptor(
        name='labos.create_maintenance_record',
        description='Legt einen Wartungseintrag fuer Reaktor/Node/Asset an.',
        domain=ABrainActionDomain.maintenance,
        risk_level=ABrainActionRiskLevel.low,
        requires_approval=False,
        allowed_roles=['operator', 'admin'],
        arguments={
            'target_type': 'reactor|device_node|asset',
            'target_id': 'int, required',
            'maintenance_type': 'cleaning|inspection|replacement|...',
            'scheduled_at': 'ISO-8601 datetime, optional',
            'notes': 'string, optional',
        },
    ),
    ABrainActionDescriptor(
        name='labos.create_calibration_record',
        description='Erzeugt einen Kalibriereintrag.',
        domain=ABrainActionDomain.maintenance,
        risk_level=ABrainActionRiskLevel.low,
        requires_approval=False,
        allowed_roles=['operator', 'admin'],
        arguments={
            'target_type': 'reactor|device_node|asset',
            'target_id': 'int, required',
            'parameter': 'ph|temp|ec|flow|...',
            'valid_until': 'ISO-8601 datetime, optional',
            'notes': 'string, optional',
        },
    ),
    ABrainActionDescriptor(
        name='labos.run_schedule_now',
        description='Fuehrt einen vorhandenen Schedule einmalig manuell aus (trigger=manual).',
        domain=ABrainActionDomain.scheduler,
        risk_level=ABrainActionRiskLevel.medium,
        requires_approval=True,
        allowed_roles=['operator', 'admin'],
        arguments={'schedule_id': 'int, required'},
        guarded_by=['Command-Guard for command-schedules', 'role: operator|admin'],
    ),
]


def get_catalog() -> ABrainActionCatalogRead:
    return ABrainActionCatalogRead(
        contract_version=_CONTRACT_VERSION,
        generated_at=_utcnow(),
        actions=list(_ACTIONS),
    )


def find_action(name: str) -> ABrainActionDescriptor | None:
    for action in _ACTIONS:
        if action.name == name:
            return action
    return None

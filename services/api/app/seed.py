from sqlmodel import Session, select

from .db import engine
from .models import Alert, Charge, Reactor, Task, WikiPage


def seed_data() -> None:
    with Session(engine) as session:
        has_charge = session.exec(select(Charge)).first()
        if has_charge:
            return

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

        session.add(Charge(name='Charge-001', species='Chlorella vulgaris', status='active', volume_l=1.4, reactor_id=reactor.id))
        session.add(Task(title='Probe entnehmen', status='open'))
        session.add(Alert(level='warning', message='pH-Kalibrierung in 2 Tagen fällig', status='open'))
        session.add(WikiPage(slug='howto/erste-charge', title='Erste Charge anlegen', summary='Kurzanleitung für die erste Charge'))
        session.add(WikiPage(slug='sop/reinigung-reaktor', title='SOP Reaktor reinigen', summary='Reinigungsschritte für mobile Reaktoren'))
        session.commit()

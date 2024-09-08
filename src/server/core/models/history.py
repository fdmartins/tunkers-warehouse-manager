from core import db
from datetime import datetime

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(20))
    level = db.Column(db.String(20))
    message = db.Column(db.String(200))
    dt_created = db.Column(db.DateTime, default=datetime.now())


    def info(alert_type, message):
        a = History(
            alert_type=alert_type,
            level="INFO",
            message=message,
            dt_created=datetime.now()  
        )

        db.session.add(a)
        db.session.commit()

    def warning(alert_type, message):
        a = History(
            alert_type=alert_type,
            level="ATENÇÃO",
            message=message,
            dt_created=datetime.now()  
        )

        db.session.add(a)
        db.session.commit()

    def error(alert_type, message):
        a = History(
            alert_type=alert_type,
            level="ERRO",
            message=message,
            dt_created=datetime.now()  
        )

        db.session.add(a)
        db.session.commit()
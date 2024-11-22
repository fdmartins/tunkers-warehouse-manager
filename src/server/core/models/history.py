from core import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(20))
    level = db.Column(db.String(20))
    message = db.Column(db.String(200))
    dt_created = db.Column(db.DateTime, default=datetime.now())

    def info(alert_type, message):

        logger.info(f"Historico {alert_type} {message}")

        a = History(
            alert_type=alert_type,
            level="INFO",
            message=message,
            dt_created=datetime.now()  
        )

        db.session.add(a)
        db.session.commit()

    def warning(alert_type, message):
        logger.warning(f"Historico {alert_type} {message}")

        a = History(
            alert_type=alert_type,
            level="ATENÇÃO",
            message=message,
            dt_created=datetime.now()  
        )

        db.session.add(a)
        db.session.commit()

    def error(alert_type, message):
        # Verifica se já existe uma mensagem igual no banco
        # evitando mostrar sempre a mesma coisa... 
        # NAO FUNCIONOU, pois exceptionm retorna objeto hex que muda o tempo todo...
        #if History.query.filter_by(message=message).first():
        #    return
        
        logger.error(f"Historico {alert_type} {message}")

        a = History(
            alert_type=alert_type,
            level="ERRO",
            message=message,
            dt_created=datetime.now()  
        )

        db.session.add(a)
        db.session.commit()
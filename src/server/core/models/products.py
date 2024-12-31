from core import db
from datetime import datetime

class ProdutosCompleto(db.Model):
    """
    CREATE TABLE "produtos_completo" (
	"id"	INTEGER NOT NULL,
	"sku"	TEXT,
	"nome"	TEXT,
	"tipo"	TEXT,
	PRIMARY KEY("id")
    )
    """
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(250), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)


class ProdutosResumido(db.Model):
    """
    CREATE TABLE "produtos_resumido" (
	"id"	INTEGER NOT NULL,
	"bitola"	TEXT,
	"nome"	TEXT,
	"sku"	TEXT,
	"tipo"	TEXT,
	PRIMARY KEY("id")
    )
    """
    id = db.Column(db.Integer, primary_key=True)
    bitola = db.Column(db.String(10), nullable=False)
    nome = db.Column(db.String(250), nullable=False)
    sku = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)

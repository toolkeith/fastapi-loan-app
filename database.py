from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CONFIGURATION ---
# The IP of your Load Balancer (VM-LB)
LB_IP = "192.168.254.90" 
DB_USER = "loanadmin"
DB_PASS = "securepass123"
DB_NAME = "loan_db"

# --- CONNECTION 1: MASTER (Writes & Critical Reads) ---
# Connects to HAProxy Port 3306 -> Master DB
URL_MASTER = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{LB_IP}:3306/{DB_NAME}"
engine_master = create_engine(URL_MASTER)
SessionMaster = sessionmaker(autocommit=False, autoflush=False, bind=engine_master)

# --- CONNECTION 2: SLAVE (Read Only - For Login) ---
# Connects to HAProxy Port 3307 -> Slave DB
URL_SLAVE = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{LB_IP}:3307/{DB_NAME}"
engine_slave = create_engine(URL_SLAVE)
SessionSlave = sessionmaker(autocommit=False, autoflush=False, bind=engine_slave)

Base = declarative_base()

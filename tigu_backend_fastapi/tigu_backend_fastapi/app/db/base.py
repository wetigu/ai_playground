from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True,
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User, UserSession, Company, CompanyUser
from app.models.product import Product, Category, ProductImage, ProductVideo
from app.models.order import Order, OrderItem, Quotation, QuotationItem

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Drop all tables (for development/testing)
def drop_tables():
    Base.metadata.drop_all(bind=engine)

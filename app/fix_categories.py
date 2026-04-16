from database import SessionLocal
from models import Category

db = SessionLocal()

categorias = {
    1: ('Supermercado', '🛒'),
    2: ('Restaurante', '🍽️'),
    3: ('Transporte', '🚗'),
    4: ('Salud', '💊'),
    5: ('Entretenimiento', '🎬'),
    6: ('Ropa', '👕'),
    7: ('Servicios', '💡'),
    8: ('Otro', '💳')
}

for id, (name, icon) in categorias.items():
    db.query(Category).filter(Category.id == id).update({
        'name': name,
        'icon': icon
    })

db.commit()
print("✅ Categorías corregidas")
db.close()
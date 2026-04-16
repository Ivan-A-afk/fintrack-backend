from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
import models, os, shutil, base64, json, re
from dotenv import load_dotenv
import httpx

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)

@app.get("/persons")
def get_persons(db: Session = Depends(get_db)):
    return db.query(models.Person).all()

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@app.get("/expenses")
def get_expenses(db: Session = Depends(get_db)):
    return db.query(models.Expense).order_by(models.Expense.date.desc()).all()

@app.post("/expenses")
def create_expense(
    person_id: int = Form(...),
    category_id: int = Form(...),
    amount: float = Form(...),
    commerce: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    expense = models.Expense(
        person_id=person_id,
        category_id=category_id,
        amount=amount,
        commerce=commerce,
        description=description
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    db.delete(expense)
    db.commit()
    return {"mensaje": "Gasto eliminado"}

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()
    total = sum(float(e.amount) for e in expenses)
    ivan = sum(float(e.amount) for e in expenses if e.person_id == 1)
    carolina = sum(float(e.amount) for e in expenses if e.person_id == 2)
    return {
        "total": total,
        "ivan": ivan,
        "carolina": carolina,
        "count": len(expenses)
    }

@app.post("/scan")
async def scan_image(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with open(file_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "nvidia/nemotron-nano-12b-v2-vl:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": """Esta es una notificación de un banco chileno.
Extrae la siguiente información en formato JSON:
{
    "amount": (número sin puntos ni símbolos, solo el número),
    "commerce": (nombre del comercio o descripción),
    "date": (fecha si aparece, si no null)
}
Solo responde el JSON, nada más."""
                            }
                        ]
                    }
                ]
            },
            timeout=30.0
        )

    result = response.json()
    print("RESPUESTA OPENROUTER:", result)
    text = result["choices"][0]["message"]["content"].strip()
    text = re.sub(r'```json|```', '', text).strip()
    data = json.loads(text)
    return {
        "amount": data.get("amount"),
        "commerce": data.get("commerce"),
        "date": data.get("date")
    }
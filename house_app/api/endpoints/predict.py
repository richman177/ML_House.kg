from house_app.db.models import Predict
from house_app.db.schema import PredictSchema
from sqlalchemy.orm import Session
from house_app.db.database import SessionLocal
from fastapi import Depends, HTTPException, APIRouter
from typing import List, Optional
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

predict_router = APIRouter(prefix='/predict',  tags=['Predict'])

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

model_path = BASE_DIR / 'house_price_model_job.pkl'
scaler_path = BASE_DIR / 'scaler.pkl'

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@predict_router.post('/', response_model=PredictSchema, summary='Создать predict')
async def create_predict(predict: PredictSchema, db: Session = Depends(get_db)):
    predict_db = Predict(category_name=predict.id)
    db.add(predict_db)
    db.commit()
    db.refresh(predict_db)
    return predict_db


@predict_router.get('/', response_model=List[PredictSchema], summary='Получить все predict')
async def predict_list(db: Session = Depends(get_db)):
    return db.query(Predict).all()


@predict_router.get('/{predict_id}', response_model=PredictSchema, summary='Получить predict')
async def predict_detail(predict_id: int, db: Session = Depends(get_db)):
    predict = db.query(Predict).filter(Predict.id == predict_id).first()

    if predict is None:
        raise HTTPException(status_code=400, detail='Мындай маалымат жок')
    return predict


@predict_router.put('/{predict_id}', summary='Обновить predict_db')
async def predict_update(predict_id: int, predict: PredictSchema, db: Session = Depends(get_db)):
    predict_db = db.query(Predict).filter(Predict.id == predict_id).first()

    if predict_db is None:
        raise HTTPException(status_code=400, detail='Мындай маалымат жок')

    for predict_key, predict_values in predict.dict().items():
        setattr(predict_db, predict_key, predict_values)

    predict_db.id = predict.id
    db.add(predict_db)
    db.commit()
    db.refresh(predict_db)
    return predict_db


@predict_router.delete('/{predict_id}', summary='Удалить')
async def predict_delete(predict_id: int, db: Session = Depends(get_db)):
    predict_db = db.query(Predict).filter(Predict.id == predict_id).first()

    if predict_db is None:
        raise HTTPException(status_code=400, detail='Мындай маалымат жок')

    db.delete(predict_db)
    db.commit()
    db.refresh()
    return {'message': 'This predict is deleted'}

model_columns = [
    'GrLivArea',
    'YearBuilt',
    'GarageCars',
    'TotalBsmtSF',
    'FullBath',
    'OverallQual'
]


@predict_router.post('/predict')
async def predict_price(predict: PredictSchema, db: Session = Depends(get_db)):
    input_data = {
        'GrLivArea': predict.total_live_area,
        'YearBuilt': predict.built_year,
        'GarageCars': predict.garage_cars,
        'TotalBsmtSF': predict.basement_area,
        'FullBath': predict.full_bath,
        'OverallQual': predict.quality_level
    }
    input_df = pd.DataFrame([input_data])
    scaled_df = scaler.transform(input_df)
    predicted_price = model.predict(scaled_df)[0]
    return {'predicted_price': round(predicted_price)}
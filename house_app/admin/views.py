from sqladmin import ModelView   
from house_app.db.models import UserProfile, Predict


class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [UserProfile.id, UserProfile.username]
    name = 'User'
    name_plural = 'Users'


class PredictAdmin(ModelView, model=Predict):
    column_list = [Predict.id, Predict.region] 
    name = 'Predict'
    name_plural = 'Predicts'

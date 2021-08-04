from flask_admin import BaseView, expose
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from werkzeug.utils import redirect

from app import db, admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from flask_login import UserMixin, logout_user, current_user
import enum


class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    products = relationship('Product', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Product(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, default=0)
    image = Column(String(255), nullable=True)
    description = Column(String(255), nullable=False)
    # created_date = Column(DateTime, default=datetime.now())
    category_id = Column(Integer, ForeignKey(Category.id))
    creator_id = Column(Integer, ForeignKey('user.id'))
    receipt_details = relationship('ReceiptDetail', backref='product', lazy=True)


class UserRole(enum.Enum):
    ADMIN = 1
    USER = 2


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    active = Column(Boolean, default=True)
    use_role = Column(Enum(UserRole), default=UserRole.USER)
    products = relationship(Product, backref='user', lazy=True)


class Receipt(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    updated_date = Column(DateTime, default=datetime.now())
    details = relationship('ReceiptDetail', backref='receipt', lazy=True)


class ReceiptDetail(db.Model):
    product_id = Column(Integer, ForeignKey(Product.id), primary_key=True)
    receipt_id = Column(Integer, ForeignKey(Receipt.id), primary_key=True)
    product_name = Column(String(50))
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)

class LogoutView(BaseView):
    @expose("/")
    def index(self):
        logout_user()

        return redirect("/admin")

    def is_accessible(self):  # dang nhap moi hien thi
        return current_user.is_authenticated

class CategoryModelView(ModelView):
    column_display_pk = True #hien khoa chinh

    def is_accessible(self): #dang nhap moi hien thi
        return current_user.is_authenticated

class ProductModelView(ModelView):
    column_display_pk = True #hien khoa chinh

    def is_accessible(self): #dang nhap moi hien thi
        return current_user.is_authenticated

class UserModelView(ModelView):
    column_display_pk = True #hien khoa chinh

    def is_accessible(self): #dang nhap moi hien thi
        return current_user.is_authenticated


admin.add_view(CategoryModelView(Category, db.session))
admin.add_view(ProductModelView(Product, db.session))
admin.add_view(UserModelView(User, db.session))
admin.add_view(LogoutView(name="Đăng xuất"))

if __name__ == '__main__':
    db.create_all()
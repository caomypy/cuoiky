import hashlib
from flask import render_template, request, redirect, url_for, jsonify, send_file, session, flash
from app import app, dao, login, models
from app import decorator
from flask_login import LoginManager, current_user
from flask_login import login_user, logout_user
from app.decorator import login_required
import json

from app.models import User


@app.route("/")
def index():
    phones = models.Category.query.get(1).products

    tablets = models.Category.query.get(2).products

    return render_template("index.html", products=dao.read_products(),
                           phones=phones, tablets=tablets
                           )

@app.route("/search")
def search():
    keyword = request.args["keyword"] if request.args.get("keyword") else None
    return render_template("search.html", products=dao.read_products(keyword=keyword)
                           )



@app.route("/products")
def product_list():
    keyword = request.args["keyword"] if request.args.get("keyword") else None
    return render_template("product-list.html", products=dao.read_products(keyword=keyword))


@app.route('/products/detail/<int:product_id>')
def product_detail(product_id):
    product = models.Product.query.get_or_404(product_id)
    # dòng này giúp danh mục sản phẩm hiện ra các tên có trong bảng category
    return render_template('product-detail.html', product=product)





@app.route("/products/<int:category_id>")
def product_list_by_cate(category_id):
    return render_template("product-list.html", products=dao.read_products_by_cate_id(cate_id=category_id))



@app.route("/login-admin", methods=["POST", "GET"])
def login_admin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password", "")
        user_role = request.form.get("use_role")
        user_role = "ADMIN"
        password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
        user = User.query.filter(User.username ==username.strip(),
                                 User.password == password, User.use_role == user_role).first()

        if user:
            login_user(user=user)
    return redirect("/admin")


@app.route("/login", methods=["get", "post"])
def signin_user():
    err_msg = ""
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = dao.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            if "next" in request.args:
                return redirect(request.args["next"])

            return redirect(url_for('index'))
        else:
            err_msg = "Something wrong!!!"

    return render_template("login.html", err_msg=err_msg)


@app.route("/logout")
def logout():
    logout_user()

    return redirect(url_for("index"))


@app.route("/register", methods=["get", "post"])
def register():
    if session.get("user"):
        return redirect(request.url)

    err_msg = ""
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if password.strip() != confirm.strip():
            err_msg = "Mat khau khong khop"
        else:
            if dao.add_user(name=name, username=username, password=password):
                return redirect(url_for("signin_user"))
            else:
                err_msg = "Lỗi"

    return render_template("register.html", err_msg=err_msg)


@app.route("/cart", methods=['get', 'post'])
@login_required
def cart():
    err_msg = ""
    if request.method == 'POST':
        if 'cart' in session and session['cart']:
            if dao.add_receipt(cart_products=session["cart"].values()):
                session['cart'] = None
                return redirect(url_for('cart'))
            else:
                err_msg = "Add receipt failed"
        else:
            err_msg = "Không có sản phẩm trong giỏ hàng"

    return render_template("payment.html", err_msg=err_msg)

# #chức năng xóa item có trong giỏ hàng
# @app.route('/deleteItem/<int:id>')
# def deleteItem(id):
#     if 'cart' not in session and len(session['cart']) <= 0:
#         return redirect(url_for('index'))
#
#     try:
#         session.modified = True
#         for key, item in session['cart'].items():
#             if int(key) == id:
#                 session['cart'].pop(key, None)
#                 return redirect(url_for('cart'))
#     except Exception as e:
#         print(e)
#         return redirect(url_for('cart'))

# @app.route('/api/cart/<item_id>')
# def delete_item(item_id):
#     if 'cart' in session:
#         cart = session['cart']
#         if item_id in cart:
#             del cart[item_id]
#
#             return jsonify({'err_msg': 'successful', 'code': 200})
#
#         return jsonify({'err_msg': 'failed', 'code': 500})

@app.route("/api/cart", methods=["post"])
def add_to_cart():
    data = json.loads(request.data)
    product_id = data.get("product_id")
    name = data.get("name")
    price = data.get("price")
    if "cart" not in session or session['cart'] == None:
        session["cart"] = {}

    cart = session["cart"]

    product_key = str(product_id)
    if product_key in cart: # đa từng bỏ sản phẩm product_id vào giỏ
        cart[product_key]["quantity"] = cart[product_key]["quantity"] + 1
    else: # bỏ sản phẩm mới vào giỏ
        cart[product_key] = {
            "id": product_id,
            "name": name,
            "price": price,
            "quantity": 1
        }

    session["cart"] = cart
    q = 0
    s = 0
    for c in list(session["cart"].values()):
        q = q + c['quantity']
        s = s + c['quantity'] * c['price']

    return jsonify({"success": 1, "quantity": q, 'sum': s})



@app.context_processor
def append_cate():
    common = {
        "categories": dao.read_categories()
    }

    if 'cart' in session and session['cart']:
        q = 0
        s = 0
        for c in list(session["cart"].values()):
            q = q + c['quantity']
            s = s + c['quantity'] * c['price']

        common['cart_quantity'] = q
        common['cart_price'] = s

    return common



@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id=user_id)


if __name__ == "__main__":
    app.run(debug=True, port=8801)

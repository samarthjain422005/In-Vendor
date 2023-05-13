from flask import Flask, render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,login_required,logout_user,current_user, LoginManager
from sqlalchemy.sql import func
from sqlalchemy import Table, Column,Integer, ForeignKey
from datetime import date
from sqlalchemy import create_engine

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.sqlite3'
#database
db=SQLAlchemy(app)
DB_NAME="./database.db"

login_manager=LoginManager(app)
login_manager.login_view='login'
engine=create_engine('sqlite:///database.sqlite3')

  
@login_manager.user_loader
def load_user(username):
  return User.query.get(username)


class Billing(db.Model):
  username=db.Column(db.String(150),ForeignKey('user.username'))
  bill_no=db.Column(db.String(150))
  s_no=db.Column(db.String(150),primary_key=True)
  date=db.Column(db.DateTime)
  customer_name=db.Column(db.String(150))
  mobile_number=db.Column(db.String(150))
  product_name=db.Column(db.String(150))
  product_id=db.Column(db.String(150))
  price_per_unit=db.Column(db.Integer)
  quantity=db.Column(db.Integer)
  sgst=db.Column(db.Float)
  cgst=db.Column(db.Float)
  total_price=db.Column(db.Float)

class Products(db.Model):
  username=db.Column(db.String(150),ForeignKey('user.username'))
  product_id=db.Column(db.String(150),primary_key=True)
  product_name=db.Column(db.String(150))
  price_per_unit=db.Column(db.Integer)
  sgst=db.Column(db.Float)
  cgst=db.Column(db.Float)
  quantity_sold=db.Column(db.Float)
  stock=db.Column(db.Integer)
  
class Taxes(db.Model):
  username=db.Column(db.String(150),ForeignKey('user.username'))
  product_id=db.Column(db.String(150),primary_key=True)
  gst_per_product=db.Column(db.Float)
  quantity_sold=db.Column(db.Integer)
  gst_collected=db.Column(db.Float)
  status=db.Column(db.String(150))
  

class User(db.Model,UserMixin):
  id=db.Column(db.Integer,unique=True)
  username=db.Column(db.String(150),primary_key=True)
  store_name=db.Column(db.String(150),unique=True)
  email=db.Column(db.String(150),unique=True)
  password=db.Column(db.String(150),unique=True)
  address=db.Column(db.String(150))
  city=db.Column(db.String(150))
  country=db.Column(db.String(150))
  pincode=db.Column(db.String(150))
  store_category=db.Column(db.String(150))
  billing=db.relationship('Billing')
  products=db.relationship('Products')
  taxes=db.relationship('Taxes')

db.create_all()

 
#page routing
@app.route("/")
def index():
  return render_template('index.html')

@app.route("/logout")
@login_required
def logout():
  logout_user() 
  return redirect(url_for("index"))

@app.route("/home")
@login_required
def home():
  return render_template('home.html',user=current_user)

@app.route("/sign-up",methods=['GET','POST'])
def sign_up():
   if request.method=='POST':
     username=request.form.get('username')
     store_name=request.form.get('organisation name')
     email=request.form.get('email')
     password1=request.form.get('password')
     password2=request.form.get('confirm password')
     address=request.form.get('address')
     city=request.form.get('city')
     country=request.form.get('country')
     pincode=request.form.get('pincode')
     store_category=request.form.get('store category')

     user=User.query.filter_by(username=username).first()
     if user:
       flash("Username already exists",category='error')
     elif len(email)<4:
       flash("Email must be greater than 4 characters",category='error')
     elif len(username)<2:
       flash("Username must be greater than 2 characters",category='error')
     elif password1!=password2:
       flash("Passwords don't match",category='error')
     elif len(password1)<7:
       flash("Password less than 7",category='error')
     else:
       new_user=User(username=username,store_name= store_name,email=email,password=password1,address=address,city=city,country=country,pincode=pincode,store_category=store_category)
       db.session.add(new_user)
       db.session.commit()
       login_user(user,remember=True)
       flash("Account created!!",category='success')
       return redirect(url_for('home'))
      


@app.route("/login",methods=['GET','POST'])
def login():
   if request.method=="POST":
     username=request.form.get('username')
     password=request.form.get('password')

     user=User.query.filter_by(username=username).first()
     if user:
       if user.password==password:
         flash("Logged in Successfully!!",category="success")
         login_user(user,remember=True)
         
         return redirect(url_for('home'))
       else:
         flash("Incorrect password , try again",category="error")
     else:
       flash("Username doesn't exist",category="error")
   return render_template('login.html',user=current_user)

@app.route("/billing")
@login_required
def billing():
   return render_template('billing.html',user=current_user)

@app.route("/billing/new-bill")
@login_required
def new_bill():
   if request.method=="POST":
     bill_no_temp=db.session.query(func.max(id)).all()
     bill_no_temp1=int(bill_no_temp[12:])
     username=current_user
     store_id=User.query.filter_by(username=username).first()
     date=date.today()
     bill_no=date+"-"+store_id+"-"+str(bill_no_temp1+1)
     name=request.form.get('customer_name')
     mobile_no=request.form.get('mobile_no')
     no_of_item=request.form.get('no_of_item')
     maxitem=99
     if (no_of_item>maxitem):
         print()
         flash("Please enter less than 99 items or split the bill into two",category="error")
     elif (no_of_item<=maxitem) :
         for a in range(no_of_item):
           if a<10:
             s_no=bill_no+'xx0'+str(a)
             product_code=request.form.get('no_of_item')
             rec=Products.query.filter_by(username=username).first()
             for r in rec:
                 product_name=r[2]
                 mrp=r[3]
                 sgst=r[4]
                 cgst=r[5]
                 qty=r[6]
                 stock_available=r[7]
             quantity=request.form.get('quantity')
             t=(mrp+sgst+cgst)*quantity
             j=Billing(store_id=store_id,bill_no=bill_no, s_no=s_no, date=date, customer_name=name, mobile_no=mobile_no, product_name=product_name, product_code=product_code, mrp=mrp, quantity=quantity, sgst=sgst, cgst=cgst, total=t)
             db.session.add(j)
             db.session.commit()
             upd = db.update(Products)
             val = upd.values({"stock":"stock_available-quantity"})
             cond = val.where(Products.c.product_id == product_code)
             engine.execute(upd)
            
             w=qty+quantity
             upd = db.update(Products)
             val = upd.values({"quatity_sold":"w"})
             cond = val.where(Products.c.product_id == product_code)
             engine.execute(upd)
            
             record=Taxes.query.filter_by(product_id=product_code).first()
             for u in record:
               quantity_sold=u[2]+quantity
               gst_collected=u[3]+(sgst+cgst)*quantity
             upd = db.update(Taxes)
             val = upd.values({"quantity_sold":"quantity_sold"},{"gst_collected":"gst_collected"},{"status":"Due"})
             cond = val.where(Billing.c.product_id == product_code)
             engine.execute(upd)
                              
           else:
             s_no=bill_no+'xx'+str(a)
             product_code=request.form.get('no_of_item')
             rec=Products.query.filter_by(username=username).first()
             for r in rec:
                 product_name=r[2]
                 mrp=r[3]
                 sgst=r[4]
                 cyst=r[5]
                 qty=r[6]
                 stock_available=r[7]
             quantity=request.form.get('quantity')
             t=(mrp+sgst+cgst)*quantity
             j=Billing(store_id=store_id,bill_no=bill_no, s_no=s_no, date=date, name=date, mobile_no=mobile_no, product_name=product_name, product_code=product_code, mrp=mrp, quantity=quantity, sgst=sgst, cgst=cgst, total=t)
             db.session.add(j)
             db.session.commit()
             upd = db.update(Products)
             val = upd.values({"stock":"stock_available-quantity"})
             cond = val.where(Products.c.product_id == product_code)
             engine.execute(upd)
            
             w=qty+quantity
             upd = db.update(Products)
             val = upd.values({"quatity_sold":"w"})
             cond = val.where(Products.c.product_id == product_code)
             engine.execute(upd)
            
             record=Taxes.query.filter_by(product_id=product_code).first()
             for u in record:
               quantity_sold=u[2]+quantity
               gst_collected=u[3]+(sgst+cgst)*quantity
             upd = db.update(Taxes)
             val = upd.values({"quantity_sold":"quantity_sold"},{"gst_collected":"gst_collected"},{"status":"Due"})
             cond = val.where(Billing.c.product_id == product_code)
             engine.execute(upd)
              
     flash("Billing Success!!",category="success")
    
    
   return render_template('new bill.html',user=current_user)




@app.route("/billing/search-bill")
@login_required
def search_bill():   #to be completed
   return render_template('search bill.html',user=current_user) #to be completed


@app.route("/billing/print")
@login_required
def print_bill(bill_no):
    import csv

    rec1=Billing.query.filter_by(bill_no=bill_no).all()
    rec=rec1[0][3]
    data=[["","","","","Store Name","","",""],["","","","","Invoice","","",""],["","Address Line 1","","","","","","Date",*rec[0]],["","Address Line 2","","","","","","Invoice #",bill_no],["","Phone:","Phone Number","","","",], []]
    filename = str(bill_no)+".csv"
    with open(filename, 'w', newline="") as csvfile:
        csvwriter=csv.writer(csvfile) 
        csvwriter.writerows(data)
    record1=Billing.query.filter_by(s_no=s_no).all()
    record=record1[0][2]
    for i in record:
        for j in i:
            rec=Billing.query.filter_by(s_no=j).all()
            for r in rec:
                c_name=r[4]
                mob=r[5]
                data=[["","Bill To: ","","","",],["","Customer Name:",c_name,"","",""],["","Mobile No :",mob,"","",],[],["","S. No.","Product Name","Product Code","Price per Unit","SGST","CGST","Quantity","Total"]]
    with open(filename,'a',newline="") as csvfile:
        csvwriter=csv.writer(csvfile)
        csvwriter.writerows(data)
        t=0
        for i in record:
            for j in i:
                rec=Billing.query.filter_by(s_no=j).all()
                for r in rec:
                    s_no=i[::-2]
                    p_name=r[6]
                    p_code=r[7]
                    ppu=r[8]
                    qty=r[9]
                    sgst=r[10]
                    cgst=r[11]
                    total=r[12]
                    t=t+total
                    data=["",s_no,p_name,p_code,ppu,sgst,cgst,qty,total]
    with open(filename,'a',newline="") as csvfile:
        csvwriter=csv.writer(csvfile)
        csvwriter.writerows(data)
        data=[[],["","Grand Total: ","","","","","","",t,"","","",],[],["","","Thank you for shopping!","","",]]
    with open(filename,'a',newline="") as csvfile:
        csvwriter=csv.writer(csvfile)
        csvwriter.writerows(data)
  return render_template('print bill.html',user=current_user)
@app.route("/products")
@login_required
def products():
   return render_template('products.html',user=current_user)
@app.route("/products/check_product")
@login_required
def check_product():
   return render_template('check_product.html',user=current_user)
@app.route("/products/add-product")
@login_required
def add_product():
   if request.method=='POST':
     product_id=request.form.get('product_id')
     product_name=request.form.get('product_name') 
     price_per_unit=request.form.get('price_per_unit')
     tax_rate=request.form.get('tax_rate')
     gst=tax_rate*price_per_unit
     sgst=gst/2
     stock=request.form.get('stock')
     qty=0
     j=Products(username=current_user,product_id=product_id,product_name=product_name,price_per_unit=price_per_unit,sgst=sgst,cgst=sgst,quantity_sold=qty,stock=stock)
     db.session.add(j)
     db.session.commit()
     n=Taxes(username=current_user,product_id=product_id,gst_per_product=gst,quantity_sold=qty,gst_collected=0,status='Due')
    
   return render_template('add product.html',user=current_user)

@app.route("/products/update-product")
@login_required
def update_product():
   if request.method=='POST':
     product_id=request.form.get('product_id')
     product_name=request.form.get('product_name') 
     price_per_unit=request.form.get('price_per_unit')
     tax_rate=request.form.get('tax_rate')
     gst=tax_rate*price_per_unit
     sgst=gst/2
     stock=request.form.get('stock')
     qty=request.form.get('quantity_sold')
     j=Products(username=current_user,product_id=product_id,product_name=product_name,price_per_unit=price_per_unit,sgst=sgst,cgst=sgst,quantity_sold=qty,stock=stock)
     db.session.add(j)
     db.session.commit()
     upd = db.update(Products)
     val = upd.values({"product_id":"product_id"},{"gst_per_product":"gst_per_product"},{"product_id":"product_id"},{"quantity_sold":"qty"})
     cond = val.where(Products.c.product_id == product_id)
     engine.execute(upd)
                
   return render_template('update product.html',user=current_user)

@app.route("/products/check-stock")
@login_required
def check_stock():#to be completed
  return render_template('check stock.html',user=current_user)

@app.route("/products/check-stock")
@login_required
def check_taxes():#to be completed
  return render_template('check taxes.html',user=current_user)

@app.route("/taxes")
@login_required
def taxes():
  return render_template('taxes.html',user=current_user)

@app.route("/taxes/check-taxes")
@login_required
def check_taxes():#to be completed
  return render_template('check taxes.html',user=current_user)

@app.route("/taxes/pay-taxes")
@login_required
def pay_taxes():
  if request.method=='POST':
    total_gst=0
    myresult=User.query.filter_by(username=username).all()
    for a in myresult:
        for x in a:
            total_gst=total_gst+x
            upd = db.update(Taxes)
            val = upd.values({"Status":"Due"})
            cond = val.where(Taxes.c.product_id == product_code)
            engine.execute(upd)
            
            

  return render_template('pay taxes.html',user=current_user)


app.run(host='localhost',port=8080,debug=True)

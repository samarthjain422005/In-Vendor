from flask import Flask,request,render_template

app=Flask(__name__)

database={'admin':"xyz",'sukjin':'9.9','sammyboy':'123456789'}

@app.route('/')
def landingpage():
    return render_template('index.html')

@app.route('/login',methods=['POST','GET'])
def login():
    username=request.form['username']
    password=request.form['password']
    if username not in database:
        return render_template('login.html',info='Invalid User')
    else:
        if database[username]!=password:
            return render_template('login.html',info='Incorrect Password')
        else:
            return render_template('home.html',username=username)

if __name__=='__main__':
    app.run()
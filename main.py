#for the app
from flask import Flask, render_template, request, send_file 
import os
import tempfile
import datetime

#for logging
import traceback
import sys 

#utils for generating (scraping) the Hanko
import requests
from bs4 import BeautifulSoup
import base64

#utils for the digital signature (keys / certificates)
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import pkcs12

#utils for pdf signing / manipulation
from endesive.pdf import cms
from PIL import Image, ImageOps

app = Flask('app')

def getHankoImage(text, shape, style, font, origin=None, rotation=0):
  site = "https://www.hankogenerator.com"
  url = site + "/getimage/"

  s = requests.Session() 
  r = s.get(site).text
  soup = BeautifulSoup(r, 'html.parser')

  token = soup.find(attrs={"name": "csrfmiddlewaretoken"})['value']

  headers = {"referer": "https://www.hankogenerator.com/", "content-type":"application/x-www-form-urlencoded"}

  #input parameters: text <kanji/hiragana/katakana chars>, shape <round/square>, style & font => check website for types
  
  data = {"Text":text,"size":"0.83","shape":shape,"style":style,"font": font, "csrfmiddlewaretoken":token}

  p = s.post(url, data=data, headers=headers)

  if origin != None: 
    if p.status_code == 200: 
      return p.text
    else: 
      return "Error: " + p.text
  else: 
    if p.status_code == 200: 
      _fq, imagepath = tempfile.mkstemp(".png")
      imgdata = base64.b64decode(p.text)
      with open(imagepath, 'wb') as f:
          f.write(imgdata)
      img = Image.open(imagepath).rotate(rotation+180) #endesive rotation needs compensation
      if shape == "square":
        side = img.size[0]
        ImageOps.expand(img, border=side//20, fill="red").save(imagepath) #borders for square seals need enhancement
      else:
        img.save(imagepath)
      img.close()
      return [imagepath, _fq]
    else:
      app.logger.error("Issue with website scraping: " + p.text)
      return ["Message: Dependency Error [Check Console]", p.text]

def signPDF(docdata, page, email, name, shape, style, font, region, x1,y1,x2,y2, rotation):
  try:
    res = getHankoImage(name, shape, style, font, rotation=rotation)
    if "Message" in res[0]: 
      return res
    else: 
      _fr, fname = tempfile.mkstemp(".pdf")

    one_day = datetime.timedelta(1, 0, 0)
    private_key = rsa.generate_private_key(
      public_exponent=65537,
      key_size=2048,
      backend=default_backend()
    )
    public_key = private_key.public_key()
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name([
      x509.NameAttribute(NameOID.COMMON_NAME, name),
    ]))
    builder = builder.issuer_name(x509.Name([
      x509.NameAttribute(NameOID.COMMON_NAME, u'inkantan'),
    ]))
    builder = builder.not_valid_before(datetime.datetime.today() - one_day)
    builder = builder.not_valid_after(datetime.datetime.today() + (one_day * 365))
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(public_key)
    builder = builder.add_extension(
      x509.SubjectAlternativeName(
          [x509.DNSName("@inkantan")]
      ),
      critical=False
    )
    builder = builder.add_extension(
      x509.BasicConstraints(ca=False, path_length=None), critical=True,
    )
    certificate = builder.sign(
      private_key=private_key, algorithm=hashes.SHA256(),
      backend=default_backend()
    )
    p12 = pkcs12.serialize_key_and_certificates(b'test', private_key, certificate, [certificate], serialization.BestAvailableEncryption(b'1234'))
    y = pkcs12.load_key_and_certificates(p12, b'1234', default_backend())

    date = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
    date = date.strftime("D:%Y%m%d%H%M%S+00'00'")
    tspurl = "http://public-qlts.certum.pl/qts-17"
    dct = {
        "aligned": 0,
        "sigflags": 1,
        "sigflagsft": 132,
        "sigpage": int(page)-1,
        "sigbutton": True,
        "sigfield": "Signature1",
        "sigandcertify": True,
        "signaturebox": (max(x1,x2),(max(y1,y2)),min(x1,x2),min(y1,y2)), 
        "signature_img": res[0],
        "contact": email,
        "location": region,
        "signingdate": date,
        "reason": "To execute/formalize/affirm the contract", #目的：契約書に署名する 
        "password": "1234",
    }

    with open(fname, 'wb') as fx: 
      fx.write(docdata)

    datau = open(fname, "rb").read()
    try:
      datas = cms.sign(datau, dct, y[0], y[1], y[2], "sha256", timestampurl=tspurl)
    except Exception as x:
      return errHandler(x, [res[0], fname], [res[1], _fr])
      
    with open(fname, "wb") as fp:
        fp.write(datau)
        fp.write(datas)
    os.close(res[1])
    os.remove(res[0])
    os.close(_fr)
    return fname
  except Exception as e:
    return errHandler(e, [res[0], fname], [res[1], _fr])

def errHandler(e, path, descriptor):
  #clean up memory
  for i in descriptor:
    os.close(i)
  for j in path:
    os.remove(j)
  #log
  app.logger.error(e)
  app.logger.info(traceback.format_exc())
  exc_type, exc_value, exc_traceback = sys.exc_info()
  return ["Error Message: " + str(exc_value), str(traceback.format_exc())]

@app.route('/')
def home():
  return render_template("index.html")

@app.route('/test', methods=["POST"])
def test():
  content = request.json
  return getHankoImage(content['name'], content['shape'], content['style'], content['font'], "self")

@app.route('/sign', methods=["POST"])
def sign():
  if request.method == "POST":
    
    name = request.form['name']
    email = request.form['email']
    y_compensator = round(float(request.form['ycom']))
    x1 = int(request.form['x1'])
    y1 = y_compensator - int(request.form['y1'])
    x2 = int(request.form['x2'])
    y2 = y_compensator - int(request.form['y2'])
    shape = request.form['shape']
    style = request.form['style']
    font = request.form['font']
    region = request.form['region']
    page = request.form['page']
    if request.form['rotation'] in ["", None] or request.form['shape'] != "round": 
      rotation = 0
    else:
      rotation = int(request.form['rotation'])
    data = request.files.get('file', None)
    
    if data.filename.rsplit('.', 1)[1].lower() == "pdf":
      api_response = signPDF(data.read(), page, email, name, shape, style, font, region, x1, y1, x2, y2, rotation)
      if type(api_response) == list:
        return render_template("error.html", e=api_response[0], c=api_response[1])
      elif api_response == None:
        return render_template("error.html", e="Nonetype: Script Error", c="Check server logs")
      else:
        r = send_file(api_response, mimetype="application/pdf", as_attachment=False)
        os.remove(api_response)
        return r
    else: 
      return render_template("error.html", e="Wrong File Type, not a PDF", c="PDF File Error")

app.run(host='0.0.0.0', port=8080, debug=True)

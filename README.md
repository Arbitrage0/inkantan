<p align="center"><a href="https://creativecommons.org/share-your-work/public-domain/cc0/"><img src="https://img.shields.io/badge/License-CC--0-green.svg"></a>
  <a href="https://www.twitter.com/quantequivocal">
    <img src="https://img.shields.io/badge/Contact-@quantequivocal-blue.svg" />
  </a>
<a href="https://www.blockchain.com/btc/payment_request?address=1CD3LVXQvysJ1eP16DinFXEfuctmnjizYh&amount=0.0005"><img src="https://img.shields.io/badge/BTC-donate-orange.svg" /></a>
</p>

# <u>in</u><span style="text-decoration: overline"><u>kan</u>tan</span>: A digital <i>mitome-in</i> web app

<img alt="seal image" src="https://upload.wikimedia.org/wikipedia/commons/4/47/Guanyin_song1.png" width="200" style="display: block;margin-left: auto;margin-right: auto;"><br/>

## Background Introduction

Inkantan is a simple and lite Flask web app that allows users to upload PDFs and get them digitally signed with a custom-generated hanko (はんこ: seal) aesthetic element. 

> The name is a silly portmanteau of the Japanese words <i>"inkan"</i> (印鑑) which refers to the mark or impression made by affixing a seal, and the word <i>"kantan"</i> (簡単) meaning simple. Therefore, simple sealing.

The user only needs to fill out a short form, and upload the file before being prompted to drag and select the area on the signature page where the seal needs to be applied. Neither the document nor any of the personal information provided will be stored on the server, and the result PDF is instantly generated. 

The resultant PDF document should contain the visual seal element on the page and embedded digital signature data that can be inspected by using software like Adobe® Reader, which ensures document integrity, validity and tamper-detectability. 

> <i>"Mitome-in"</i> (認印) is one of the three common types of seal that normally tends to be unregistered, off-the-shelf for ¥200, and is used for acknowledgement, uncomplicated or routine contracts, and low-to-medium-value dealings. They are used both in personal and corporate contexts. 
>
>This service creates self-signed root certificates and doesn't rely on CAs because, in line with the above, that would be disproportionate relative to the purpose. That does not mean, however, that such signatures are not capable of being legally recognized or binding (e.g. <a href="http://www.japaneselawtranslation.go.jp/law/detail_main?re=&vm=02&id=109">Article 2(1) of The Act on Electronic Signatures and Certification Business (Act No. 102 of 31 May 2000)</a> in Japan). 

Given how important a cultural role the seal plays in Japanese (and broadly East Asian) societies, and given the present need for caution in physical interaction, I thought this solution would offer a modern, progressive, and free-to-use compromise. 

<strike>I hope this may be slightly better than totally useless, and that someone may gain some value out of it.</strike>

Try it live <a href="https://35.231.16.38:8080/">here</a>.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

The PDF-manipulation python library that the project makes use of (i.e. ```endesive```) requires the following package to be installed:

```
apt install swig 
#or use the equivalent homebrew command for macOS
```

### Installing

It is recommended to install all the dependencies and project files in a virtual environment so first: 

```
python3 -m venv env
source env/bin/activate
```

Then clone the repository and ```cd``` into the environment and run:

```
pip3 install -r requirements.txt
```

## Deployment

Once installation is complete, run the following command to start the Flask server on localhost. By default, it will run on port 8080 and in debug mode. 

```
python3 main.py
```

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
* [Cryptography](https://cryptography.io/en/latest/) - For creating digital signatures, keys and certificates
* [Endesive](https://github.com/m32/endesive) - For digitally signing PDFs
* [Pillow](https://pillow.readthedocs.io/en/stable/) - For Image data manipulation
* [PDF.js](https://mozilla.github.io/pdf.js/) - For web PDF rendering and interaction
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - For HTML web scraping
* [Requests](https://requests.readthedocs.io/en/master/) - For HTTP web requests and session management

## Known Issues

* Cannot be used for PDFs with existing structural malformations/anomalies
* <strike>PDFs with existing signatures will have those sigs invalidated due to manipulation of PDF data (a solution is currently being worked on because ```PIL``` with ```endesive``` as an alternative is quite temperamental).</strike> Issue has been resolved. 
* Hanko Generator has inconsistent treatment of CJK characters, which may not show up on the final seals (or possibly lead to 500 errors). I suspect this mainly pertains to simplified Chinese characters, but it is a [fool's errand to try to validate CJK name input by way of Regex](https://salesforce.stackexchange.com/questions/127565/regular-expression-to-find-chinese-characters). Use with caution, I guess? 

## Authors

* **Izaan Khan** - *Initial work* - [Arbitrage0](https://github.com/Arbitrage0)

## Contributing
If something can be improved, it should be; and you should submit a PR for it! The contribution philosophy (for now, at least) is methodological anarchism. Anything goes...

## License

This project is free to be used, remixed, copied, and shared, as it is open source and in the public domain, with none of the creator's © rights reserved, **where applicable** - see [CC0](https://creativecommons.org/share-your-work/public-domain/cc0/) for details. Attribution would be nice. 

## Acknowledgments

* Major Hat tip to [HankoGenerator](https://www.hankogenerator.com/), the web service that creates the signature aesthetics, without which this project would be impossible. 

# Asylum Decision Database -- Human Rights First
An application to assist immigration advocates in winning asylum cases. 

## Description

Built for the Human Rights First 501(c)3, our application uses optical character recognition to scan input court decisions for such values as the name of the presiding judge, the decision, and the asylum seeker's country of origin, and inserts these values into a database. The hope is that advocates for asylum seekers can use these data to better tailor their arguments before a particular judge and maximize their client's chances of receiving asylum.

## Tools

* [Pytesseract](https://github.com/madmaze/pytesseract)
* [FastAPI](https://github.com/tiangolo/fastapi)
* [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/)

## Installation

After cloning the repository, run:
```
pipenv shell
cd app
python main.py
```
Then open localhost:8000 in your browser. The application should be running. 

## Contributors

[Steven Lee](https://github.com/StevenBryceLee)

[Tristan Brown](https://github.com/Tristan-Brown1096)

[Liam Cloud Hogan](https://github.com/liam-cloud-hogan)

[Edwina Palmer](https://github.com/edwinapalmer)



## License

This project is licensed under the terms of the MIT license.


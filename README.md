# Amazon Comprehend connector for transcriptions created from Vonage API connectors and messages from Vonage API applications

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/nexmo-se/aws-comprehend)

This Vonage API's Amazon Comprehend connector allows transcriptions created from your deployed Vonage API connectors and messages from your Vonage API applications to be sentiment analyzed by AWS Comprehend. Multiple languages are supported.

## Amazon Comprehend connector

In order to get started, you need to have an [AWS account](http://aws.amazon.com), retrieve your AWS key and secret, and take note of your AWS services default region.

To find your Access Key and Secret Access Key:

- Log in to your [AWS Management Console](http://aws.amazon.com/console).
- Click on your user name at the top right of the page.
- Click on the Security Credentials link from the drop-down menu.
- Find the Access Credentials section, and copy the latest Access Key ID.
- Click on the Show link in the same row, and copy the Secret Access Key.

## How to use this connector

Your Vonage API application uses HTTP POST to the connector address with the follwing requirements:
- The text to be sentiment analyzed is sent as a _**"text"**_ element in a JSON formatted payload in the HTTP POST body, not as a query parameter! Thus your application must set the header "Content-Type:application/json",
- Must include at least the following query parameters:
	- _**webhook_url**_ (e.g. https://my_server.my_company.com:32000/sentiment_score) where the sentiment scores will be posted by the connector to your Vonage API application,
	- _**language**_ (e.g. en), which defines the transcription language as listed [here](https://docs.aws.amazon.com/comprehend/latest/dg/supported-languages.html),
- Your application may send/use any additional query parameter names and values for your application logic needs, except it **may not** use/send the following reserved query parameter names:
	- _**sentiment**_,
	- _**text**_,
	- _**service**_.

A few seconds later, the connector posts back to your Vonage API application webhook_url a JSON formatted payload (in the body of an HTTP POST):</br>
	- the _**"sentiment"**_, i.e. sentiment results,</br>
	- the _**"text"**_,</br>
	- the name of the _**"service"**_, which is "AWS Comprehend" in this case,</br> 
	- and all other values sent as query parameters of the original request to the connector, e.g. _**"webhook_url"**_, _**"language"**_, and any additional query parameters that have been sent in the original HTTP POST.</br>

## Running Comprehend connector

You may select one of the following 4 types of deployments.

### Docker deployment

Copy the `.env.example` file over to a new file called `.env`:
```bash
cp .env.example .env
```

Edit `.env` file,<br/>
set the 3 first parameters with their respective values retrieved from your AWS account,<br/>
set the `PORT` value where websockets connections will be established.

Launch the Transcribe & Comprehend connector as a Docker instance:

```bash
docker-compose up
```
Your Docker container's public hostname and port will be used by your Vonage Voice API application as the address to where to submit the transcription request `https://<docker_host_name>:<proxy_port>/sentiment`, e.g. `https://myserver.mydomain.com:40000/sentiment`

### Local deployment

To run your own instance locally you'll need an up-to-date version of Python 3.8 (we tested with version 3.8.5).

Copy the `.env.example` file over to a new file called `.env`:

```bash
cp .env.example .env
```

Edit `.env` file,<br/>
set the 3 first parameters with their respective values retrieved from your AWS account,<br/>
set the `PORT` value where websockets connections will be established.

Install dependencies once:
```bash
pip install --upgrade -r requirements.txt
```

Launch the connector service:
```bash
python server.py
```

Your server's public hostname and port will be used by your Vonage Voice API application as the address to where to submit the transcription request `https://<serverhostname>:<port>/transcribe`, e.g. `https://abcdef123456.ngrok.io/sentiment`

### Command Line Heroku deployment

If you do not yet have a local git repository, create one:</br>
```bash
git init
git add .
git commit -am "initial"
```

Deploy this connector application to Heroku from the command line using the Heroku CLI:

```bash
heroku create myappname
```

On your Heroku dashboard where your connector application page is shown, click on `Settings` button,
add the following `Config Vars` and set them with their respective values retrieved from your AWS account:</br>
AWS_ACCESS_KEY_ID</br>
AWS_SECRET_ACCESS_KEY</br>
AWS_DEFAULT_REGION</br>

```bash
git push heroku master
```

On your Heroku dashboard where your connector application page is shown, click on `Open App` button, that URL will be the one to be used by your Vonage Voice API application as where to submit the HTTP POST, e.g. `https://myappname.herokuapp.com/sentiment`.

### 1-click Heroku deployment

Click the 'Deploy to Heroku' button at the top of this page, and follow the instructions to enter your Heroku application name and the 3 AWS parameter respective values retrieved from your AWS account.

Once deployed, on the Heroku dashboard where your connector application page is shown, click on `Open App` button, that URL will be the one to be used by your Vonage Voice API application as where to submit the HTTP POST, e.g. `https://myappname.herokuapp.com/sentiment`.

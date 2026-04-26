
<h2>Start</h2>
`
gunicorn -w 1 --threads 4 -b 127.0.0.1:5001 "app:create_app()"
`

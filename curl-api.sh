curl --location --request POST \
'https://send.api.mailtrap.io/api/send' \
--header 'Authorization: Bearer '"$MAILTRAP_API_PASSWORD" \
--header 'Content-Type: application/json' \
--data-raw '{"from":{"email":"mailtrap@nbrinton.dev","name":"Mailtrap Test"},"to":[{"email":"nab.natethegreat@gmail.com"}],"subject":"You are awesome!","text":"Congrats for sending test email with Mailtrap!","category":"Integration Test"}'

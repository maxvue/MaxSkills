<?php

/*
|--------------------------------------------------------------------------
| Trecho para config/services.php
|--------------------------------------------------------------------------
|
| Adicione estas chaves ao array retornado em config/services.php.
| Os valores ficam no .env (NUNCA commitar credenciais).
|
| .env de exemplo:
|
|   GOOGLE_CLIENT_ID=
|   GOOGLE_CLIENT_SECRET=
|   GOOGLE_REDIRECT_URI="${APP_URL}/auth/google/callback"
|
|   FACEBOOK_CLIENT_ID=
|   FACEBOOK_CLIENT_SECRET=
|   FACEBOOK_REDIRECT_URI="${APP_URL}/auth/facebook/callback"
|
*/

return [

    // ... outros serviços (mailgun, postmark, ses, etc.) ...

    'google' => [
        'client_id'     => env('GOOGLE_CLIENT_ID'),
        'client_secret' => env('GOOGLE_CLIENT_SECRET'),
        'redirect'      => env('GOOGLE_REDIRECT_URI'),
    ],

    'facebook' => [
        'client_id'     => env('FACEBOOK_CLIENT_ID'),
        'client_secret' => env('FACEBOOK_CLIENT_SECRET'),
        'redirect'      => env('FACEBOOK_REDIRECT_URI'),
    ],

];

<?php

// Trecho de config/services.php — credenciais OAuth do Google e Facebook.
// As chaves devem bater com config("services.$provider.client_id") usado no
// SocialiteController::providers(). Provedor sem client_id/client_secret é
// automaticamente omitido da lista exposta ao frontend.

return [

    // ... demais serviços ...

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

/*
 * .env correspondente:
 *
 * GOOGLE_CLIENT_ID=
 * GOOGLE_CLIENT_SECRET=
 * GOOGLE_REDIRECT_URI="${APP_URL}/auth/google/callback"
 *
 * FACEBOOK_CLIENT_ID=
 * FACEBOOK_CLIENT_SECRET=
 * FACEBOOK_REDIRECT_URI="${APP_URL}/auth/facebook/callback"
 *
 * O redirect URI deve apontar para a rota nomeada social.callback
 * (/auth/{provider}/callback) e estar cadastrado no console do provedor.
 */

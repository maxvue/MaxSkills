<?php

// Trecho de routes/auth.php — apenas as rotas de login social.
// Os NOMES são o contrato consumido pelo frontend via Ziggy (route('social.redirect', ...)).
// Mantenha-os estáveis: renomear quebra o Ziggy silenciosamente.

use App\Http\Controllers\Auth\SocialiteController;
use Illuminate\Support\Facades\Route;

Route::middleware('guest')->group(function () {
    // GET /auth/providers       → lista de provedores habilitados (monta os botões)
    Route::get('auth/providers', [SocialiteController::class, 'providers'])
        ->name('social.providers');

    // GET /auth/{provider}/redirect → inicia o OAuth (redirect do navegador)
    Route::get('auth/{provider}/redirect', [SocialiteController::class, 'redirect'])
        ->name('social.redirect');

    // GET /auth/{provider}/callback → provedor retorna aqui; cria sessão (e usuário, se 1º acesso)
    Route::get('auth/{provider}/callback', [SocialiteController::class, 'callback'])
        ->name('social.callback');
});

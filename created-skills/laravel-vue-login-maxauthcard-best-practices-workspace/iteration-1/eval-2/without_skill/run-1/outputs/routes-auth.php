<?php

/*
|--------------------------------------------------------------------------
| Trecho para routes/auth.php
|--------------------------------------------------------------------------
|
| Rotas de login social. As rotas são NOMEADAS para que o Ziggy as exponha
| ao frontend Vue. No Vue use:
|
|   route('auth.social.redirect', { provider: 'google' })
|   route('auth.social.redirect', { provider: 'facebook' })
|
| O parâmetro {provider} é restringido via whereIn para que o Ziggy/router
| só aceite os provedores suportados.
|
*/

use App\Http\Controllers\Auth\SocialiteController;
use Illuminate\Support\Facades\Route;

Route::middleware('guest')->group(function () {
    // Inicia o fluxo OAuth (redireciona para Google/Facebook).
    Route::get('auth/{provider}/redirect', [SocialiteController::class, 'redirect'])
        ->whereIn('provider', ['google', 'facebook'])
        ->name('auth.social.redirect');

    // Recebe o callback, cria/loga o usuário na sessão.
    Route::get('auth/{provider}/callback', [SocialiteController::class, 'callback'])
        ->whereIn('provider', ['google', 'facebook'])
        ->name('auth.social.callback');
});
